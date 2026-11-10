from pathlib import Path
from collections import Counter
import subprocess

import vapoursynth as vs
core = vs.core

def get_fps(source: str) -> float:
    
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", source]
    fps_str = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()

    num, den = fps_str.split('/')
    fps = float(num) / float(den)
    
    return fps

def create_fast_sample(source: str, samplefile: str, start_time: str | int = "00:20:00", duration: str | None = None, num_frames: int | None = None) -> str:
    
    samplefile_path = Path(samplefile)
    sample_dir = samplefile_path.resolve().parent
    
    # if not samplefile_path.exists():
    sample_dir.mkdir(parents=True, exist_ok=True)

    if num_frames is not None:
        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", source, "-frames:v", str(num_frames), "-c:v", "copy", "-sn", samplefile]
    else:
        duration_val = duration if duration else "00:00:10"
        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", source, "-t", duration_val, "-c:v", "copy", "-sn", samplefile]
        
    subprocess.run(cmd, check=True)
    
    return str(samplefile)
        
def cut_clip(clip: vs.VideoNode, start_sec: int, num_frames: int = 1) -> vs.VideoNode:
    # Extract 1 frame at the 1200th second (20th minute) for a quick visual check
    # clip = extract_sample(clip, start_sec=1200, num_frames=1)

    fps = clip.fps.numerator / clip.fps.denominator
    start_frame = int(start_sec * fps)
    
    return clip[start_frame : start_frame + num_frames]

def parse_crop_values(ffmpeg_output: str) -> tuple[int, int, int, int]:
    
    crop_values = [line.split("crop=")[-1].split(" ")[0] 
                   for line in ffmpeg_output.splitlines() 
                   if "crop=" in line]
    
    most_common_crop = Counter(crop_values).most_common(1)[0][0]
    
    w, h, x, y = [int(val) for val in most_common_crop.strip().split(":")]
    
    return w, h, x, y

def ffmpeg_cropdetect(source: str, start_time: str = "00:00:00.000", frames: int = 100) -> str:
    
    cmd = ["ffmpeg", "-hide_banner", "-ss", start_time, "-i", source, "-vf", "cropdetect", "-an", "-sn", "-frames:v", str(frames), "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    return result.stderr

def print_node_info(vnode: vs.VideoNode):

    text = f"Format: {vnode.format} | Width: {vnode.width} | Height: {vnode.height} | Num_of_Frames: {vnode.num_frames} | FPS: {vnode.fps.numerator} | "

def get_clip_frame(vnode: vs.VideoNode, index: int) -> vs.VideoFrame:
    
    return vnode.get_frame(index)

def iterate_frames(vnode: vs.VideoNode):
    '''
    prefetch argument defines how many frames are rendered concurrently. 
    Is only there for debugging purposes and should never need to be changed. 
    
    backlog argument defines how many unconsumed frames (including those that 
    did not finish rendering yet) vapoursynth buffers at most before it stops 
    rendering additional frames. This argument is there to limit the memory 
    this function uses storing frames.
    '''
    yield from vnode.frames(prefetch=1, backlog=1)


def save_crop_as_image(cropped_clip: vs.VideoNode, frame_index: int, output_path: str):

    rgb_clip = cropped_clip.resize.Bicubic(format=vs.RGB24, matrix_in=1)
    writer = core.imwri.Write(rgb_clip, imgformat='PNG', filename=output_path, overwrite=True)
    return writer.get_frame(frame_index)

# Usage:
# save_crop_as_image(my_video_node, 120, 'C:/path/to/frame_120.png')

# 3. Handle color matrix and convert to RGB24 for IMWRI
# matrix = clip.get_frame(0).props.get('_Matrix', None)
# if matrix in [None, 2, 3]:
#     matrix = 1
# clip = core.resize.Bicubic(clip, format=vs.RGB24, matrix_in=matrix)

# # 4. Set up IMWRI writer to export PNG
# output_pattern = r'C:/path/to/output_frame_%06d.png'
# writer = core.imwri.Write(clip, imgformat='PNG', filename=output_pattern, overwrite=True)

# # 5. Request a specific frame number (e.g., frame 150)
# target_frame_number = 150
# writer.get_frame(target_frame_number)