from pathlib import Path
import numpy as np
import vapoursynth as vs
from typing import Dict

class VapourSynthCrop:
    
    @staticmethod
    def get_crop_values(sourcefile: Path, num_samples: int = 15, threshold: int = 16) -> Dict[str, int] :
        
        core = vs.core
        
        clip = core.lsmas.LWLibavSource(source=str(sourcefile))
        
        y_clip = core.resize.Bicubic(clip, format=vs.GRAY8)
        
        total_frames = y_clip.num_frames
        step = max(1, total_frames // (num_samples + 1))
        
        top_list, bottom_list, left_list, right_list = [], [], [], []
        width, height = y_clip.width, y_clip.height

        for i in range(1, num_samples + 1):
            frame_idx = i * step
            if frame_idx >= total_frames:
                break
                
            frame = y_clip.get_frame(frame_idx)
            # Convert VapourSynth frame to NumPy array
            arr = np.asarray(frame[0])
            
            # Find pixels above the threshold (black level)
            non_black = np.where(arr > threshold)
            
            if non_black[0].size > 0 and non_black[1].size > 0:
                top_list.append(int(np.min(non_black[0])))
                bottom_list.append(int(height - 1 - np.max(non_black[0])))
                left_list.append(int(np.min(non_black[1])))
                right_list.append(int(width - 1 - np.max(non_black[1])))

        # To avoid distortion in dark scenes, use the smallest cropping (widest image) values.
        # and round to a multiple of 2 (mod2) for H.264/H.265 compatibility.
        top = (min(top_list) // 2) * 2 if top_list else 0
        bottom = (min(bottom_list) // 2) * 2 if bottom_list else 0
        left = (min(left_list) // 2) * 2 if left_list else 0
        right = (min(right_list) // 2) * 2 if right_list else 0

        return {
            "top": top,
            "bottom": bottom,
            "left": left,
            "right": right,
            "width": width,
            "height": height
        }

    # def foo():
    #     crop_values = Crop(clip, crop=False) 
    