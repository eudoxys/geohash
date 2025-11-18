"""Geohash library"""

import math

#
# Geographic location encoding/decoding
#
_cache = {}

def _decode(gh):
    """
    Decode the geohash to its exact values, including the error
    margins of the result.  Returns four float values: latitude,
    longitude, the plus/minus error for latitude (as a positive
    number) and the plus/minus error for longitude (as a positive
    number).
    """
    __base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
    __decodemap = { }
    for i,c in enumerate(__base32):
        __decodemap[c] = i
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    lat_err, lon_err = 90.0, 180.0
    is_even = True
    for c in gh:
        cd = __decodemap[c]
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
    """
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

def geohash(latitude, longitude, precision=6):
    """Encode a position given in float arguments latitude, longitude to
    a geohash which will have the character count precision.
    """
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

def distance(a,b):
    """Get the distance between to geohashes"""
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
    Returns the great-circle distance between two point in meters
    '''
    phi1 = lat1 * math.pi/180
    phi2 = lat2 * math.pi/180
    delta_phi = phi2 - phi1
    delta_lam = (lon2 - lon1) * math.pi/180
    a = (math.sin(delta_phi/2) * math.sin(delta_phi/2)
         + math.cos(phi1) * math.cos(phi2)
         * math.sin(delta_lam/2) * math.sin(delta_lam/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return c * 6378.1e3 # radius of earth in km

def nearest(gh,ghlist,withdist=False):
    """Find the nearest geohash in a list of geohashes"""
    if len(ghlist) > 0:
        dist = sorted([(x,distance2(gh,x)) for x in ghlist],key=lambda y:y[1])
        return (dist[0][0],distance(gh,dist[0][0])) if withdist else dist[0][0]
    return (None,float('nan')) if withdist else None

def nearest2(test_latlon, latlonlist):
    """Find the nearest lat/lon in a list of lat/lons"""
    test_lat, test_lon = test_latlon
    best_ix = 0
    best_dist = math.inf
    for _ix,ll in enumerate(latlonlist):
        _lat, _lon = ll[0:2]
        _new_dist = haversine_distance(_lat, _lon, test_lat, test_lon)
        if _new_dist < best_dist:
            best_dist = _new_dist
            best_ix = _ix
    return best_ix, latlonlist[best_ix], best_dist
