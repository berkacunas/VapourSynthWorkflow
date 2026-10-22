$filepath = "D:\Movies\Completed\Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"
$encoding_dir = "D:\Movies\Completed\encoding"
$new_video_file = "D:\Movies\Completed\Dune.Part2.Encoded.Video.mkv"
$final_output = "D:\Movies\Completed\Dune.Part.Two.2024.Encoded.FINAL.mkv"

$truehdd_exe = "C:\Tools\truehdd.exe"
$qaac_exe = "C:\Tools\qaac64.exe"

$thd_file = "D:\Movies\Completed\encoding\audio_demux.thd"
$w64_file = "D:\Movies\Completed\encoding\audio_decode.w64"
$m4a_file = "D:\Movies\Completed\encoding\audio_final.m4a"

mkvextract.exe $filepath tracks 1:$thd_file

# Inspect file with eac2to
eac2to "$filepath"

# Decode audio stream with eac2to
eac3to "$filepath" 2: "$encoding_dir/audio_decode.wav"

& $qaac_exe --tvbr 127 --no-delay $w64_file -o $m4a_file
mkvmerge.exe -o $final_output $new_video_file $m4a_file
