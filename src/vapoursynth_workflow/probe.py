import subprocess
import json
from pathlib import Path

from typing import Dict, Tuple, Any

class FfFileProbe:
    
    @staticmethod
    def probe_file(sourcefile: Path) -> Dict[str, Any]:
        
        probe_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_frames,tags", "-of", "json", sourcefile]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(probe_result.stdout)["streams"][0]
        
        return video_info
    
    @staticmethod
    def get_resolution(ffvideoinfo: Dict[str, Any]) -> Tuple[int, int]:
        
        w = ffvideoinfo["width"]
        h = ffvideoinfo["height"]
        
        return w, h

    @staticmethod
    def fftry_get_total_frames(ffvideoinfo: Dict[str, Any]) -> int:
        
        total_frames_str = ffvideoinfo.get("nb_frames") or ffvideoinfo.get("tags", {}).get("NUMBER_OF_FRAMES", "0")
        
        return int(total_frames_str)

class VapourSynthProbe:
    
    @staticmethod
    def probe(sourcefile: Path, vapoursynth_file: Path) -> Dict[str, Any]:
        
        probe_cmd = ["vspipe", "--arg", f"sourcefile={sourcefile.as_posix()}", "--info", vapoursynth_file.as_posix(), "-"]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        
        stdout = probe_result.stdout
        
        videoinfo: Dict[str, Any] = {}
        for line in stdout.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                videoinfo[key.strip()] = value.strip()
            
        # If the data has been read, ignore the vapoursynth crash error.
        # Crash only if it has failed to read the data and an error code is present.
        if not videoinfo and probe_result.returncode != 0:
            raise RuntimeError(f"VapourSynth Crashed:\n{probe_result.stderr}")
            
        return videoinfo

    @staticmethod
    def get_total_frames(vpinfo) -> int:
        
        return int(vpinfo["Frames"])

    @staticmethod
    def get_fps(vpinfo) -> float:
        
        text = str(vpinfo["FPS"])
        splitted = text.split("(")
        if len(splitted) > 1:
            fps_str = splitted[1].replace("fps)", "").strip()
            
        return float(fps_str)
