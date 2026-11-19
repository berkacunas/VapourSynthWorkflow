import subprocess
from pathlib import Path
from tarfile import ENCODING
import threading
from typing import Tuple, List

from vapoursynth_workflow.hardware_monitor import monitor as hardware_monitor
from vapoursynth_workflow.video_utilities import parse_crop_values, ffmpeg_cropdetect

g_encoding_step: int = 1


def encode_audio(sourcefile: Path, qaac_path: Path, output_file: Path):
    
    global g_encoding_step
    print(f"\n[{g_encoding_step}/3] Extracting audio and encoding with AAC...")
    g_encoding_step += 1

    audio_cmd = f'eac3to "{sourcefile}" 2: stdout.wav -down6 | "{qaac_path}" --tvbr 100 - -o "{output_file}"'
    subprocess.run(audio_cmd, shell=True, check=True)
    print(f"Audio encoding complete: {output_file}")

def get_crop_values(sourcefile: Path, start_time: str = "00:00:00.000", frames: int = 10) -> Tuple[int, int, int, int]:

    w, h, x, y = parse_crop_values(ffmpeg_cropdetect(sourcefile.as_posix(), start_time, frames))
    return w, h, x, y

def convert_cropping_values(w, h, x, y, source_width, source_height):
    
    left = x
    top = y
    right = source_width - w - x
    bottom = source_height - h - y
    
    return left, top, right, bottom
    
def encode_video_with_nvencc(nvencc_path: Path, vapoursynth_file: Path, sourcefile: Path, output_file: Path, target_width: int = 1920, target_height: int = 1080, 
                             left: int = 0, top: int = 0, right: int = 0, bottom: int = 0, start_frame: int = 0, end_frame: int = 0) -> bool:
    
    global g_encoding_step
    print(f"\n[{g_encoding_step}/3] NVEncC hardware encoding via VapourSynth is starting...")
    g_encoding_step += 1
    
    vspipe_cmd = ["vspipe", "-c", "y4m"]
    if not (start_frame <= 0 and end_frame <= 0):
        vspipe_cmd.extend(["-a", f"start_frame={start_frame}"])
        if end_frame > 0:
            vspipe_cmd.extend(["-a", f"end_frame={end_frame}"])
        
    vspipe_cmd.extend(["--arg", f"sourcefile={str(sourcefile.as_posix())}"])
    vspipe_cmd.extend([str(vapoursynth_file.as_posix()), "-"])
    
    nvencc_pipe_cmd = [ str(nvencc_path), "--y4m", "-i", "-", 
                    "-c", "hevc", 
                    "--vbr", "0", 
                    "--vbr-quality", "22", 
                    "--max-bitrate", "35000", 
                    "--multipass", "2pass-full",
                    "--crop", f"{left},{top},{right},{bottom}",
                    "--output-res", f"{target_width}x{target_height}",
                    "--lookahead", "32", 
                    "--aq", "--aq-temporal", 
                    "--output-depth", "10", 
                    "-o", str(output_file)
                    ]

    p_vspipe = subprocess.Popen(vspipe_cmd, stdout=subprocess.PIPE, text=False)
    
    # Lock the vspipe process to only cores 0 and 1 (CPU 0 and CPU 1)
    # Causing thermal hotspots. Don't add.
    # vspipe_process = psutil.Process(p_vspipe.pid)
    # vspipe_process.cpu_affinity([0, 2])
    
    p_nvencc = subprocess.Popen(nvencc_pipe_cmd, stdin=p_vspipe.stdout, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    stop_event = threading.Event()
    monitor_thread = threading.Thread(target=hardware_monitor, args=(p_vspipe, p_nvencc, stop_event), daemon=True)
    monitor_thread.start()

    try:
        if p_vspipe.stdout is not None:
            p_vspipe.stdout.close()
                    
        if p_nvencc.stdout is not None:
            for line in p_nvencc.stdout:
                print(line, end="")

        p_nvencc.wait()
        p_vspipe.wait()

        if p_nvencc.returncode != 0:
            return False
            
        print(f"Video encoding complete: {output_file}")
        return True
    
    finally:
        stop_event.set()

def merge(encoded_video_file: Path, encoded_audio_file: Path, final_muxed_file: Path):
    
    global g_encoding_step
    print(f"\n[{g_encoding_step}/3] Audio and video are being merged into an MKV file...")
    g_encoding_step += 1

    mux_cmd = [ "mkvmerge", "-o", str(final_muxed_file), str(encoded_video_file), str(encoded_audio_file) ]
    subprocess.run(mux_cmd, check=True)

    print(f"\n[DONE] The process is complete. Final file: {final_muxed_file}")

def cleanup(encoded_video_file: Path, encoded_audio_file: Path):
    # (Optional) - Cleanup: Deletes intermediate files.
    encoded_video_file.unlink()
    encoded_audio_file.unlink()

def merge_parts(final_output: Path, parts: List[str]):
    
    merge_cmd = ["mkvmerge", "-o", str(final_output), str(parts[0])]
    for part in parts[1:]:
        merge_cmd.extend(["+", str(part)])
        
    subprocess.run(merge_cmd, stdout=subprocess.PIPE, text=True, check=True)
