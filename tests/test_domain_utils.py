import pytest
import domain_utils as du


def test_get_ps_plus_one_cloudfront():
    result = du.get_ps_plus_1('https://my.domain.cloudfront.net')
    assert result == 'domain.cloudfront.net'


def test_get_ps_plus_one_no_https():
    result = du.get_ps_plus_1('my.domain.cloudfront.net')
    assert result == 'domain.cloudfront.net'


def test_get_ps_plus_one_on_about_blank():
    result = du.get_ps_plus_1('about:blank')
    assert result is None


def test_get_ps_plus_one_on_relative_url():
    result = du.get_ps_plus_1('/my/path/is.html')
    assert result is None


def test_get_ps_plus_1_on_exotic_public_suffix():
    assert du.get_ps_plus_1('http://foo.bar.website.apartments') == 'website.apartments'


def test_get_ps_plus_1_on_data_url():
    assert du.get_ps_plus_1("data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAA") is None


def test_get_ps_plus_1_on_fbsbx_example():
    # apps.fbsbx.com is on the public sufix list (Apr 2, 2020)
    assert du.get_ps_plus_1('http://foo.blah.apps.fbsbx.com') == 'blah.apps.fbsbx.com'
    assert du.get_ps_plus_1('http://foo.blah.www.fbsbx.com') == 'fbsbx.com'


def test_get_ps_plus_1_on_ip_addresses():
    assert du.get_ps_plus_1('http://192.168.1.1') == '192.168.1.1'
    assert du.get_ps_plus_1('http://127.0.0.1/foo.html') == '127.0.0.1'


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
    result = du.get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


@pytest.mark.xfail(reason=port_no_schema_msg)
def test_get_stripped_url_with_port_when_no_scheme_and_use_netloc_false():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = du.get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_get_stripped_url_document_behavior_with_port_when_no_scheme():
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = du.get_stripped_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = du.get_stripped_url(url, use_netloc=False)
    assert result == 'my.example.com:8080/path/to/webapp.htm?aced=1'

# End of url with port but no scheme
