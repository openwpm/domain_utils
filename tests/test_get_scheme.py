import pytest
from domain_utils import get_scheme



def test_get_scheme_no_scheme():
    result = get_scheme("domain.net")
    assert result == 'blank'

def test_get_scheme_file():
    result = get_scheme("file:///home/user/index.html")
    assert result == 'file'
    
def test_get_scheme_https():
    result = get_scheme("https://domain.net")
    assert result == 'https'
    
def test_get_scheme_http():
    result = get_scheme("http://domain.net")
    assert result == 'http'
    
def test_get_scheme_about():
    result = get_scheme("about:config")
    assert result == 'about'

def test_get_scheme_webpack():
    result = get_scheme("webpack://index.js")
    assert result == 'webpack'

def test_get_scheme_empty():
    result = get_scheme("")
    assert result == 'blank'
    

def test_get_scheme_ws():
    result = get_scheme("ws://socket")
    assert result == 'ws'
