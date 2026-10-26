"""@private Geohash encoding, decoding, and distances

This module is private: import its public names from the package
(`from geohash import geohash, geocode, ...`), which documents them.

Latitudes and longitudes are in degrees (north and east positive) and
distances are in km. Codes use the geohash alphabet
`0123456789bcdefghjkmnpqrstuvwxyz`; they are returned in lowercase and
accepted in any case.

Examples
--------

    >>> from geohash import geohash, geocode, distance, nearest, nearest_latlon
    >>> geohash(32.225646, -115.43884)
    '9mtzm4'
    >>> geohash(32.225646, -115.43884, precision=8)
    '9mtzm4kp'
    >>> geocode("9mtzm4")
    (32.22564697265625, -115.4388427734375)
    >>> round(distance("9q8yyk", "dr5reg"), 1)
    4128.5
    >>> nearest("9q8yyk", ["dr5reg", "9q5ctr", "c23nb6"])
    '9q5ctr'
    >>> nearest_latlon((37.7749, -122.4194), [(40.7128, -74.0060), (34.0522, -118.2437)])
    (1, (34.0522, -118.2437), 559.120577061553)

References
----------

  - Consumer Technology Association, CTA-5009-A, *Fast and Readable
    Geographical Hashing*, https://shop.cta.tech/products/cta-5009 (free);
    it adopts the algorithm in the "Technical description" section of the
    Wikipedia Geohash article. The original CTA-5009 is the reference for
    the `geohash` claim (key 282) in the IANA CBOR Web Token (CWT) Claims
    registry, https://www.iana.org/assignments/cwt/cwt.xhtml

  - Geohash, https://en.wikipedia.org/wiki/Geohash

  - Haversine formula, https://en.wikipedia.org/wiki/Haversine_formula
"""

import functools
import math
import numbers
from collections.abc import Sequence

#
# Geographic location encoding/decoding
#
_BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz'
_DECODEMAP = {c:i for i,c in enumerate(_BASE32)}
_BITS = (16, 8, 4, 2, 1)

GEOCODE_CACHE_SIZE = 4096
"""Number of most recently decoded codes `geocode()` remembers. Decoding is
cheap, so this only saves repeated work in loops such as `nearest()`; it
bounds the memory used by the memo."""

def _normalize(gh:str) -> str:
    """Return the geohash `gh` in lowercase after checking that it is a
    non-empty string of geohash base32 characters. Raises `TypeError` if
    `gh` is not a string and `ValueError` if it is empty or contains a
    character outside `0123456789bcdefghjkmnpqrstuvwxyz` (case-insensitive).
    """
    if not isinstance(gh,str):
        raise TypeError(f"geohash must be a str, not {type(gh).__name__}")
    if not gh:
        raise ValueError("geohash is empty")
    code = gh.lower()
    for pos,c in enumerate(code):
        if c not in _DECODEMAP:
            raise ValueError(f"invalid geohash character {gh[pos]!r} "
                f"at position {pos} in {gh!r}")
    return code

def _decode(gh:str) -> tuple[float,float,float,float]:
    """
    Decode the geohash to its exact values, including the error
    margins of the result.  Returns four float values: latitude,
    longitude, the plus/minus error for latitude (as a positive
    number) and the plus/minus error for longitude (as a positive
    number). Raises `ValueError` if `gh` is not a valid geohash
    (see `_normalize()`).
    """
    gh = _normalize(gh)
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    lat_err, lon_err = 90.0, 180.0
    is_even = True
    for c in gh:
        cd = _DECODEMAP[c]
        for mask in _BITS:
            if is_even: # adds longitude info
                lon_err /= 2
                if cd & mask:
                    lon_interval = ((lon_interval[0]+lon_interval[1])/2, lon_interval[1])
                else:
                    lon_interval = (lon_interval[0], (lon_interval[0]+lon_interval[1])/2)
            else:      # adds latitude info
                lat_err /= 2
                if cd & mask:
                    lat_interval = ((lat_interval[0]+lat_interval[1])/2, lat_interval[1])
                else:
                    lat_interval = (lat_interval[0], (lat_interval[0]+lat_interval[1])/2)
            is_even = not is_even
    lat = (lat_interval[0] + lat_interval[1]) / 2
    lon = (lon_interval[0] + lon_interval[1]) / 2
    return lat, lon, lat_err, lon_err

@functools.lru_cache(maxsize=GEOCODE_CACHE_SIZE)
def _geocode(code:str) -> tuple[float,float]:
    """Return the cell center of the normalized (valid, lowercase) `code`,
    memoized for the `GEOCODE_CACHE_SIZE` most recently used codes."""
    lat, lon, _, _ = _decode(code)
    return float(lat), float(lon)

