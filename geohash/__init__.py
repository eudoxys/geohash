"""Geohash tools

Syntax: geohash [OPTIONS ...] [CODE|LAT,LON ...]

Options:

    -d|--debug: enable traceback output on exceptions
    -f|--format=FORMAT: set lat/lon number format
    -h|--help|help: output this help
    -p|--precision=PRECISION: set geohash string length

Each CODE or LAT,LON tuple is converted to its corresponding LAT,LON or CODE
respectively and output, line by line.

The geohash tools conform to standard CTA-5009.

Exit codes:

    0 - Ok
    1 - Syntax error
    9 - Exception caught (use --debug to see traceback)

Example:

The following command:

    geohash 9mtzm4 32.225646,-115.43884

gives the following output

    9mtzm4=32.22564697265625,-115.4388427734375
    32.225646,-115.43884=9mtzm4
"""

import sys
try:
    from .geohash import geohash,geocode,nearest,nearest2,distance
except ImportError:
    from geohash import geohash,geocode,nearest,nearest2,distance

DEBUG=False
FORMAT="{lat},{lon}"
PRECISION=6

def main(args=None):

    if args == None:
        args = sys.argv[1:] if len(sys.argv) > 1 else []

    global DEBUG
    if len(args) == 0:
        print("\n".join([x for x in __doc__.split("\n") if x.startswith("Syntax: ")]),file=sys.stderr)
        return 1

    # --debug applies to the whole command, wherever it appears
    DEBUG = any(arg.split("=",1)[0] in ["-d","--debug"] for arg in args)

    try:

        return _run(args)

    except Exception as err: # pylint: disable=broad-exception-caught

        if DEBUG:
            raise

        print(f"ERROR [geohash]: {type(err).__name__} {err}",file=sys.stderr)
        return 9

def _run(args):

    global FORMAT
    global PRECISION
    for arg in args:

        try:
            key,value = arg.split("=",1)
        except:
            key = arg
            value = None

        if key in ["-d","--debug"]:

            pass # handled in main()

        elif key in ["-f","--format"]:

            FORMAT = value

        elif key in ["-h","--help","help"]:

            print(__doc__)
            return 0

        elif key in ["-p","--precision"]:

            PRECISION = int(value)

        elif "," in arg: # lat/lon
            
            lat,lon = [float(x) for x in arg.split(",")]
            print(arg,geohash(lat,lon,PRECISION),sep="=")

        else: # geohash

            print(arg,FORMAT.format(**dict(zip(["lat","lon"],geocode(arg)))),sep="=")

    return 0

if __name__ == "__main__":

    sys.exit(main())
