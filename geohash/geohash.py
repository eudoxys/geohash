"""Geohash library"""

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
    """
    Decode geohash, returning two strings with latitude and longitude
    containing only relevant digits and with trailing zeroes removed.

    Geohashes are case-insensitive, e.g., `geocode("9MTZM4")` and
    `geocode("9mtzm4")` return the same location.

    Raises `ValueError` if `gh` is empty or contains a character that
    is not in the geohash base32 alphabet
    `0123456789bcdefghjkmnpqrstuvwxyz` (i.e., `a`, `i`, `l`, `o`, and
    any non-alphanumeric character), and `TypeError` if `gh` is not a
    string.
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
    """Encode a position given in float arguments latitude, longitude to
    a geohash which will have the character count precision.

    Example: `geohash(32.225646,-115.43884)` returns `"9mtzm4"`.

    Raises `ValueError` if `latitude` is outside [-90, 90], `longitude` is
    outside [-180, 180] (coordinates are not wrapped), either is NaN, or
    `precision` is less than 1, and `TypeError` if a coordinate is not a
    real number or `precision` is not an integer.
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
    """Get the great-circle distance in km between two geohashes.

    Each geohash is decoded to the center of its cell (see `geocode()`)
    and the distance is computed by `haversine_distance()` using
    `EARTH_RADIUS_KM`.

    Example: `distance("9q8yyk", "dr5reg")` (San Francisco to New York)
    returns about 4130 km.
    """
    lat1,lon1 = geocode(a)
    lat2,lon2 = geocode(b)
    return haversine_distance(lat1, lon1, lat2, lon2)

def distance2(a,b):
    """Get the distance squared between two geohashes"""

    x0,y0 = geocode(a)
    x1,y1 = geocode(b)
    dx,dy = x0-x1,y0-y1
    return dx*dx+dy*dy

def haversine_distance(lat1, lon1, lat2, lon2):
    '''
    Returns the great-circle distance in km between two points given as
    latitude and longitude in degrees, using the haversine formula on a
    sphere of radius `EARTH_RADIUS_KM`.
    '''
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
    """Find the nearest geohash in a list of geohashes.

    Returns the nearest geohash in `ghlist`, or `None` if `ghlist` is
    empty. If `withdist` is true, returns a tuple of the nearest geohash
    and its great-circle distance in km from `gh` (see `distance()`), or
    `(None, nan)` if `ghlist` is empty.
    """
    if len(ghlist) > 0:
        best = min(((x,distance(gh,x)) for x in ghlist),key=lambda y:y[1])
        return best if withdist else best[0]
    return (None,float('nan')) if withdist else None

def nearest2(test_latlon, latlonlist):
    """Find the nearest lat/lon in a list of lat/lons.

    Returns a tuple of the index of the nearest entry in `latlonlist`, the
    entry itself, and its great-circle distance in km from `test_latlon`
    (see `haversine_distance()`). If `latlonlist` is empty, returns
    `(0, None, inf)`.
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
