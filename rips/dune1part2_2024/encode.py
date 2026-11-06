import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, List, Any

from vapoursynth_workflow.video_utilities import parse_crop_values, ffmpeg_stderr

def process_audio(sourcefile: Path, qaac_path: Path, output_file: Path):
    
    print("\n[1/3] Extracting audio and encoding with AAC...")

    audio_cmd = f'eac3to "{sourcefile}" 2: stdout.wav -down6 | "{qaac_path}" --tvbr 127 - -o "{output_file}"'
    subprocess.run(audio_cmd, shell=True, check=True)
    print(f"Audio encoding complete: {output_file}")


def probe_file(sourcefile: Path) -> Dict[str, Any]:
    
    probe_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_frames,tags", "-of", "json", sourcefile]
    probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    video_info = json.loads(probe_result.stdout)["streams"][0]
    
    return video_info

def probe_vapoursynth(vapoursynth_file: Path) -> Dict[str, Any]:
    
    probe_cmd = ["vspipe", "--info", vapoursynth_file, "-"]
    probe_result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, text=True, check=True)
    stdout = probe_result.stdout
    
    videoinfo: Dict[str, Any] = {}
    for line in stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            videoinfo[key.strip()] = value.strip()
        
    return videoinfo

def get_total_frames(videoinfo: Dict[str, Any]) -> int:
    
    total_frames_str = videoinfo.get("nb_frames") or videoinfo.get("tags", {}).get("NUMBER_OF_FRAMES", "0")
    
    return int(total_frames_str)

def get_resolution(video_info: Dict[str, Any]) -> Tuple[int, int]:
    
    w = video_info["width"]
    h = video_info["height"]
    
    return w, h

def get_cropping_values(sourcefile: Path) -> Tuple[int, int, int, int]:

    w, h, x, y = parse_crop_values(ffmpeg_stderr(str(sourcefile)))
    return w, h, x, y

def convert_cropping_values(w, h, x, y, source_width, source_height):
    
    left = x
    top = y
    right = source_width - w - x
    bottom = source_height - h - y
    
    return left, top, right, bottom
    

def process_video_with_nvencc(nvencc_path: Path, vapoursynth_file: Path, sourcefile: Path, output_file: Path, target_width: int = 1920, target_height: int = 1080, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0, start_frame: int = 0, end_frame: int = 0):
    
    print("\n[2/3] NVEncC hardware encoding via VapourSynth is starting...")
    
    vspipe_cmd = ["vspipe", "-c", "y4m"]
    if not (start_frame <= 0 and end_frame <= 0):
        vspipe_cmd.extend(["-a", f"start_frame={start_frame}"])
        if end_frame > 0:
            vspipe_cmd.extend(["-a", f"end_frame={end_frame}"])
        
    vspipe_cmd.extend(["--arg", f"sourcefile={str(sourcefile)}"])
    vspipe_cmd.extend([str(vapoursynth_file), "-"])
    
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

    p_vspipe = subprocess.Popen(vspipe_cmd, stdout=subprocess.PIPE)
    p_nvencc = subprocess.Popen(nvencc_pipe_cmd, stdin=p_vspipe.stdout)

    if p_vspipe.stdout is not None:
        p_vspipe.stdout.close()

    p_nvencc.wait()
    p_vspipe.wait()

    print(f"Video encoding complete: {output_file}")

def merge(encoded_video_file: Path, encoded_audio_file: Path, final_muxed_file: Path):
    
    print("\n[3/3] Audio and video are being merged into an MKV file...")

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

def main():
    
    root_dir = Path("./rips/dune1part2_2024").resolve()
    sourcefile = Path(r"D:\BT\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv")
    samplefile = Path(r"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024\samples\sample_file.mkv")
    
    vapoursynth_file = root_dir / "vapoursynth.vpy"
    nvencc_path = Path(r"E:\HOME\Documents\Encoding\SOFTWARE\NVEncC\NVEncC_9.12_x64\NVEncC64.exe")
    qaac_path = Path(r"E:\HOME\Documents\Encoding\SOFTWARE\Apple CoreAudio\iTunes-makeportable\QTfiles64\qaac64.exe")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = root_dir / f"samples/encoded_video_{timestamp}.hevc"
    encoded_audio_file = root_dir / f"samples/encoded_audio_{timestamp}.m4a"
    final_muxed_file = root_dir / f"samples/Dune_Final_{timestamp}.mkv"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # TEST
    sourcefile = samplefile
    
    videoinfo = probe_file(sourcefile)
    source_width, source_height = get_resolution(videoinfo)
    
    vsinfo = probe_vapoursynth(vapoursynth_file)
    total_frames = int(vsinfo["Frames"])
    
    w, h, x, y = get_cropping_values(sourcefile)
    
    left, top, right, bottom = convert_cropping_values(w, h, x, y, source_width, source_height)
    
    target_width = 1920
    target_height = ((h * target_width) // w) // 2 * 2
    
    encoding_parts = 10
    
    if encoding_parts > 0:
        part_names = []
        frames_per_loop = total_frames // encoding_parts
        
        for i, start_frame in enumerate(range(0, total_frames, frames_per_loop)):
            part_file = root_dir / f"samples/encoded_video_part{i}.hevc"
            end_frame = start_frame + frames_per_loop - 1 
            process_video_with_nvencc(nvencc_path, vapoursynth_file, sourcefile, part_file, target_width, target_height, left, top, right, bottom, start_frame, end_frame)
            part_names.append(part_file)
            
        merge_parts(output_file, part_names)
    else:
        process_video_with_nvencc(nvencc_path, vapoursynth_file, sourcefile, output_file, target_width, target_height, left, top, right, bottom)
    
    process_audio(sourcefile, qaac_path, encoded_audio_file)
    merge(output_file, encoded_audio_file, final_muxed_file)
    
if __name__ == "__main__":
    main()
