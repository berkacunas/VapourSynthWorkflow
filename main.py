import argparse

from encoding import run_encode_pipeline, run_demux

def main():

    # Master Parser Initialization
    parser = argparse.ArgumentParser(description="")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True  # Ensures the script doesn't run without a valid sub-command

    # Sub-Command: encode
    encode_parser = subparsers.add_parser("encode", help="Run the full video encoding pipeline (Demux -> VapourSynth -> x264)")
    
    # Input / Output Arguments
    encode_parser.add_argument("-i", "--input", required=True, help="Source MKV file")
    encode_parser.add_argument("-a", "--audio", default="2", help="Audio track ID to extract via eac3to")
    encode_parser.add_argument("-o", "--output", default="encode_out.264", help="Output raw video file")
    
    # x264 Encoding Parameters
    encode_parser.add_argument("--crf", default="18", help="Constant Rate Factor (Quality: 0-51, lower is better)")
    encode_parser.add_argument("--preset", default="slower", 
                               choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
                               help="x264 encoding preset (determines CPU effort vs compression)")
    encode_parser.add_argument("--profile", default="high", choices=["baseline", "main", "high"], help="H.264 profile")
    encode_parser.add_argument("--level", default="4.1", choices=["3.0", "3.1", "3.2", "4.0", "4.1", "4.2", "5.0", "5.1", "5.2"],
                               help="H.264 hardware compatibility level")
    

    # Sub-Command: demux (Audio only) 
    demux_parser = subparsers.add_parser("demux", help="Only extract the audio track (no video processing)")
    demux_parser.add_argument("-i", "--input", required=True, help="Source file")
    demux_parser.add_argument("-t", "--track", default="2", help="Audio track ID to extract")
    demux_parser.add_argument("-a", "--audio", default=None, help="Extracted audio track file (Optional)")

    args = parser.parse_args()

    if args.command == "encode":
        run_encode_pipeline(args)
    elif args.command == "demux":
        run_demux(args)

if __name__ == "__main__":
    main()
