from domain_utils.domain_utils import _adapt_url_for_port_and_scheme


def test_url_no_scheme_port(extractor):
    url = 'domain.com:8080/path/to/test.html?a=1&b=2'
    result = _adapt_url_for_port_and_scheme(url, extractor=extractor)
    assert result == '//domain.com:8080/path/to/test.html?a=1&b=2'


def test_url_no_scheme_port_no_path(extractor):
    url = 'domain.com:8080'
    result = _adapt_url_for_port_and_scheme(url, extractor=extractor)
    assert result == '//domain.com:8080/'


def test_typical_url_with_custom_extractor(custom_extractor):
    url = 'http://foo.bar.moz.illa/path/to/webapp.htm?aced=1'
    result = _adapt_url_for_port_and_scheme(url, extractor=custom_extractor)
    assert result == 'http://foo.bar.moz.illa/path/to/webapp.htm?aced=1'


def test_scenario_with_custom_extractor(custom_extractor):
    # Custom extractor only comes into play when we have no scheme
    # and a port and in that case the extractor is used to look at the
    # suffix to see if we think we have a regular URL. We contrive
    # the following examples to test the behavior. Note that
    # the custom extractor has only one publix suffix in it
    # `moz.illa`
    url = 'domain.com:8080/path/to/test.html?a=1&b=2'
    result = _adapt_url_for_port_and_scheme(url, extractor=custom_extractor)
    # The url has not been parsed because of our custom public suffix list
    assert result == 'domain.com:8080/path/to/test.html?a=1&b=2'


def test_url_no_scheme_port_and_ip(extractor):
    # An ip address can never be parsed as a scheme, so this url reaches
    # urlparse as a bare path.
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = _adapt_url_for_port_and_scheme(url, extractor=extractor)
    assert result == '//127.0.0.1:8080/path/to/webapp.htm?aced=1'


def test_url_single_label_host_with_port(extractor):
    url = 'localhost:8000'
    result = _adapt_url_for_port_and_scheme(url, extractor=extractor)
    assert result == '//localhost:8000/'


def test_url_with_netloc_is_left_alone(extractor):
    url = 'https://domain.com:8080/path?a=1'
    assert _adapt_url_for_port_and_scheme(url, extractor=extractor) == url


def test_non_http_scheme_is_left_alone(extractor):
    # `data` and `ws` are both public suffixes, so they must not be mistaken
    # for hosts.
    for url in ['about:blank', 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP', 'file:///tmp/a']:
        assert _adapt_url_for_port_and_scheme(url, extractor=extractor) == url
