#!/bin/bash

# Install fdkaac
sudo apt update -y > /dev/null 2>&1
sudo apt install -y fdkaac cargo git > /dev/null 2>&1

# Install truehdd from gitHub repo
if ! command -v truehdd &> /dev/null; then
    git clone https://github.com/truehdd/truehdd.git /tmp/truehdd > /dev/null 2>&1
    cd /tmp/truehdd && cargo build --release > /dev/null 2>&1
    sudo cp target/release/truehdd /usr/local/bin/ > /dev/null 2>&1
fi

filepath="/mnt/BETELGEUSE/BT/Completed/Dune.Part.Two.2024.UHD.BluRay.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR.mkv"
encoding_dir="/mnt/BETELGEUSE/BT/Completed/encoding"

mkdir -p "$encoding_dir"

new_video_file="$encoding_dir/video_demux.hevc"
thd_file="$encoding_dir/audio_demux.thd"
m4a_file="$encoding_dir/audio_final.m4a"
final_output="/mnt/BETELGEUSE/BT/Completed/Dune.Part.Two.2024.Encoded.FINAL.mkv"

mkvextract "$filepath" tracks 0:"$new_video_file" 1:"$thd_file"

truehdd decode --presentation max "$thd_file" --format wav --output-path - | fdkaac -p 2 -m 5 - -o "$m4a_file"

mkvmerge -o "$final_output" "$new_video_file" "$m4a_file"
