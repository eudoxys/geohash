"""Docstring examples show real output (issue #10)"""

import doctest
import importlib

import pytest

# the public functions are documented and doctested in the private
# `geohash._core` module that defines them
MODULES = ["geohash", "geohash._core", "geohash.cli"]

@pytest.mark.parametrize("name", MODULES)
def test_docstring_examples(name):
    module = importlib.import_module(name)
    result = doctest.testmod(module, optionflags=doctest.NORMALIZE_WHITESPACE)
    assert result.attempted > 0 or name == "geohash.cli"
    assert result.failed == 0
