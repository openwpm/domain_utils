from domain_utils import get_stripped_url


def test_get_stripped_url_params():
    url = 'https://my.domain.cloudfront.net?a=1&b=2'
    result = get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_hash():
    url = 'https://my.domain.cloudfront.net#anchor'
    result = get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_path():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html'
    result = get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_get_stripped_url_no_path_and_drop_non_http_false():
    url = 'https://my.domain.cloudfront.net#anchor'
    result = get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_no_scheme():
    url = 'my.domain.cloudfront.net#anchor'
    result = get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_no_scheme_and_scheme_true():
    url = 'my.domain.cloudfront.net#anchor'
    result = get_stripped_url(url, scheme=True)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_no_scheme_and_drop_non_http_urls_true():
    # Note we assume that empty schemes are http urls
    url = 'my.domain.cloudfront.net#anchor'
    result = get_stripped_url(url, drop_non_http=True)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_path_params():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    result = get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_get_stripped_url_with_hostname_only_and_scheme():
    url = 'https://my.domain.cloudfront.net'
    result = get_stripped_url(url, scheme=True)
    assert result == url


def test_get_stripped_url_non_http_scheme_none():
    url = 'about:blank'
    result = get_stripped_url(url, drop_non_http=True)
    assert result == ''


def test_get_stripped_url_non_http_scheme_return_self():
    url = 'about:blank'
    result = get_stripped_url(url, drop_non_http=False)
    assert result == url


def test_get_stripped_url_returns_port_if_present():
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_get_stripped_url_returns_port_if_present_and_use_netloc_false():
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_get_stripped_with_port_when_no_scheme():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_get_stripped_url_with_port_when_no_scheme_and_use_netloc_false():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_get_stripped_url_with_port_when_no_scheme_and_ip_and_use_netloc_false():
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url, use_netloc=False)
    assert result == '127.0.0.1/path/to/webapp.htm'


def test_get_stripped_url_with_ip_address_when_no_scheme():
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url)
    assert result == '127.0.0.1:8080/path/to/webapp.htm'


def test_get_stripped_url_with_ip_address_and_scheme():
    url = 'http://8.8.8.8:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url)
    assert result == '8.8.8.8:8080/path/to/webapp.htm'
