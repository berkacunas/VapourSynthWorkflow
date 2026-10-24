import vapoursynth as vs
core = vs.core

from vapoursynth_workflow.video_utilities import parse_crop_values, ffmpeg_stderr, load_fast_sample

# How to use vsrepo:
# $ vsrepo update
# $ vsrepo install lsmas

SOURCE_FILE = r"D:\BT\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"
SOURCE_HEVC = r"D:\HOME\Encoding\Dune_Part2_2024\video_demux.hevc"

SAMPLE_FILE = r"D:\HOME\Encoding\Dune_Part2_2024\Samples\sample_file.mkv"
SAMPLE_MODE = True
    
w, h, x, y = parse_crop_values(ffmpeg_stderr(SOURCE_FILE))
clip = load_fast_sample(source=SOURCE_FILE, samplefile=SAMPLE_FILE, start_time=1000, num_frames=50)
clip = core.std.CropAbs(clip, width=w, height=h, x=x, y=y)
# clip = core.std.FlipHorizontal(clip)
clip.set_output()
