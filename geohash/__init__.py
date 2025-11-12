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
    from .geohash import geohash,geocode
except ImportError:
    from geohash import geohash,geocode

DEBUG=False
FORMAT="{lat},{lon}"
PRECISION=6

def main(args=None):

    if args == None:
        args = sys.argv[1:] if len(sys.argv) > 1 else []

    global FORMAT
    global PRECISION
    if len(args) == 0:
        print("\n".join([x for x in __doc__.split("\n") if x.startswith("Syntax: ")]),file=sys.stderr)
        return 1

    for arg in args:

        try:
            key,value = arg.split("=",1)
        except:
            key = arg
            value = None

        if key in ["-d","--debug"]:

            DEBUG=True

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

    # main(["-f={lat:.2f},{lon:.2f}","9mtzm4","32.227887,-115.436076","32.22564697265625,-115.4388427734375"],)

    try:

        rc = main()

    except:

        if DEBUG:
            raise

        e_name,e_value,e_trace = sys.exc_info()
        print(f"EXCEPTION: {e_name.__name__} {e_value}")
        rc = 9

    sys.exit(rc)