def geocode(gh:str) -> tuple[float,float]:
    """Decode a geohash code to the center of its cell

    Arguments
    ---------

      - `gh`: geohash code (`str`, case-insensitive)

    Returns
    -------

      - `tuple[float,float]`: latitude and longitude of the cell center,
        in degrees

    Raises `ValueError` if `gh` is empty or contains a character that
    is not in the geohash alphabet `0123456789bcdefghjkmnpqrstuvwxyz`
    (i.e., `a`, `i`, `l`, `o`, and any non-alphanumeric character), and
    `TypeError` if `gh` is not a string.

    Examples
    --------

        >>> geocode("9mtzm4")
        (32.22564697265625, -115.4388427734375)
        >>> geocode("9MTZM4")
        (32.22564697265625, -115.4388427734375)

    Caveats
    -------

      - The result is the cell center, not the position that was encoded;
        it differs from that position by up to half the cell size, e.g.
        about 0.0027 deg (0.31 km) in latitude and 0.0055 deg in longitude
        for a 6-character code.

      - The full floating-point center is returned; round it for display
        (e.g. with the CLI `--format` option).

      - The `GEOCODE_CACHE_SIZE` most recently decoded codes are remembered,
        so memory used by the memo is bounded.
    """
    return _geocode(_normalize(gh))

def _check_coordinate(name:str, value:float, limit:float) -> float:
    """Return `value` as a float after checking that it is a finite real
    number in [-`limit`, `limit`]. Raises `TypeError` if `value` is not a
    real number and `ValueError` if it is NaN or out of range.
    """
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise TypeError(f"{name} must be a real number, "
            f"not {type(value).__name__}")
    value = float(value)
    if not -limit <= value <= limit: # also rejects NaN
        raise ValueError(f"{name} {value!r} is outside [-{limit}, {limit}]")
    return value

