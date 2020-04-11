import pytest
from domain_utils import get_etld1


def test_get_ps_plus_one_cloudfront():
    result = get_etld1('https://my.domain.cloudfront.net')
    assert result == 'domain.cloudfront.net'


def test_get_ps_plus_one_no_https():
    result = get_etld1('my.domain.cloudfront.net')
    assert result == 'domain.cloudfront.net'


def test_get_ps_plus_one_on_about_blank():
    result = get_etld1('about:blank')
    assert result == ''


def test_get_ps_plus_one_on_relative_url():
    assert get_etld1('/my/path/is.html') == ''


def test_when_anchor():
    assert get_etld1('http://www.google.com#anchor') == 'google.com'


def test_get_etld1_on_vanilla_public_suffix():
    assert get_etld1('http://www.google.com') == 'google.com'


def test_get_etld1_on_exotic_public_suffix():
    assert get_etld1('http://foo.bar.website.apartments') == 'website.apartments'


def test_get_etld1_on_data_url():
    assert get_etld1("data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAA") == ''


def test_get_etld1_on_fbsbx_example():
    # apps.fbsbx.com is on the public sufix list (Apr 2, 2020)
    assert get_etld1('http://foo.blah.apps.fbsbx.com') == 'blah.apps.fbsbx.com'
    assert get_etld1('http://foo.blah.www.fbsbx.com') == 'fbsbx.com'


def test_get_etld1_on_ip_addresses():
    assert get_etld1('http://192.168.1.1') == '192.168.1.1'
    assert get_etld1('http://127.0.0.1/foo.html') == '127.0.0.1'


def test_get_etld1_on_url_with_port():
    assert get_etld1('http://my.example.com:8080/path/to/webapp.htm?aced=1') == 'example.com'


def test_extractor_none_raises_an_issue():
    with pytest.raises(ValueError):
        get_etld1('', extractor=None)


def test_extractor_not_tld_extract_instance_raises_an_issue():
    with pytest.raises(ValueError):
        get_etld1('', extractor='astring')


def test_extractor_with_custom_tld_extract_instance_successful(custom_extractor):
    url = 'http://foo.bar.moz.illa/path/to/webapp.htm?aced=1'
    result = get_etld1(url, extractor=custom_extractor)
    assert result == 'bar.moz.illa'


def test_punyencoded_url():
    result = get_etld1('http://xn----7sbi4aadnjoecmhmg9juc.xn--p1ai')
    assert result == 'xn----7sbi4aadnjoecmhmg9juc.xn--p1ai'
