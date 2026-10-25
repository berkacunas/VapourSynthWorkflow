from pathlib import Path
import subprocess

from vapoursynth_workflow.video_domain_objects import EncoderSettings

root_dir = Path("./rips/dune_part2_2024")

encoded_sample_path = root_dir / Path("./samples/cropped_encoded_sample2.mkv")
vs_path = root_dir / Path("./vapoursynth.vpy")

encoder_settings = EncoderSettings()
        
vspipe_cmd = ["vspipe", "-c", "y4m", str(vs_path), "-"]
ffmpeg_cmd = ["ffmpeg", "-y", "-i", "pipe:0", "-c:v", encoder_settings.encoder, "-crf", str(encoder_settings.crf), "-preset", encoder_settings.preset, str(encoded_sample_path)]

sample_parent_dir = encoded_sample_path.resolve().parent
if not sample_parent_dir.exists():
    sample_parent_dir.mkdir(parents=True, exist_ok=True)

p1 = subprocess.Popen(vspipe_cmd, stdout=subprocess.PIPE)
p2 = subprocess.Popen(ffmpeg_cmd, stdin=p1.stdout)

if p1.stdout is not None:
    p1.stdout.close()
p2.wait()