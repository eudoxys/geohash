"""Command line interface

See `geohash` for the command syntax.

Examples
--------

    geohash 9mtzm4 32.225646,-115.43884

outputs

    9mtzm4=32.22564697265625,-115.4388427734375
    32.225646,-115.43884=9mtzm4

and

    geohash -p 8 -f "{lat:.4f},{lon:.4f}" 32.225646,-115.43884 9mtzm4

outputs

    32.225646,-115.43884=9mtzm4kp
    9mtzm4=32.2256,-115.4388
"""

import sys
import re
import argparse
import logging
import warnings

from ._core import geohash, geocode

_logger = logging.getLogger(__name__)

E_OK = 0
"""Exit code: ok"""
E_SYNTAX = 1
"""Exit code: syntax error, including no arguments and precision less than 1"""
E_EXCEPTION = 9
"""Exit code: exception caught (use `--debug` to see the traceback)"""

# an argument that looks like a negative LAT,LON (e.g. -32.2,115.4); it is a
# location, not an option (geohash codes never contain a comma)
_NEGATIVE_LATLON = r"-\.?\d[^,]*,.*"

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geohash",
        description="Convert each CODE to LAT,LON and each LAT,LON to CODE, "
            "and output the results line by line. Uses the geohash algorithm of CTA-5009-A.",
        epilog="Exit codes: 0 ok, 1 syntax error, 9 exception caught "
            "(use --debug to see traceback). "
            "See https://www.eudoxys.com/geohash for full documentation.")
    parser.add_argument("location",nargs="+",metavar="CODE|LAT,LON",
        help="geohash code or latitude,longitude pair to convert")
    parser.add_argument("-d","--debug",action="store_true",
        help="enable debug logging and traceback on exceptions")
    parser.add_argument("-f","--format",default="{lat},{lon}",metavar="FORMAT",
        help="lat/lon output format (default '{lat},{lon}')")
    parser.add_argument("-p","--precision",type=int,default=6,metavar="PRECISION",
        help="geohash code length (default 6)")
    parser.add_argument("-w","--warning",action="store_true",
        help="enable warning messages from python")
    # Treat LAT,LON arguments with a negative latitude (e.g. -32.2,115.4) as
    # positional arguments rather than unrecognized options. argparse has no
    # public hook for this; it already does the same for plain negative numbers.
    parser._negative_number_matcher = re.compile( # pylint: disable=protected-access
        rf"^-\d+$|^-\d*\.\d+$|^{_NEGATIVE_LATLON}$")
    return parser

def _parse_latlon(location:str) -> tuple[float,float]:
    """Return the latitude and longitude in a `LAT,LON` argument. Raises
    `ValueError` if it is not exactly two numbers separated by a comma.
    """
    parts = location.split(",")
    try:
        if len(parts) != 2:
            raise ValueError
        lat,lon = (float(x) for x in parts)
    except ValueError:
        raise ValueError(f"invalid LAT,LON {location!r}: expected two numbers "
            "separated by a comma") from None
    return lat,lon

def _convert(location:str, precision:int, fmt:str) -> str:
    if "," in location: # geohash codes never contain a comma
        lat,lon = _parse_latlon(location)
        return f"{location}={geohash(lat,lon,precision)}"
    lat,lon = geocode(location)
    return f"{location}={fmt.format(lat=lat,lon=lon)}"

def main(argv:list[str]|None=None) -> int:
    """Command line entry point

    Arguments
    ---------

      - `argv`: command line arguments (default `sys.argv[1:]`)

    Returns
    -------

      - `int`: exit code (0 ok, 1 syntax error, 9 exception caught)
    """
    parser = _parser()
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as err: # argparse exits on --help (0) and on errors (2)
        return E_OK if err.code in (0,None) else E_SYNTAX

    if args.precision < 1:
        print(f"ERROR [geohash]: precision must be positive, got {args.precision}",
            file=sys.stderr)
        return E_SYNTAX

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    with warnings.catch_warnings():
        if not args.warning:
            warnings.simplefilter("ignore")

        try:
            for location in args.location:
                _logger.debug("converting %r",location)
                print(_convert(location,args.precision,args.format))
            return E_OK
        except Exception as err: # pylint: disable=broad-exception-caught
            if args.debug:
                raise
            print(f"ERROR [geohash]: {type(err).__name__} {err}",file=sys.stderr)
            return E_EXCEPTION

if __name__ == "__main__":
    sys.exit(main())
