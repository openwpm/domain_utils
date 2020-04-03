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


def test_get_stripped_url_path_params():
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    result = du.get_stripped_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'
