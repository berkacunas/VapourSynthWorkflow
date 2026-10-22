import os
import subprocess
import re
import sys

def main():
    
    filepath = r"D:\BT\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"
    encoding_dir = r"D:\HOME\Encoding\Dune_Part2_2024"
    
    video_file = os.path.join(encoding_dir, "video_demux.hevc")
    m4a_file = os.path.join(encoding_dir, "audio_final.m4a")

    mkvextract_exe = "mkvextract.exe"
    eac3to_exe = r"E:\HOME\Documents\Encoding\SOFTWARE\eac3to\eac3to_3.64\eac3to.exe"
    qaac_exe = r"E:\HOME\Documents\Encoding\SOFTWARE\Apple CoreAudio\iTunes-makeportable\QTfiles64\qaac64.exe"

    os.makedirs(encoding_dir, exist_ok=True)

    mkv_result = subprocess.run([mkvextract_exe, filepath, "tracks", f"0:{video_file}"])
    if mkv_result.returncode != 0:
        print(f"Error: MKV extraction failed. Return code: {mkv_result.returncode}.", file=sys.stderr)
        sys.exit(1)

    info_process = subprocess.run([eac3to_exe, filepath], capture_output=True, text=True)
    
    track_id = None
    for line in info_process.stdout.splitlines():
        if "TrueHD" in line:
            track_id = line.split(":")[0].strip()
            break

    if not track_id:
        print("Error: TrueHD audio track not found in the source file.", file=sys.stderr)
        sys.exit(1)
    
    p1 = subprocess.Popen([eac3to_exe, filepath, f"{track_id}:", "stdout.wav", "-down6"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen([qaac_exe, "--tvbr", "127", "--no-delay", "-", "-o", m4a_file], stdin=p1.stdout)

    
    if p1.stdout is not None:
        p1.stdout.close()
    p2.communicate()

    if p2.returncode != 0:
        print(f"Error: Audio encoding failed. Error code: {p2.returncode}.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
