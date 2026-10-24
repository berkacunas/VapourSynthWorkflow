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

def load_fast_sample(source: str, samplefile: str, start_time: str | int = "00:20:00", duration: str | None = None, num_frames: int | None = None) -> vs.VideoNode:
    
    samplefile_path = Path(samplefile)
    sample_dir = samplefile_path.resolve().parent
    
    # if not samplefile_path.exists():
    sample_dir.mkdir(parents=True, exist_ok=True)

    if num_frames is not None:
        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", source, "-frames:v", str(num_frames), "-c:v", "copy", "-an", "-sn", samplefile]
    else:
        duration_val = duration if duration else "00:00:10"
        cmd = ["ffmpeg", "-y", "-ss", str(start_time), "-i", source, "-t", duration_val, "-c:v", "copy", "-an", "-sn", samplefile]
        
    subprocess.run(cmd, check=True)
        
    return core.lsmas.LWLibavSource(source=samplefile, format="YUV420P10")

def cut_clip(clip: vs.VideoNode, start_sec: int, num_frames: int = 1) -> vs.VideoNode:
    # Extract 1 frame at the 1200th second (20th minute) for a quick visual check
    # clip = extract_sample(clip, start_sec=1200, num_frames=1)

    fps = clip.fps.numerator / clip.fps.denominator
    start_frame = int(start_sec * fps)
    
    return clip[start_frame : start_frame + num_frames]

def parse_crop_values(ffmpeg_output: str) -> tuple[int, int, int, int]:
    
    crop_values = [line.split("crop=")[-1].split(" ")[0] for line in ffmpeg_output.splitlines() if "crop=" in line]
    most_common_crop = Counter(crop_values).most_common(1)[0][0]
    
    w, h, x, y = [int(val) for val in most_common_crop.strip().split(":")]
    return w, h, x, y

def parse_crop_values_deprecated(ffmpeg_output: str) -> tuple[int, int, int, int]:
    
    target = "crop="
    start_idx = ffmpeg_output.rfind(target)
    
    if start_idx == -1:
        raise ValueError("Cannot find 'crop=' in ffmpeg output. Please scan more frames.")
        
    start_idx += len(target)
    end_idx = ffmpeg_output.find("\n", start_idx)
    crop_str = ffmpeg_output[start_idx:end_idx] if end_idx != -1 else ffmpeg_output[start_idx:]
    
    w, h, x, y = [int(val) for val in crop_str.strip().split(":")]
    
    return w, h, x, y

def ffmpeg_stderr(source: str) -> str:
    
    cmd = ["ffmpeg", "-hide_banner", "-ss", "00:20:00", "-i", source, "-vf", "cropdetect", "-an", "-sn", "-frames:v", "100", "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    return result.stderr
