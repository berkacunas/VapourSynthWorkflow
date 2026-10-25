import vapoursynth as vs
core = vs.core

core.num_threads = 2

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

clip.set_output()

# clip = core.std.FlipHorizontal(clip)
# clip = clip.std.Trim(first=100, last=2000).std.FlipVertical()
# clip = core.resize.Bicubic(clip, format=vs.YUV422P10)
# clip.set_output(alt_output=1)

# for frame in clip.frames():
#     # Do stuff with your frame
#     pass

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
