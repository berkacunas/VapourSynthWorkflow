from datetime import datetime
from pathlib import Path

from vapoursynth_workflow.encoding import encode_video_with_nvencc, get_crop_values, convert_cropping_values, merge, merge_parts, encode_audio
from vapoursynth_workflow.crop import VapourSynthCrop
from vapoursynth_workflow.probe import FfFileProbe, VapourSynthProbe
from vapoursynth_workflow.video_utilities import create_fast_sample


def main():
    
    root_dir = Path(r"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024").resolve()
    sourcefile = Path(r"D:\BT\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv")
    samplefile = Path(r"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024\samples\sample_file2.mkv")
    
    vapoursynth_file = root_dir / "vapoursynth.vpy"
    nvencc_path = Path(r"E:\HOME\Documents\Encoding\SOFTWARE\NVEncC\NVEncC_9.12_x64\NVEncC64.exe")
    qaac_path = Path(r"E:\HOME\Documents\Encoding\SOFTWARE\Apple CoreAudio\iTunes-makeportable\QTfiles64\qaac64.exe")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    encoded_audio_file = root_dir / f"samples/encoded_audio_{timestamp}.m4a"
    final_muxed_file = root_dir / f"samples/Dune_Final_{timestamp}.mkv"
    state_file = root_dir / "completed_parts.txt"
    output_file = root_dir / f"samples/encoded_video_{timestamp}.hevc"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # create_fast_sample(str(sourcefile), str(samplefile), num_frames=150)
    
    
    completed_parts = []
    if state_file.exists():
        with open(state_file, "r") as f:
            completed_parts = [line.strip() for line in f]
            
    # TEST
    sourcefile = samplefile
    
    ffvideoinfo = FfFileProbe.probe_file(sourcefile)
    source_width, source_height = FfFileProbe.get_resolution(ffvideoinfo)
    
    vpinfo = VapourSynthProbe.probe(sourcefile, vapoursynth_file)
    total_frames = VapourSynthProbe.get_total_frames(vpinfo)
    fps = VapourSynthProbe.get_fps(vpinfo)
    
    w, h, x, y = get_crop_values(sourcefile, start_time="00:00:00", frames=100)
    
    crop_values_dict = VapourSynthCrop.get_crop_values(sourcefile, 100)
    
    left, top, right, bottom = convert_cropping_values(w, h, x, y, source_width, source_height)
    
    target_width = 1920
    target_height = ((h * target_width) // w) // 2 * 2
    
    encoding_parts = 10
    
    if encoding_parts > 0:
        
        part_names = []
        frames_per_loop = total_frames // encoding_parts
        
        success = True
        for i, start_frame in enumerate(range(0, total_frames, frames_per_loop)):
            part_file = root_dir / f"samples/encoded_video_part{i}.hevc"
            part_names.append(part_file)
            if part_file.as_posix() in completed_parts:
                print(f"[INFO] {part_file} already encoded, skipping next...")
                continue
            
            end_frame = start_frame + frames_per_loop - 1 
            success = encode_video_with_nvencc(nvencc_path, vapoursynth_file, sourcefile, part_file, target_width, target_height, left, top, right, bottom, start_frame, end_frame)
            if success:
                with open(state_file, "a") as f:
                    f.write(f"{part_file.as_posix()}\n")
            else:
                break
    else:
        success = encode_video_with_nvencc(nvencc_path, vapoursynth_file, sourcefile, output_file, target_width, target_height, left, top, right, bottom)
    
    if success:
        if encoding_parts > 0:
            merge_parts(output_file, part_names)
            
        encode_audio(sourcefile, qaac_path, encoded_audio_file)
        merge(output_file, encoded_audio_file, final_muxed_file)
    else:
        print("[FATAL] The operation was interrupted. Other items in the queue are being cancelled.")
    
if __name__ == "__main__":
    main()