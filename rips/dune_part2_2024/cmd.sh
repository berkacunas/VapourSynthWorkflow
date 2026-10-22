#!/bin/bash

# Install fdkaac
sudo apt update -y > /dev/null 2>&1
sudo apt install -y fdkaac cargo git > /dev/null 2>&1

# Install truehdd from gitHub repo
if ! command -v truehdd &> /dev/null; then
    git clone https://github.com /tmp/truehdd > /dev/null 2>&1
    cd /tmp/truehdd && cargo build --release > /dev/null 2>&1
    sudo cp target/release/truehdd /usr/local/bin/ > /dev/null 2>&1
fi

filepath="/mnt/BETELGEUSE/BT/Completed/Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"

# mkvmerge -i "$filepath"

encoding_dir="encoding"
mkdir "$encoding_dir"

# Extract (demux) video stream
mkvextract "$filepath" tracks 0:"$encoding_dir/video_demux.hevc"

# Extract (demux TrueHD / Atmos) audio stream
mkvextract "$filepath" tracks 1:"$encoding_dir/audio_demux.thd"






final_output="/mnt/BETELGEUSE/BT/Completed/Dune.Part.Two.2024.Encoded.FINAL.mkv"



thd_file="/mnt/BETELGEUSE/BT/Completed/encoding/audio_demux.thd"
w64_file="/mnt/BETELGEUSE/BT/Completed/encoding/audio_decode.w64"
m4a_file="/mnt/BETELGEUSE/BT/Completed/encoding/audio_final.m4a"

mkvextract "$filepath" tracks 1:"$thd_file"
truehdd decode --presentation max "$thd_file" --format w64 --output-path "$w64_file"
fdkaac -p 2 -m 5 "$w64_file" -o "$m4a_file"
mkvmerge -o "$final_output" "$new_video_file" "$m4a_file"

