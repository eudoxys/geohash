"""Tests for the geohash command line interface (issues #3, #4)"""

import warnings
import pytest
import geohash
from geohash.cli import main

CODE = "9mtzm4"
CODE_OUT = "9mtzm4=32.22564697265625,-115.4388427734375\n"

def test_package_exports_main():
    assert geohash.main is main

def test_main_ok(capsys):
    assert main([CODE]) == 0
    assert capsys.readouterr().out == CODE_OUT

def test_main_latlon_and_code(capsys):
    assert main([CODE,"32.225646,-115.43884"]) == 0
    assert capsys.readouterr().out == CODE_OUT + "32.225646,-115.43884=9mtzm4\n"

def test_main_negative_latitude(capsys):
    assert main(["-32.2,115.4"]) == 0
    assert capsys.readouterr().out == "-32.2,115.4=qd60cf\n"

@pytest.mark.parametrize("argv",[
    ["-p","8","32.225646,-115.43884"],
    ["-p=8","32.225646,-115.43884"],
    ["--precision","8","32.225646,-115.43884"],
    ["--precision=8","32.225646,-115.43884"],
    ["32.225646,-115.43884","-p","8"],
    ])
def test_main_precision(capsys,argv):
    assert main(argv) == 0
    assert capsys.readouterr().out == "32.225646,-115.43884=9mtzm4kp\n"

@pytest.mark.parametrize("opt",["-f","--format"])
def test_main_format(capsys,opt):
    assert main([opt,"{lat:.2f};{lon:.2f}",CODE]) == 0
    assert capsys.readouterr().out == "9mtzm4=32.23;-115.44\n"
    assert main([f"{opt}={{lat:.1f}}",CODE]) == 0
    assert capsys.readouterr().out == "9mtzm4=32.2\n"

def test_main_options_do_not_persist(capsys):
    assert main(["-p","8","-f","{lat}",CODE,"32.225646,-115.43884"]) == 0
    capsys.readouterr()
    assert main([CODE,"32.225646,-115.43884"]) == 0
    assert capsys.readouterr().out == CODE_OUT + "32.225646,-115.43884=9mtzm4\n"

@pytest.mark.parametrize("argv",[
    [],
    ["-f",CODE], # missing value consumes the only location
    ["-p"],
    ["-p","x",CODE],
    ["-p","0",CODE],
    ["--bogus",CODE],
    ])
def test_main_syntax_error(capsys,argv):
    assert main(argv) == 1
    out = capsys.readouterr()
    assert out.out == ""
    assert "geohash" in out.err

@pytest.mark.parametrize("opt",["-h","--help"])
def test_main_help(capsys,opt):
    assert main([opt]) == 0
    assert "usage: geohash" in capsys.readouterr().out

def test_main_exception_returns_9(capsys):
    assert main(["9mtzma"]) == 9
    out = capsys.readouterr()
    assert out.out == ""
    assert out.err.startswith("ERROR [geohash]: KeyError")
    assert len(out.err.strip().split("\n")) == 1

def test_main_bad_format_returns_9(capsys):
    assert main(["-f","{x}",CODE]) == 9
    assert capsys.readouterr().err.startswith("ERROR [geohash]: KeyError")

def test_main_help_word_is_not_an_option(capsys):
    assert main(["help"]) == 9 # treated as a (bad) geohash code

@pytest.mark.parametrize("flag",["-d","--debug"])
def test_main_debug_raises(flag):
    with pytest.raises(KeyError):
        main([flag,"9mtzma"])

def test_main_debug_after_code_raises():
    with pytest.raises(KeyError):
        main(["9mtzma","--debug"])

def test_main_debug_does_not_persist():
    with pytest.raises(KeyError):
        main(["--debug","9mtzma"])
    assert main(["9mtzma"]) == 9

@pytest.mark.parametrize("flag",["-w","--warning"])
def test_main_warning(capsys,flag):
    assert main([flag,CODE]) == 0
    assert capsys.readouterr().out == CODE_OUT

def test_main_does_not_change_warning_filters():
    before = list(warnings.filters)
    main([CODE])
    assert warnings.filters == before
