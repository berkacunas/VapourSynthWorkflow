# VapourSynth Encoding Workflow

This repository contains low-level, modular video encoding and processing experiments built around [VapourSynth](https://www.vapoursynth.com/) and serves as a bridge, tracking how the classic Gordian Knot and scene workflows of the early 2000s have evolved into modern, modular, low-level media pipelines.

* **Video Processing**: VapourSynth (`vspipe`) for filtering and Mod2/Mod4 compliant cropping.
* **Video Encoding**: `x264` & `x265` handling low-level compression via raw piped streams.
* **Demuxing & Muxing**: GPAC (`MP4Box`) for low-level ISO parsing.
* **Audio Processing**: Apple CoreAudio (`qaac`) via TVBR for high-fidelity encoding.
