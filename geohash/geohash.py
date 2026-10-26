"""Geohash encoding, decoding, and distances

Latitudes and longitudes are in degrees (north and east positive) and
distances are in km. Codes use the geohash alphabet
`0123456789bcdefghjkmnpqrstuvwxyz`; they are returned in lowercase and
accepted in any case.

The public functions are re-exported by the package, except
`distance2()` and `haversine_distance()`, which are imported from
`geohash.geohash`.

Examples
--------

    >>> from geohash import geohash, geocode, distance, nearest, nearest2
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
    >>> nearest2((37.7749, -122.4194), [(40.7128, -74.0060), (34.0522, -118.2437)])
    (1, (34.0522, -118.2437), 559.120577061553)

Caveats
-------

  - Decoding returns the center of the code's cell, not the position that
    was encoded; see the cell size table in the package documentation.

  - Close positions need not share a code prefix, e.g. across the equator,
    the prime meridian, or the antimeridian.

  - Distances are great-circle distances on a sphere of radius
    `EARTH_RADIUS_KM`.

References
----------

  - Consumer Technology Association, standard CTA-5009.

  - Geohash, https://en.wikipedia.org/wiki/Geohash

  - Haversine formula, https://en.wikipedia.org/wiki/Haversine_formula
"""

import math
import numbers

#
# Geographic location encoding/decoding
#
_cache = {}

_BASE32 = '0123456789bcdefghjkmnpqrstuvwxyz'
_DECODEMAP = {c:i for i,c in enumerate(_BASE32)}

def _normalize(gh):
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

def _decode(gh):
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
        for mask in [16, 8, 4, 2, 1]:
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

def geocode(gh):
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

      - Results are remembered for the life of the process, so memory grows
        with the number of distinct codes decoded.
    """
    gh = _normalize(gh)
    if gh in _cache:
        return _cache[gh][0],_cache[gh][1]
    lat, lon, _, _ = _decode(gh)
    # from math import log10
    # # Format to the number of decimals that are known
    # lats = "%.*f" % (max(1, int(round(-log10(lat_err)))) - 1, lat)
    # lons = "%.*f" % (max(1, int(round(-log10(lon_err)))) - 1, lon)
    # if '.' in lats: lats = lats.rstrip('0')
    # if '.' in lons: lons = lons.rstrip('0')
    _cache[gh] = (float(lat), float(lon))
    return float(lat), float(lon)

def _check_coordinate(name, value, limit):
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

def geohash(latitude, longitude, precision=6):
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
    __base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    __decodemap = { }
    for i,c in enumerate(__base32):
        __decodemap[c] = i
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    gh = []
    bits = [ 16, 8, 4, 2, 1 ]
    bit = 0
    ch = 0
    even = True
    while len(gh) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= bits[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            gh += __base32[ch]
            bit = 0
            ch = 0
    return ''.join(gh)

EARTH_RADIUS_KM = 6371.0
"""Earth radius in km used for great-circle distances. This is an
assumption: the IUGG mean Earth radius, treating the Earth as a sphere.
Distances computed with it can differ from ellipsoidal (geodesic)
distances by up to about 0.5%. For a different radius `R`, multiply the
result by `R / EARTH_RADIUS_KM`."""

def distance(a,b):
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

def distance2(a,b):
    """Squared coordinate difference between two geohash codes

    Arguments
    ---------

      - `a`: first geohash code (`str`, case-insensitive)

      - `b`: second geohash code (`str`, case-insensitive)

    Returns
    -------

      - `float`: $(\\Delta\\text{lat})^2 + (\\Delta\\text{lon})^2$ between the
        cell centers, in square degrees

    Raises `ValueError` or `TypeError` for an invalid code (see
    `geocode()`).

    Examples
    --------

        >>> from geohash.geohash import distance2
        >>> distance2("9q8yyk", "dr5reg")
        2351.7545644193888

    Caveats
    -------

      - This is not a distance: a degree of longitude is treated as equal to
        a degree of latitude at every latitude, and longitudes are not
        wrapped at the antimeridian. Use `distance()` for km.
    """

    x0,y0 = geocode(a)
    x1,y1 = geocode(b)
    dx,dy = x0-x1,y0-y1
    return dx*dx+dy*dy

def haversine_distance(lat1, lon1, lat2, lon2):
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

        >>> from geohash.geohash import haversine_distance
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

def nearest(gh,ghlist,withdist=False):
    """Find the geohash code in a list nearest to a given code

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
    return (None,float('nan')) if withdist else None

def nearest2(test_latlon, latlonlist):
    """Find the position in a list nearest to a given position

    Arguments
    ---------

      - `test_latlon`: latitude and longitude in degrees to search from

      - `latlonlist`: positions to search; each entry's first two items are
        its latitude and longitude in degrees, and further items are ignored

    Returns
    -------

      - `tuple[int,object,float]`: the index of the nearest entry in
        `latlonlist`, the entry itself, and its great-circle distance in km
        (see `haversine_distance()`); `(0, None, inf)` if `latlonlist` is
        empty

    Examples
    --------

        >>> nearest2((37.7749, -122.4194),
        ...     [(40.7128, -74.0060), (34.0522, -118.2437)])
        (1, (34.0522, -118.2437), 559.120577061553)
        >>> nearest2((0, 0), [])
        (0, None, inf)

    Caveats
    -------

      - Coordinates are not range-checked.

      - The search is linear in the length of `latlonlist`.

      - Of entries at equal distance, the first in `latlonlist` is returned.
    """
    test_lat, test_lon = test_latlon
    best_ix = 0
    best_dist = math.inf
    best_ll = None
    for _ix,ll in enumerate(latlonlist):
        _lat, _lon = ll[0:2]
        _new_dist = haversine_distance(_lat, _lon, test_lat, test_lon)
        if _new_dist < best_dist:
            best_dist = _new_dist
            best_ix = _ix
            best_ll = ll
    return best_ix, best_ll, best_dist
