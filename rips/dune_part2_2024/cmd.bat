set "sourcefile=D:\BT\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"

set "eac2to_exe=E:\HOME\Documents\Encoding\SOFTWARE\eac3to\eac3to_3.64\eac3to.exe"
set "qaac_exe=E:\HOME\Documents\Encoding\SOFTWARE\Apple CoreAudio\iTunes-makeportable\QTfiles64\qaac64.exe"

set "demux_video=D:\HOME\Encoding\Dune_Part2_2024\video_demux.hevc"
set "thd_file=D:\HOME\Encoding\Dune_Part2_2024\audio_demux.thd"
set "m4a_file=D:\HOME\Encoding\Dune_Part2_2024\audio_final.m4a"

mkvextract "%sourcefile%" tracks 0:"%demux_video%"
mkvextract "%sourcefile%" tracks 1:"%thd_file%"

:: Inspect file with eac2to
"%eac2to_exe%" "%sourcefile%"

:: Decode | pipe and encode
"%eac2to_exe%" "%sourcefile%" 2: stdout.wav -down6 | "%qaac_exe%" --tvbr 127 --no-delay - -o "%m4a_file%"


:: Render VapourSynth script as Y4M stream and pipe directly to x265 STDIN
vspipe -y "video_script.vpy" - | x265 --y4m - --preset slow --crf 16 -o "output_video.hevc"

:: Merge final video and audio
:: mkvmerge.exe -o "%final_output%" "%new_video_file%" "%m4a_file%"
