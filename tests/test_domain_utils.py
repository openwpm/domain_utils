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


def test_get_stripped_url_path_params():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'
