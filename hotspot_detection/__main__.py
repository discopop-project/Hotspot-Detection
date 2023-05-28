import argparse
from .hotspotDetection import read_and_write_results

def __parseArguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="hotspot_detection",
        description="create the hotspot-ratio of a given set of hotspot-analysis results",
    )

    parser.add_argument(
        "-f", "--files",
        help="list of filenames to read from",
        required=True,
        type=str,
        nargs="+",
    )

    parser.add_argument(
        "-o", "--output",
        help="output filename",
        required=True,
        type=str,
    )

    return parser.parse_args()



def main():
    args = __parseArguments()
    read_and_write_results(args.files, args.output)

if __name__ == "__main__":
    main()