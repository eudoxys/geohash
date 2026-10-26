"""Tests for geohash.main() error handling (issue #3)"""

import pytest
import geohash

def test_main_ok(capsys):
    assert geohash.main(["9mtzm4"]) == 0
    assert capsys.readouterr().out == "9mtzm4=32.22564697265625,-115.4388427734375\n"

def test_main_exception_returns_9(capsys):
    assert geohash.main(["9mtzma"]) == 9
    out = capsys.readouterr()
    assert out.out == ""
    assert out.err.startswith("ERROR [geohash]: KeyError")
    assert len(out.err.strip().split("\n")) == 1

@pytest.mark.parametrize("flag",["-d","--debug"])
def test_main_debug_raises(flag):
    with pytest.raises(KeyError):
        geohash.main([flag,"9mtzma"])
    assert geohash.DEBUG

def test_main_debug_after_code_raises():
    with pytest.raises(KeyError):
        geohash.main(["9mtzma","--debug"])

def test_main_debug_does_not_persist(capsys):
    with pytest.raises(KeyError):
        geohash.main(["--debug","9mtzma"])
    assert geohash.main(["9mtzma"]) == 9
    assert not geohash.DEBUG
