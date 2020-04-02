import pytest
import domain_utils as du


def test_get_ps_plus_one_cloudfront():
    result = du.get_ps_plus_1('https://my.domain.cloudfront.net')
    assert result == 'domain.cloudfront.net'


@pytest.mark.xfail(reason="Currently not supported")
def test_get_ps_plus_one_no_https():
    result = du.get_ps_plus_1('my.domain.cloudfront.net')
    assert result == 'domain.cloudfront.net'


def test_get_stripped_url_params():
    url = 'https://my.domain.cloudfront.net?a=1&b=2'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_hash():
    url = 'https://my.domain.cloudfront.net#anchor'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_path():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_get_stripped_url_no_path_and_drop_non_http_false():
    url = 'https://my.domain.cloudfront.net#anchor'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_no_scheme():
    url = 'my.domain.cloudfront.net#anchor'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_no_scheme_and_scheme_true():
    url = 'my.domain.cloudfront.net#anchor'
    result = du.get_stripped_url(url, scheme=True)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_no_scheme_and_drop_non_http_urls_true():
    # Note we assume that empty schemes are http urls
    url = 'my.domain.cloudfront.net#anchor'
    result = du.get_stripped_url(url, drop_non_http=True)
    assert result == 'my.domain.cloudfront.net'


def test_get_stripped_url_path_params():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_get_stripped_url_with_hostname_only_and_scheme():
    url = 'https://my.domain.cloudfront.net'
    result = du.get_stripped_url(url, scheme=True)
    assert result == url


def test_get_stripped_url_non_http_scheme_none():
    url = 'about:blank'
    result = du.get_stripped_url(url, drop_non_http=True)
    assert result == ''


def test_get_stripped_url_non_http_scheme_return_self():
    url = 'about:blank'
    result = du.get_stripped_url(url, drop_non_http=False)
    assert result == url


def test_get_stripped_url_returns_port_if_present():
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = du.get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_get_stripped_url_returns_port_if_present_and_use_netloc_false():
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = du.get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'
