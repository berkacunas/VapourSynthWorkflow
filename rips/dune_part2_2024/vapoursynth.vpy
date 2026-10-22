import vapoursynth as vs
core = vs.core

# Load 10-bit HEVC source safely via L-SMASH Works
clip = core.lsmas.LWLibavSource(source="video_demux.hevc", format="YUV420P10")

# Mod2 cropping for YUV420 color space (example values)
clip = core.std.Crop(clip, left=0, right=0, top=276, bottom=276)

clip.set_output()
