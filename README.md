[![Validation](https://github.com/eudoxys/geohash/actions/workflows/validate.yaml/badge.svg)](https://github.com/eudoxys/geohash/actions/workflows/validate.yaml)
[![Documentation](https://github.com/eudoxys/geohash/actions/workflows/deploy-pages.yaml/badge.svg)](https://github.com/eudoxys/geohash/actions/workflows/deploy-pages.yaml)

Eudoxys geohash tools

`geohash` encodes latitude/longitude positions as geohash codes and decodes
codes back to the latitude and longitude of their cell centers, following
standard CTA-5009. It also gives great-circle distances in km between codes
and finds the nearest code or position in a list. It provides a `geohash`
command and a Python API for anyone who needs compact, prefix-nested location
keys, and has no third-party dependencies.

# Documentation

See https://www.eudoxys.com/geohash

# Installation

Install using Eudoxys Package Manager:

    pip install --upgrade eudoxys
    epm install geohash

Install using `pip`:

    pip install git+https://github.com/eudoxys/geohash

Note: the name `geohash` on PyPI belongs to an unrelated package, so
`pip install geohash` without the URL installs the wrong package.

# Maintenance

## Update docs

    make docs

This builds the pdoc site in `docs/` (not committed). The
[Documentation](.github/workflows/deploy-pages.yaml) workflow publishes it to
https://www.eudoxys.com/geohash on each push to `main` that changes the
package code.

## Run tests

    pip install -e . pytest
    pytest

The tests need no credentials, network, or downloads, and run in under a
second. See [geohash/_test/README.md](geohash/_test/README.md) for what each
test file checks.

# Examples

## Command line

    geohash 9mtzm4 32.225646,-115.43884

prints

    9mtzm4=32.22564697265625,-115.4388427734375
    32.225646,-115.43884=9mtzm4

and

    geohash -p 8 -f "{lat:.4f},{lon:.4f}" 32.225646,-115.43884 9mtzm4

prints

    32.225646,-115.43884=9mtzm4kp
    9mtzm4=32.2256,-115.4388

Run `geohash --help` for all options and exit codes.

## Python

    from geohash import geohash, geocode, distance, nearest
    print(geohash(32.225646, -115.43884))
    print(geocode("9mtzm4"))
    print(round(distance("9q8yyk", "dr5reg"), 1))  # km
    print(nearest("9q8yyk", ["dr5reg", "9q5ctr", "c23nb6"], withdist=True))

prints

    9mtzm4
    (32.22564697265625, -115.4388427734375)
    4128.5
    ('9q5ctr', 558.749145533643)

# Acknowledgments

- This material is based on work supported by the U.S. Department of Energy’s Office of Electricity through a grant from the Grid Controls and Communications Division
