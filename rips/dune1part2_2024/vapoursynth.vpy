from datetime import datetime
from pathlib import Path

import vapoursynth as vs
import havsfunc as haf
core = vs.core
core.num_threads = 3

from vapoursynth_workflow.video_utilities import parse_crop_values, ffmpeg_stderr, create_fast_sample, save_crop_as_image

sourcefile = r"D:\BT\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"
samplefile = r"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024\samples\sample_file.mkv"

neo_f3kdb_path = r"E:\HOME\GitHub\berk\VapourSynthWorkflow\plugins\neo-f3kdb.dll"

core.std.LoadPlugin(path=neo_f3kdb_path)

# How to use vsrepo:
# $ vsrepo update
# $ vsrepo install lsmas
# $ vsrepo install imwri
# $ vsrepo install havsfunc && vsrepo check havsfunc
# $ vsrepo install mlrt  => AI-filters

samplefile = create_fast_sample(source=sourcefile, samplefile=samplefile, start_time=1500, num_frames=150)

# 1. Load source
clip = core.lsmas.LWLibavSource(source=samplefile, format="YUV420P10")

# 2. Cropping
# VapourSynth cropping is heavily CPU-bound. If you are piping to a hardware 
# encoder (e.g., NVEncC, QSVEnc), disable this line and use the encoder's native 
# cropping parameters (like --crop) for better thermal stability and speed.
# w, h, x, y = parse_crop_values(ffmpeg_stderr(sourcefile))
# clip = core.std.Crop(clip, left=x, right=clip.width - w - x, top=y, bottom=clip.height - h - y)

# 3. Clean Grains
# clip = haf.SMDegrain(clip, tr=2, thSAD=150, RefineMotion=True)

#############################################################
# 4. AI Denoise Filter Example
# vsrepo install mlrt

# Convert to RGB-Float for AI access
# clip_rgb = core.resize.Bicubic(clip, format=vs.RGBS, matrix_in=vs.MatrixCoefficients.MATRIX_BT2020_NCL)

# DPIR Yapay Zeka filtresini çağırıyoruz. 
# strength: 5.0 light, 15.0 aggressive
# task: select 'denoise' or 'deblock'

# vsrepo install dpir
# import vs_dpir as dpir
# clip_rgb = dpir.DPIR(clip_rgb, strength=10.0, task='denoise', device_type='cuda')

# AI işleminden sonra videoyu tekrar orijinal 10-bit YUV formatına geri döndürüyoruz
# clip = core.resize.Bicubic(clip_rgb, format=vs.YUV420P10, matrix=vs.MatrixCoefficients.MATRIX_BT2020_NCL)
#############################################################

# 4. Resize
target_width = 1920
target_height = ((int((clip.height * target_width) / clip.width)) // 2) * 2

clip = core.resize.Bicubic(clip, width=target_width, height=target_height,
                           matrix_in=vs.MatrixCoefficients.MATRIX_BT2020_NCL, transfer_in=vs.TransferCharacteristics.TRANSFER_ST2084,   
                           primaries_in=vs.ColorPrimaries.PRIMARIES_BT2020, matrix=vs.MatrixCoefficients.MATRIX_BT709,                
                           transfer=vs.TransferCharacteristics.TRANSFER_BT709, primaries=vs.ColorPrimaries.PRIMARIES_BT709)

# 5. Debanding
# vsrepo install neo_f3kdb
# clip = core.neo_f3kdb.Deband(clip, range=15, y=64, cb=64, cr=64, grainy=0, grainc=0, output_depth=10)

# 5. Color Space Tagging / Metadata Flagging
clip = core.std.SetFrameProps(clip, _Matrix=vs.MatrixCoefficients.MATRIX_BT709, _Transfer=vs.TransferCharacteristics.TRANSFER_BT709, 
                              _Primaries=vs.ColorPrimaries.PRIMARIES_BT709)

frame_index = 50
save_crop_as_image(clip, frame_index, fr"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024\samples\crop_image_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}_frame{frame_index}.png")

clip.set_output()
