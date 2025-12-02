# Installation

Install using pip (python installer):

    pip install git+https://github.com/eudoxys.com/geohash
    
# Geohash tool

Syntax: geohash [OPTIONS ...] [CODE|LAT,LON ...]

## Options

    -d|--debug: enable traceback output on exceptions
    -f|--format=FORMAT: set lat/lon number format
    -h|--help|help: output this help
    -p|--precision=PRECISION: set geohash string length

Each CODE or LAT,LON tuple is converted to its corresponding LAT,LON or CODE
respectively and output, line by line.

The geohash tools conform to standard CTA-5009.

## Exit codes

    0: Ok
    1: Syntax error
    9: Exception caught (use --debug to see traceback)

# Example

The following command:

    geohash 9mtzm4 32.225646,-115.43884

gives the following output

    9mtzm4=32.22564697265625,-115.4388427734375
    32.225646,-115.43884=9mtzm4

  
