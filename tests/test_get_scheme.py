from domain_utils import get_scheme, NO_SCHEME


def test_no_scheme():
    result = get_scheme("domain.net")
    assert result == NO_SCHEME


def test_file():
    result = get_scheme("file:///home/user/index.html")
    assert result == 'file'


def test_https():
    result = get_scheme("https://domain.net")
    assert result == 'https'


def test_http():
    result = get_scheme("http://domain.net")
    assert result == 'http'


def test_about():
    result = get_scheme("about:config")
    assert result == 'about'


def test_webpack():
    result = get_scheme("webpack://index.js")
    assert result == 'webpack'


def test_empty():
    result = get_scheme("")
    assert result == NO_SCHEME


def test_ws():
    result = get_scheme("ws://socket")
    assert result == 'ws'


def test_pass_custom_empty_value():
    assert get_scheme('10.0.0.1/path/to/index.html', no_scheme=None) is None
