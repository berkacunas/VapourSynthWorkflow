from __future__ import annotations
import argparse
import subprocess
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import argparse

@dataclass
class DemuxConfig:
    
    input_file: Path
    output_path: Optional[Path] = None
    audio_track_id: int | None = None
    video_track_id: int | None = None

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> DemuxConfig:
        
        return cls(input_file=Path(args.input), 
                   output_path=Path(args.output) if getattr(args, 'output', None) else None,
                   audio_track_id=getattr(args, 'audio', None), 
                   video_track_id=getattr(args, 'video', None))
        
def _extract_track(decoder: str, input_file: Path, track_id: int, output_file: Path):
    
    cmd = ["mp4box", "-raw", f"{track_id}:output={str(output_file)}", str(input_file)]
    
    logger.info(f"[*] Executing demux: Extracting track {input_file} with {decoder}...")
    logger.info(f"[*] Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    logger.info("[+] Audio extraction completed.")
    
def _extract_audio(input_file: Path, output_file: Path, track_id: int) -> None:

    ext = input_file.suffix.lower()
    
    if ext != '.wav':
        output_file = output_file.with_suffix('.wav')
        logger.warning(f"Audio extraction output can strictly be WAV. The extension was automatically changed from '{ext}' to '.wav'.")
            
    match ext:
        case "mp4":
            # mp4box syntax: 
            # $ mp4box -raw <track_id>:output=<output_file> <input_file>
            decoder = "mp4box"
            try:
                _extract_track(decoder, input_file, track_id, output_file)
            except subprocess.CalledProcessError as e:
                logger.info(f"[-] An error occured during demuxing audio: {e}")
        case "mkv":
            # eac3to syntax: 
            # $ eac3to <input_file> <track_id>: <output_file>
            decoder = "eac3to"
            try:
                _extract_track("eac3to", input_file, track_id, output_file)
            except subprocess.CalledProcessError as e:
                logger.info(f"[-] An error occured during demuxing audio: {e}")
        case _:
            raise ValueError(f"Unsupported container format: {ext}")

def _extract_video(input_file: Path, output_file: Path, track_id: int) -> None:
    
    valid_exts = ['.h264', '.264', '.hevc', '.h265']
    
    if not output_file:
        # Defaulting to .h264 if user provides no output name
        output_file = input_file.with_suffix('.h264')
        
    original_suffix = output_file.suffix.lower()
    
    if original_suffix not in valid_exts:
        logger.warning(f"Output extension '{original_suffix}' is unusual for a raw video stream. Proceeding anyway, but verify your codec.")
        
    _extract_track(input_file, track_id, output_file)
    
    
def generate_vapoursynth(input_file: Path, vpy_file: Path):
    
    vpy_content = f"""import vapoursynth as vs
    core = vs.core
    clip = core.bs.VideoSource(source=r"{input_file.resolve()}")
    clip.set_output()
    """
    with open(vpy_file, "w", encoding="utf-8") as f:
        f.write(vpy_content)

def run_demux(args):
    
    input_file = Path(args.input)
    track_id = args.track
    
    if args.audio:
        audio_out = Path(args.audio)
    else:
        audio_out = input_file

    _extract_audio(input_file, audio_out, track_id)
    logger.info("[+] Demux completed!")

def run_encode_pipeline(args):
    """Executes the pipeline -> vpy -> pipe -> x264 workflow."""
    input_file = Path(args.input)
    audio_out = input_file.with_suffix('.aac')
    vpy_file = input_file.with_suffix('.vpy')

    # Demux
    logger.info(f"[*] Extracting track {args.audio} with eac3to...")
    subprocess.run(["eac3to", str(input_file), f"{args.audio}:", str(audio_out)], check=True)

    # Dynamic VapourSynth Project Generation
    logger.info(f"[*] Generating {vpy_file.name} project...")
    vpy_content = f"""import vapoursynth as vs
core = vs.core
clip = core.bs.VideoSource(source=r"{input_file.resolve()}")
clip.set_output()
"""
    with open(vpy_file, "w", encoding="utf-8") as f:
        f.write(vpy_content)

    # OS-Level Piping
    logger.info(f"[*] Initiating pipe: vspipe -> x264 (CRF {args.crf}, Preset: {args.preset})...")
    
    vspipe_cmd = ["vspipe", "-c", "y4m", str(vpy_file), "-"]
    
    x264_cmd = ["x264", "--demuxer", "y4m", "--crf", args.crf, "--preset", args.preset, "--profile", 
                args.profile, "--level", args.level, "--output", args.output, "-"]

    p_vspipe = subprocess.Popen(vspipe_cmd, stdout=subprocess.PIPE)
    p_x264 = subprocess.Popen(x264_cmd, stdin=p_vspipe.stdout)
    
    p_x264.wait()
    logger.info("[+] Full encode pipeline completed!")

