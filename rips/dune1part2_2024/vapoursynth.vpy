from datetime import datetime

import vapoursynth as vs
import havsfunc as haf

from vapoursynth_workflow.video_utilities import save_crop_as_image

# How to use vsrepo:
# $ vsrepo update
# $ vsrepo install lsmas
# $ vsrepo install imwri
# $ vsrepo install havsfunc && vsrepo check havsfunc
# $ vsrepo install mlrt  => AI-filters

neo_f3kdb_path = r"E:\HOME\GitHub\berk\VapourSynthWorkflow\plugins\neo-f3kdb.dll"

num_of_threads = 2
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

core = vs.core
core.num_threads = num_of_threads
core.std.LoadPlugin(path=neo_f3kdb_path)

# 1. Load source
sourcefile = globals().get("sourcefile")
if sourcefile is None:
    raise ValueError("sourcefile argument was not passed to VapourSynth!")

# sourcefile = r"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024\samples\sample_file.mkv"
# samplefile = create_fast_sample(source=sourcefile, samplefile=samplefile, start_time=1500, num_frames=150)
clip = core.lsmas.LWLibavSource(source=sourcefile, format="YUV420P10", threads=2)

# 2 . Trim
start_frame = globals().get('start_frame')
end_frame = globals().get('end_frame')

if start_frame is not None or end_frame is not None:
    first_val = int(start_frame) if start_frame is not None else 0
    if end_frame is not None:
        clip = core.std.Trim(clip, first=first_val, last=int(end_frame))
    else:
        clip = core.std.Trim(clip, first=first_val)

# 3. Cropping
# VapourSynth cropping is heavily CPU-bound. If you are piping to a hardware 
# encoder (e.g., NVEncC, QSVEnc), disable this line and use the encoder's native 
# cropping parameters (like --crop) for better thermal stability and speed.
# w, h, x, y = parse_crop_values(ffmpeg_stderr(sourcefile))
# clip = core.std.Crop(clip, left=x, right=clip.width - w - x, top=y, bottom=clip.height - h - y)

# 4. Clean Grains
# clip = haf.SMDegrain(clip, tr=2, thSAD=150, RefineMotion=True)

#############################################################
# 5. AI Denoise Filter Example
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

# 6. Resize
target_width = 1920
target_height = ((int((clip.height * target_width) / clip.width)) // 2) * 2

clip = core.resize.Bicubic(clip, width=target_width, height=target_height,
                           matrix_in=vs.MatrixCoefficients.MATRIX_BT2020_NCL, transfer_in=vs.TransferCharacteristics.TRANSFER_ST2084,   
                           primaries_in=vs.ColorPrimaries.PRIMARIES_BT2020, matrix=vs.MatrixCoefficients.MATRIX_BT709,                
                           transfer=vs.TransferCharacteristics.TRANSFER_BT709, primaries=vs.ColorPrimaries.PRIMARIES_BT709)

# 7. Debanding
# vsrepo install neo_f3kdb
# clip = core.neo_f3kdb.Deband(clip, range=15, y=64, cb=64, cr=64, grainy=0, grainc=0, output_depth=10)

# 8. Color Space Tagging / Metadata Flagging
clip = core.std.SetFrameProps(clip, _Matrix=vs.MatrixCoefficients.MATRIX_BT709, _Transfer=vs.TransferCharacteristics.TRANSFER_BT709, 
                              _Primaries=vs.ColorPrimaries.PRIMARIES_BT709)

frame_index = clip.num_frames // 2
save_crop_as_image(clip, frame_index, fr"E:\HOME\GitHub\berk\VapourSynthWorkflow\rips\dune1part2_2024\samples\crop_image_{timestamp}_frame{frame_index}.png")

clip.set_output()
