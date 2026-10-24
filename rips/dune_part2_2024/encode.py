from pathlib import Path
import subprocess

vs_path = Path("./vapoursynth.vpy")

vspipe_cmd = ["vspipe", "-c", "y4m", str(vs_path), "-"]
p1 = subprocess.Popen(vspipe_cmd, stdout=subprocess.PIPE)

ffmpeg_cmd = ["ffmpeg", "-y", "-i", "pipe:0", "-c:v", "libx265", "-crf", "18", "-preset", "fast", "cropped_encoded_sample2.mkv"]
p2 = subprocess.Popen(ffmpeg_cmd, stdin=p1.stdout)

if p1.stdout is not None:
    p1.stdout.close()
p2.wait()