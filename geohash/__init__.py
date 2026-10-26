"""Geohash tools

Syntax: geohash [OPTIONS ...] CODE|LAT,LON [CODE|LAT,LON ...]

Options:

    -d|--debug: enable debug logging and traceback output on exceptions
    -f|--format FORMAT: set lat/lon output format (default `{lat},{lon}`)
    -h|--help: output this help
    -p|--precision PRECISION: set geohash string length (default 6)
    -w|--warning: enable warning messages from python

Options apply to all arguments wherever they appear, and may also be given as
`--option=VALUE` or `-o=VALUE`.

Each CODE or LAT,LON tuple is converted to its corresponding LAT,LON or CODE
respectively and output, line by line.
CODE is case-insensitive. A CODE that is empty or contains a character
outside the geohash alphabet `0123456789bcdefghjkmnpqrstuvwxyz` is
reported as a `ValueError` (exit code 9).
A LAT,LON must be exactly two numbers separated by a comma, with latitude
in [-90, 90] and longitude in [-180, 180] (coordinates are not wrapped);
anything else is reported as a `ValueError` (exit code 9). PRECISION must
be at least 1 (syntax error otherwise).

The geohash tools conform to standard CTA-5009.

Exit codes:

    0 - Ok
    1 - Syntax error (including no arguments)
    9 - Exception caught (use --debug to see traceback)

Example:

The following command:

    geohash 9mtzm4 32.225646,-115.43884

gives the following output

    9mtzm4=32.22564697265625,-115.4388427734375
    32.225646,-115.43884=9mtzm4

The following command:

    geohash -p 8 -f "{lat:.4f},{lon:.4f}" 32.225646,-115.43884 9mtzm4

gives the following output

    32.225646,-115.43884=9mtzm4kp
    9mtzm4=32.2256,-115.4388
"""

try:
    import importlib.metadata
    __version__ = importlib.metadata.version("geohash")
except Exception: # pylint: disable=broad-exception-caught
    __version__ = "dev"

from .geohash import geohash,geocode,nearest,nearest2,distance
from .cli import main
