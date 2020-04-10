from domain_utils import stem_url


def test_params():
    url = 'https://my.domain.cloudfront.net?a=1&b=2'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_hash():
    url = 'https://my.domain.cloudfront.net#anchor'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_path():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_no_path_and_drop_non_http_false():
    url = 'https://my.domain.cloudfront.net#anchor'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_no_scheme():
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_no_scheme_and_scheme_true():
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url, scheme=True)
    assert result == 'http://my.domain.cloudfront.net'


def test_no_scheme_and_scheme_true_default_scheme_none():
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url, scheme=True, scheme_default=None)
    # This returns the original URL because only http and https schemes
    # are parsed and the scheme_default was changed to None
    assert result == 'my.domain.cloudfront.net#anchor'


def test_no_scheme_and_drop_non_http_urls_true():
    # Note we assume that empty schemes are http urls
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url, return_unparsed=False)
    assert result == 'my.domain.cloudfront.net'


def test_path_params():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_with_hostname_only_and_scheme():
    url = 'https://my.domain.cloudfront.net'
    result = stem_url(url, scheme=True)
    assert result == url


def test_non_http_scheme_none():
    url = 'about:blank'
    result = stem_url(url, return_unparsed=False)
    assert result == ''


def test_non_http_scheme_return_self():
    url = 'about:blank'
    result = stem_url(url, return_unparsed=True)
    assert result == url


def test_returns_port_if_present():
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_returns_port_if_present_and_use_netloc_false():
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_get_stripped_with_port_when_no_scheme():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_with_port_when_no_scheme_and_use_netloc_false():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_with_port_when_no_scheme_and_ip_and_use_netloc_false():
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url, use_netloc=False)
    assert result == '127.0.0.1/path/to/webapp.htm'


def test_with_ip_address_when_no_scheme():
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == '127.0.0.1:8080/path/to/webapp.htm'


def test_with_ip_address_and_scheme():
    url = 'http://8.8.8.8:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == '8.8.8.8:8080/path/to/webapp.htm'


def test_with_no_scheme_return_scheme_and_parsed_non_default_scheme():
    url = 'domain.com/path?a=1'
    result = stem_url(url, scheme=True, scheme_default='https')
    assert result == 'https://domain.com/path'


def test_with_no_scheme_and_not_parsed_non_default_scheme():
    url = 'domain.com/path?a=1'
    result = stem_url(url, scheme_default='wont_parse')
    assert result == 'domain.com/path?a=1'


def test_ws_urls_parsed_by_default():
    url = 'ws://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url)
    assert result == 'domain.com:8080/path/to/test.html'


def test_wss_urls_parsed_by_default():
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url)
    assert result == 'domain.com:8080/path/to/test.html'


def test_wss_urls_with_scheme_true():
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url, scheme=True)
    assert result == 'wss://domain.com:8080/path/to/test.html'


def test_wss_urls_not_parsed_if_requested():
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url, parse_ws=False)
    assert result == 'wss://domain.com:8080/path/to/test.html?a=1&b=2'


def test_return_path_false():
    url = 'http://localhost/path/to?a=1&b=2'
    result = stem_url(url, path=False)
    assert result == 'localhost'


def test_return_path_false_scheme_true():
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url, path=False, scheme=True)
    assert result == 'wss://domain.com:8080'