def geohash(latitude:float, longitude:float, precision:int=6) -> str:
    """Encode a latitude and longitude as a geohash code

    Arguments
    ---------

      - `latitude`: latitude in degrees, north positive, in [-90, 90]

      - `longitude`: longitude in degrees, east positive, in [-180, 180]

      - `precision`: number of characters in the code (`int`, at least 1,
        default 6)

    Returns
    -------

      - `str`: lowercase geohash code of `precision` characters naming the
        cell that contains the position

    Raises `ValueError` if `latitude` is outside [-90, 90], `longitude` is
    outside [-180, 180] (coordinates are not wrapped), either is NaN, or
    `precision` is less than 1, and `TypeError` if a coordinate is not a
    real number or `precision` is not an integer.

    Examples
    --------

        >>> geohash(32.225646, -115.43884)
        '9mtzm4'
        >>> geohash(32.225646, -115.43884, precision=8)
        '9mtzm4kp'
        >>> geohash(-32.2, 115.4)
        'qd60cf'

    Caveats
    -------

      - A position exactly on a cell boundary is assigned to the cell to the
        south or west of it, e.g. `geohash(0, 0)` returns `'7zzzzz'`.

      - Beyond about 22 characters the code resolves finer than a 64-bit
        float coordinate, so further characters carry no information.
    """
    latitude = _check_coordinate("latitude", latitude, 90)
    longitude = _check_coordinate("longitude", longitude, 180)
    if isinstance(precision, bool) or not isinstance(precision, numbers.Integral):
        raise TypeError(f"precision must be an int, "
            f"not {type(precision).__name__}")
    if precision < 1:
        raise ValueError(f"precision must be positive, got {precision}")
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    gh = []
    bit = 0
    ch = 0
    even = True
    while len(gh) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= _BITS[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= _BITS[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            gh.append(_BASE32[ch])
            bit = 0
            ch = 0
    return ''.join(gh)

EARTH_RADIUS_KM = 6371.0
"""Earth radius in km used for great-circle distances. This is an
assumption: the IUGG mean Earth radius, treating the Earth as a sphere.
Distances computed with it can differ from ellipsoidal (geodesic)
distances by up to about 0.5%. For a different radius `R`, multiply the
result by `R / EARTH_RADIUS_KM`."""

def distance(a:str,b:str) -> float:
    """Great-circle distance between two geohash codes

    Arguments
    ---------

      - `a`: first geohash code (`str`, case-insensitive)

      - `b`: second geohash code (`str`, case-insensitive)

    Returns
    -------

      - `float`: great-circle distance in km between the centers of the two
        cells, on a sphere of radius `EARTH_RADIUS_KM`

    Raises `ValueError` or `TypeError` for an invalid code (see
    `geocode()`).

    Examples
    --------

        >>> round(distance("9q8yyk", "dr5reg"), 1)  # San Francisco to New York
        4128.5
        >>> distance("9q8yyk", "9Q8YYK")
        0.0

    Caveats
    -------

      - The distance is between cell centers, so it can differ from the
        distance between the encoded positions by up to the cell diagonal.

      - The spherical Earth can make the result differ from an ellipsoidal
        (geodesic) distance by up to about 0.5%.
    """
    lat1,lon1 = geocode(a)
    lat2,lon2 = geocode(b)
    return haversine_distance(lat1, lon1, lat2, lon2)

def haversine_distance(lat1:float, lon1:float, lat2:float, lon2:float) -> float:
    """Great-circle distance between two positions

    Arguments
    ---------

      - `lat1`: latitude of the first position in degrees

      - `lon1`: longitude of the first position in degrees

      - `lat2`: latitude of the second position in degrees

      - `lon2`: longitude of the second position in degrees

    Returns
    -------

      - `float`: great-circle distance in km, computed with the haversine
        formula on a sphere of radius `EARTH_RADIUS_KM`

    Examples
    --------

        >>> haversine_distance(0, 0, 0, 1)  # one degree along the equator
        111.19492664455873

    Caveats
    -------

      - Arguments are not range-checked; longitudes that differ by 360
        degrees give the same result.

      - The spherical Earth can make the result differ from an ellipsoidal
        (geodesic) distance by up to about 0.5%.
    """
    phi1 = lat1 * math.pi/180
    phi2 = lat2 * math.pi/180
    delta_phi = phi2 - phi1
    delta_lam = (lon2 - lon1) * math.pi/180
    a = (math.sin(delta_phi/2) * math.sin(delta_phi/2)
         + math.cos(phi1) * math.cos(phi2)
         * math.sin(delta_lam/2) * math.sin(delta_lam/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return c * EARTH_RADIUS_KM

def nearest(gh:str,ghlist:Sequence[str],withdist:bool=False) -> str|None|tuple[str|None,float]:
    """Find the geohash code in a list nearest to a given code

    Use `nearest_latlon()` to search latitude/longitude positions instead.

    Arguments
    ---------

      - `gh`: geohash code to search from (`str`, case-insensitive)

      - `ghlist`: geohash codes to search (sequence of `str`)

      - `withdist`: also return the distance (default `False`)

    Returns
    -------

      - `str`: the entry of `ghlist` nearest to `gh` by `distance()`, or
        `None` if `ghlist` is empty, when `withdist` is false

      - `tuple[str,float]`: that entry and its distance in km, or
        `(None, nan)` if `ghlist` is empty, when `withdist` is true

    Raises `ValueError` or `TypeError` for an invalid code (see
    `geocode()`).

    Examples
    --------

        >>> nearest("9q8yyk", ["dr5reg", "9q5ctr", "c23nb6"])
        '9q5ctr'
        >>> nearest("9q8yyk", ["dr5reg", "9q5ctr", "c23nb6"], withdist=True)
        ('9q5ctr', 558.749145533643)
        >>> nearest("9q8yyk", [], withdist=True)
        (None, nan)

    Caveats
    -------

      - The search is linear in the length of `ghlist`.

      - Of entries at equal distance, the first in `ghlist` is returned.
    """
    if len(ghlist) > 0:
        best = min(((x,distance(gh,x)) for x in ghlist),key=lambda y:y[1])
        return best if withdist else best[0]
    return (None,math.nan) if withdist else None

def nearest_latlon(latlon:Sequence[float],
        latlonlist:Sequence[Sequence]) -> tuple[int|None,object,float]:
    """Find the position in a list nearest to a given position

    Use `nearest()` to search geohash codes instead.

    Arguments
    ---------

      - `latlon`: latitude and longitude in degrees to search from

      - `latlonlist`: positions to search; each entry's first two items are
        its latitude and longitude in degrees, and further items are ignored

    Returns
    -------

      - `tuple[int,object,float]`: the index of the nearest entry in
        `latlonlist`, the entry itself, and its great-circle distance in km
        (see `haversine_distance()`); `(None, None, nan)` if `latlonlist`
        is empty

    Examples
    --------

        >>> nearest_latlon((37.7749, -122.4194),
        ...     [(40.7128, -74.0060), (34.0522, -118.2437)])
        (1, (34.0522, -118.2437), 559.120577061553)
        >>> nearest_latlon((0, 0), [(10, 0, "a"), (1, 0, "b")])
        (1, (1, 0, 'b'), 111.19492664455873)
        >>> nearest_latlon((0, 0), [])
        (None, None, nan)

    Caveats
    -------

      - Coordinates are not range-checked.

      - The search is linear in the length of `latlonlist`.

      - Of entries at equal distance, the first in `latlonlist` is returned.
    """
    lat, lon = latlon
    best_ix = None
    best_dist = math.inf
    best_ll = None
    for ix,ll in enumerate(latlonlist):
        dist = haversine_distance(ll[0], ll[1], lat, lon)
        if dist < best_dist:
            best_ix, best_ll, best_dist = ix, ll, dist
    return (best_ix, best_ll, best_dist) if best_ix is not None else (None, None, math.nan)
