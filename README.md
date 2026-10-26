# Installation

Install using Eudoxys Package Manager:

    pip install --upgrade eudoxys
    epm install geohash

Install using `pip`:

    pip install git+https://github.com/eudoxys/geohash
    
# Geohash tool

Syntax: geohash [OPTIONS ...] CODE|LAT,LON [CODE|LAT,LON ...]

## Options

    -d|--debug: enable debug logging and traceback output on exceptions
    -f|--format FORMAT: set lat/lon output format (default `{lat},{lon}`)
    -h|--help: output this help
    -p|--precision PRECISION: set geohash string length (default 6)
    -w|--warning: enable warning messages from python

Options apply to all arguments wherever they appear, and may also be given as
`--option=VALUE` or `-o=VALUE`.

Each CODE or LAT,LON tuple is converted to its corresponding LAT,LON or CODE
respectively and output, line by line.

The geohash tools conform to standard CTA-5009.

## Exit codes

    0: Ok
    1: Syntax error (including no arguments)
    9: Exception caught (use --debug to see traceback)

# Example

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

  

# Acknowledgments

- This material is based on work supported by the U.S. Department of Energy’s Office of Electricity through a grant from the Grid Controls and Communications Division
