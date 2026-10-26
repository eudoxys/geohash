"""Conformance tests for CTA-5009-A (issue #12)

CTA-5009-A, "Fast and Readable Geographical Hashing" (Consumer Technology
Association, https://shop.cta.tech/products/cta-5009), adopts the algorithm
in the "Technical description" section of the Wikipedia "Geohash" article
(https://en.wikipedia.org/wiki/Geohash). Each test below checks one point of
that algorithm, using the article's worked examples where it gives them:

  1. Alphabet: values 0-31 are written `0123456789bcdefghjkmnpqrstuvwxyz`
     (digits and lowercase letters except a, i, l, o), 5 bits per character,
     most significant bit first.

  2. Interleaving: counting bits from the left from 0, even bits refine the
     longitude and odd bits the latitude.

  3. Interval halving: latitude starts at [-90, 90] and longitude at
     [-180, 180]; each bit keeps the upper half if 1 and the lower half if 0.

  4. Decoding: the decoded position is the midpoint of the final intervals,
     and the error is half their width.

  5. Worked examples: `ezs42` decodes to about 42.605 +/- 0.022, -5.603 +/-
     0.022, and 57.64911, 10.40744 encodes to `u4pruydqqvj`.

  6. Precision: a code of length n carries floor(5n/2) latitude bits and
     ceil(5n/2) longitude bits, giving the article's error table.

The bit-level reference decoder here is written independently of
`geohash.geohash` so the package is checked against the algorithm as stated,
not against itself.
"""

import random

import pytest

from geohash.geohash import geohash, geocode, _decode

ALPHABET = "0123456789bcdefghjkmnpqrstuvwxyz"

def _bits(code):
    """Bit string of a code, 5 bits per character, MSB first"""
    return "".join(f"{ALPHABET.index(c):05b}" for c in code.lower())

def _halve(bits,low,high):
    """Interval left after halving [low,high] once per bit (1 = upper)"""
    for b in bits:
        mid = (low + high) / 2
        low,high = (mid,high) if b == "1" else (low,mid)
    return low,high

def _reference_decode(code):
    """Decode by the stated algorithm: (lat, lon, lat_err, lon_err)"""
    bits = _bits(code)
    lon_lo,lon_hi = _halve(bits[0::2],-180.0,180.0) # even bits
    lat_lo,lat_hi = _halve(bits[1::2],-90.0,90.0) # odd bits
    return ((lat_lo+lat_hi)/2, (lon_lo+lon_hi)/2,
        (lat_hi-lat_lo)/2, (lon_hi-lon_lo)/2)

# 1. Alphabet

def test_alphabet():
    assert len(ALPHABET) == 32 and len(set(ALPHABET)) == 32
    assert not set("ailo") & set(ALPHABET)
    assert ALPHABET[10:] == "bcdefghjkmnpqrstuvwxyz"

@pytest.mark.parametrize("value",range(32))
def test_alphabet_value(value):
    # the one-character cell with this 5-bit value: bits 0, 2, 4 are
    # longitude and bits 1, 3 are latitude
    bits = f"{value:05b}"
    lon_lo,lon_hi = _halve(bits[0::2],-180.0,180.0)
    lat_lo,lat_hi = _halve(bits[1::2],-90.0,90.0)
    lat,lon = (lat_lo+lat_hi)/2,(lon_lo+lon_hi)/2
    assert geohash(lat,lon,1) == ALPHABET[value]
    assert geocode(ALPHABET[value]) == (lat,lon)

# 2-4. Interleaving, interval halving, decoding to the midpoint

def test_ezs42_bits():
    # the article's split of `ezs42` into longitude and latitude codes
    bits = _bits("ezs42")
    assert bits == "0110111111110000010000010"
    assert bits[0::2] == "0111110000000"
    assert bits[1::2] == "101111001001"

def test_ezs42_decode():
    lat,lon,lat_err,lon_err = _decode("ezs42")
    assert (round(lat,3),round(lon,3)) == (42.605,-5.603)
    assert (round(lat_err,3),round(lon_err,3)) == (0.022,0.022)
    # final intervals 42.583 to 42.627 and -5.625 to -5.581
    assert (round(lat-lat_err,3),round(lat+lat_err,3)) == (42.583,42.627)
    assert (round(lon-lon_err,3),round(lon+lon_err,3)) == (-5.625,-5.581)

def test_ezs42_geocode_rounding():
    # "rounding 42.605 to 42.61 or 42.6 is correct, rounding to 43 is not"
    lat,lon = geocode("ezs42")
    assert round(lat,1) == 42.6 and round(lon,1) == -5.6

def _random_codes(count,seed=5009):
    rng = random.Random(seed)
    return ["".join(rng.choice(ALPHABET) for _ in range(rng.randint(1,12)))
        for _ in range(count)]

@pytest.mark.parametrize("code",_random_codes(200))
def test_decode_matches_reference(code):
    assert _decode(code) == _reference_decode(code)
    assert geocode(code) == _reference_decode(code)[:2]

@pytest.mark.parametrize("code",_random_codes(200,seed=12))
def test_encode_matches_reference(code):
    # the center of a cell encodes to that cell's code
    lat,lon,_,_ = _reference_decode(code)
    assert geohash(lat,lon,len(code)) == code

# 5. Worked encoding example

def test_u4pruydqqvj_encode():
    assert geohash(57.64911,10.40744,11) == "u4pruydqqvj"

# 6. Precision table

# length: (lat bits, lon bits, lat error, lon error) from the article
PRECISION = {
    1: (2,3,23,23),
    2: (5,5,2.8,5.6),
    3: (7,8,0.70,0.70),
    4: (10,10,0.087,0.18),
    5: (12,13,0.022,0.022),
    6: (15,15,0.0027,0.0055),
    7: (17,18,0.00068,0.00068),
    8: (20,20,0.000085,0.00017),
    }

@pytest.mark.parametrize("length",PRECISION)
def test_precision_table(length):
    lat_bits,lon_bits,lat_tab,lon_tab = PRECISION[length]
    assert len(_bits("0"*length)[1::2]) == lat_bits
    assert len(_bits("0"*length)[0::2]) == lon_bits
    _,_,lat_err,lon_err = _decode("s"*length)
    assert lat_err == 90 / 2**lat_bits
    assert lon_err == 180 / 2**lon_bits
    # the article rounds or truncates the errors to two significant
    # figures (e.g. 22.5 -> 23, 0.0879 -> 0.087), so match within 3%
    assert lat_err == pytest.approx(lat_tab,rel=0.03)
    assert lon_err == pytest.approx(lon_tab,rel=0.03)
