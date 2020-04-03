import pytest
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


###############################################
# Currently don't support urls with a port but no scheme in the way we want.
#
# url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
# ParseResult(
#       scheme='my.example.com',
#       netloc='',
#       path='8080/path/to/webapp.htm', .....
#
# The following are two tests xfailed with expected behavior and one test
# that documents the actual behavior
###############################################

port_no_schema_msg = """
urlparse does not have a good way to handle a url with a port but no scheme."""


@pytest.mark.xfail(reason=port_no_schema_msg)
def test_get_stripped_with_port_when_no_scheme():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


@pytest.mark.xfail(reason=port_no_schema_msg)
def test_get_stripped_url_with_port_when_no_scheme_and_use_netloc_false():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_get_stripped_url_document_behavior_with_port_when_no_scheme():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com:8080/path/to/webapp.htm?aced=1'

# End of url with port but no scheme


def test_get_stripped_url_when_no_path_requested():
    url = 'my.example.com/path/to/webapp.htm?aced=1'
    result = get_stripped_url(url, include_path=False)
    assert result == 'my.example.com'
