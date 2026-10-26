"""Encode latitude/longitude positions as geohash codes and decode them back

Syntax
------

    geohash [-h] [-d] [-w] [-f FORMAT] [-p PRECISION] CODE|LAT,LON [CODE|LAT,LON ...]

Positional arguments
--------------------

  - `CODE`: a geohash code to decode to `LAT,LON` (case-insensitive)

  - `LAT,LON`: a latitude and longitude in degrees, separated by a comma,
    to encode as a geohash code; a negative latitude may be given as is
    (e.g. `-32.2,115.4`)

Optional arguments
------------------

  - `-d|--debug`: enable debug logging and traceback on exceptions

  - `-f|--format FORMAT`: Python format string for decoded locations, with
    fields `lat` and `lon` in degrees (default `{lat},{lon}`)

  - `-h|--help`: show the help message and exit

  - `-p|--precision PRECISION`: number of characters in encoded codes
    (default 6, at least 1)

  - `-w|--warning`: enable warning messages from python

Options apply to all arguments wherever they appear, and may also be given as
`--option=VALUE` or `-o=VALUE`.

Exit codes
----------

  - `0`: ok

  - `1`: syntax error, including no arguments and `PRECISION` less than 1

  - `9`: exception caught, e.g. an invalid `CODE` or `LAT,LON` (use
    `--debug` to see the traceback)

Description
-----------

A geohash code names a rectangular cell of latitude and longitude. Each
character of the code, from the alphabet `0123456789bcdefghjkmnpqrstuvwxyz`,
adds 5 bits that alternately halve the cell in longitude and latitude, so
longer codes name smaller cells and every code is a prefix of the codes of
the cells inside it. This is the geohash algorithm of CTA-5009-A, *Fast
and Readable Geographical Hashing* (Consumer Technology Association,
https://shop.cta.tech/products/cta-5009), which adopts the "Technical
description" of the Wikipedia Geohash article
(https://en.wikipedia.org/wiki/Geohash); `geohash/_test/test_conformance.py`
checks the alphabet, bit interleaving, interval halving, decoding to the cell
center, the cell sizes, and the article's worked examples.

The `geohash` command converts each `CODE` to `LAT,LON` and each `LAT,LON` to
`CODE`, and prints one line per argument, in order, as `ARGUMENT=RESULT`.
An argument containing a comma is a `LAT,LON`; anything else is a `CODE`.
Processing stops at the first argument that fails.

Given a latitude in [-90, 90] degrees, a longitude in [-180, 180] degrees, and
a precision $n \\ge 1$, `geohash.geohash.geohash()` returns a code that is
expected to satisfy:

  1. **Shape.** The code is a lowercase string of exactly $n$ characters from
     the geohash alphabet.

  2. **Containment.** The position lies inside the closed cell the code
     names. A position exactly on a cell boundary belongs to the cell to the
     south or west of it.

  3. **Nesting.** The code at precision $m < n$ is the first $m$ characters of
     the code at precision $n$.

  4. **Repeatability.** The same arguments always give the same code.

Given a code, `geohash.geohash.geocode()` returns the latitude and longitude
in degrees of the center of its cell, so that:

  1. **Round trip.** `geocode(geohash(lat, lon, n))` differs from
     `(lat, lon)` by at most half the cell height in latitude and half the
     cell width in longitude (see Data below).

  2. **Case.** Uppercase, lowercase and mixed-case codes decode alike.

Given two codes, `geohash.geohash.distance()` returns the great-circle
distance in km between their cell centers on a sphere of radius
`geohash.geohash.EARTH_RADIUS_KM`; it is non-negative, symmetric, and zero
for equal codes. `geohash.geohash.nearest()` and `geohash.geohash.nearest2()`
pick the closest entry of a list by that distance.

Invalid input raises `ValueError` (codes that are empty or contain a
character outside the alphabet, coordinates out of range or NaN, precision
less than 1) or `TypeError` (arguments of the wrong type).

What is not promised
--------------------

  - Decoding does not recover the original position, only the center of its
    cell; the error is up to half the cell size.

  - Codes that share a long prefix are close together, but close positions
    need not share a prefix: neighbors across a cell boundary, the equator,
    the prime meridian, or the antimeridian can have entirely different
    codes. There are no neighbor or bounding-box functions.

  - Conformance to CTA-5009-A covers the encoding and decoding algorithm
    only. The boundary rule (south or west), the input checks, the case
    handling, and the distance functions are choices of this package.

  - Coordinates are not wrapped or clamped: a latitude outside [-90, 90] or a
    longitude outside [-180, 180] is an error.

  - Distances assume a spherical Earth and can differ from ellipsoidal
    (geodesic) distances by up to about 0.5%. They are between cell centers,
    not the original positions.

  - Beyond about 22 characters the code resolves finer than a 64-bit float
    coordinate, so further characters carry no information.

  - `geohash.geohash.distance2()` is a squared difference in degrees, not a
    distance; it ignores the convergence of meridians and the antimeridian.

  - `geohash.geohash.geocode()` remembers every code it decodes for the life of
    the process, so memory grows with the number of distinct codes decoded.

Data
----

Cell size by code length, in degrees and in km at the equator (one degree is
about 111.195 km on a sphere of radius 6371 km; the east-west size in km
shrinks with the cosine of the latitude):

| Length | Latitude (deg) | Longitude (deg) | North-south (km) | East-west at equator (km) |
| -----: | -------------: | --------------: | ---------------: | ------------------------: |
|      1 | 45             | 45              | 5004             | 5004                      |
|      2 | 5.625          | 11.25           | 625.5            | 1251                      |
|      3 | 1.406          | 1.406           | 156.4            | 156.4                     |
|      4 | 0.1758         | 0.3516          | 19.55            | 39.09                     |
|      5 | 0.04395        | 0.04395         | 4.886            | 4.886                     |
|      6 | 0.005493       | 0.01099         | 0.6108           | 1.222                     |
|      7 | 0.001373       | 0.001373        | 0.1527           | 0.1527                    |
|      8 | 0.0001717      | 0.0003433       | 0.01909          | 0.03818                   |

```mermaid
flowchart LR
    latlon["LAT,LON (deg)"] -- geohash --> code[CODE]
    code -- geocode --> center["cell center LAT,LON (deg)"]
    code -- distance, nearest --> km[great-circle km]
```

Examples
--------

Encode a position and decode a code:

    geohash 9mtzm4 32.225646,-115.43884

prints

    9mtzm4=32.22564697265625,-115.4388427734375
    32.225646,-115.43884=9mtzm4

Use 8 characters and format the decoded location to 4 decimals:

    geohash -p 8 -f "{lat:.4f},{lon:.4f}" 32.225646,-115.43884 9mtzm4

prints

    32.225646,-115.43884=9mtzm4kp
    9mtzm4=32.2256,-115.4388

In Python:

    >>> from geohash import geohash, geocode, distance, nearest
    >>> geohash(32.225646, -115.43884)
    '9mtzm4'
    >>> geocode("9MTZM4")
    (32.22564697265625, -115.4388427734375)
    >>> round(distance("9q8yyk", "dr5reg"), 1)  # San Francisco to New York, km
    4128.5
    >>> nearest("9q8yyk", ["dr5reg", "9q5ctr", "c23nb6"], withdist=True)
    ('9q5ctr', 558.749145533643)
"""

try:
    import importlib.metadata
    __version__ = importlib.metadata.version("geohash")
except Exception: # pylint: disable=broad-exception-caught
    __version__ = "dev"

from .geohash import geohash,geocode,nearest,nearest2,distance
from .cli import main
