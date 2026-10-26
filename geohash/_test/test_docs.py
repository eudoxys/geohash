"""Docstring examples show real output (issue #10)"""

import doctest
import importlib

import pytest

# importlib, because the package attribute `geohash.geohash` is the function
# re-exported by the package, not the module of the same name
MODULES = ["geohash", "geohash.geohash", "geohash.cli"]

@pytest.mark.parametrize("name", MODULES)
def test_docstring_examples(name):
    module = importlib.import_module(name)
    result = doctest.testmod(module, optionflags=doctest.NORMALIZE_WHITESPACE)
    assert result.attempted > 0 or name == "geohash.cli"
    assert result.failed == 0
