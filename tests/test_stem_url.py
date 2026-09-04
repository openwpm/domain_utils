import inspect

from domain_utils import stem_url
from domain_utils.domain_utils import (
    _StemKwargs,  # pyright: ignore[reportPrivateUsage]
)


def test_params() -> None:
    url = 'https://my.domain.cloudfront.net?a=1&b=2'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_hash() -> None:
    url = 'https://my.domain.cloudfront.net#anchor'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_path() -> None:
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_no_path_and_drop_non_http_false() -> None:
    url = 'https://my.domain.cloudfront.net#anchor'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_no_scheme() -> None:
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net'


def test_no_scheme_and_scheme_true() -> None:
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url, scheme=True)
    assert result == 'http://my.domain.cloudfront.net'


def test_no_scheme_and_scheme_true_default_scheme_none() -> None:
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url, scheme=True, scheme_default=None)
    # This returns the original URL because only http and https schemes
    # are parsed and the scheme_default was changed to None
    assert result == 'my.domain.cloudfront.net#anchor'


def test_no_scheme_and_drop_non_http_urls_true() -> None:
    # Note we assume that empty schemes are http urls
    url = 'my.domain.cloudfront.net#anchor'
    result = stem_url(url, return_unparsed=False)
    assert result == 'my.domain.cloudfront.net'


def test_path_params() -> None:
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    result = stem_url(url)
    assert result == 'my.domain.cloudfront.net/a/path/to/a/file.html'


def test_with_hostname_only_and_scheme() -> None:
    url = 'https://my.domain.cloudfront.net'
    result = stem_url(url, scheme=True)
    assert result == url


def test_non_http_scheme_none() -> None:
    url = 'about:blank'
    result = stem_url(url, return_unparsed=False)
    assert result == ''


def test_non_http_scheme_return_self() -> None:
    url = 'about:blank'
    result = stem_url(url, return_unparsed=True)
    assert result == url


def test_returns_port_if_present() -> None:
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_returns_port_if_present_and_use_netloc_false() -> None:
    url = 'http://my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_get_stripped_with_port_when_no_scheme() -> None:
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == 'my.example.com:8080/path/to/webapp.htm'


def test_with_port_when_no_scheme_and_use_netloc_false() -> None:
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url, use_netloc=False)
    assert result == 'my.example.com/path/to/webapp.htm'


def test_with_port_when_no_scheme_and_ip_and_use_netloc_false() -> None:
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url, use_netloc=False)
    assert result == '127.0.0.1/path/to/webapp.htm'


def test_with_ip_address_when_no_scheme() -> None:
    url = '127.0.0.1:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == '127.0.0.1:8080/path/to/webapp.htm'


def test_with_ip_address_and_scheme() -> None:
    url = 'http://8.8.8.8:8080/path/to/webapp.htm?aced=1'
    result = stem_url(url)
    assert result == '8.8.8.8:8080/path/to/webapp.htm'


def test_with_no_scheme_return_scheme_and_parsed_non_default_scheme() -> None:
    url = 'domain.com/path?a=1'
    result = stem_url(url, scheme=True, scheme_default='https')
    assert result == 'https://domain.com/path'


def test_with_no_scheme_and_not_parsed_non_default_scheme() -> None:
    url = 'domain.com/path?a=1'
    result = stem_url(url, scheme_default='wont_parse')
    assert result == 'domain.com/path?a=1'


def test_ws_urls_parsed_by_default() -> None:
    url = 'ws://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url)
    assert result == 'domain.com:8080/path/to/test.html'


def test_wss_urls_parsed_by_default() -> None:
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url)
    assert result == 'domain.com:8080/path/to/test.html'


def test_wss_urls_with_scheme_true() -> None:
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url, scheme=True)
    assert result == 'wss://domain.com:8080/path/to/test.html'


def test_wss_urls_not_parsed_if_requested() -> None:
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url, parse_ws=False)
    assert result == 'wss://domain.com:8080/path/to/test.html?a=1&b=2'


def test_return_path_false() -> None:
    url = 'http://localhost/path/to?a=1&b=2'
    result = stem_url(url, path=False)
    assert result == 'localhost'


def test_return_path_false_scheme_true() -> None:
    url = 'wss://domain.com:8080/path/to/test.html?a=1&b=2'
    result = stem_url(url, path=False, scheme=True)
    assert result == 'wss://domain.com:8080'


def test_bare_host_keeps_trailing_slash() -> None:
    assert stem_url('my.domain.cloudfront.net') == 'my.domain.cloudfront.net/'


def test_unparsed_returns_the_original_url_not_an_adapted_one() -> None:
    url = 'my.example.com:8080/path/to/webapp.htm?aced=1'
    assert stem_url(url, scheme_default='wont_parse') == url


def test_stem_kwargs_matches_stem_url_signature() -> None:
    # _StemKwargs restates stem_url's keyword parameters so the functions that
    # forward **kwargs to it stay checkable. Nothing in the language binds the
    # two together, so pin them here: every keyword-only parameter, and no
    # other, must appear in the TypedDict.
    keyword_only = {
        name
        for name, parameter in inspect.signature(stem_url).parameters.items()
        if parameter.kind is inspect.Parameter.KEYWORD_ONLY
    }
    assert keyword_only == set(_StemKwargs.__annotations__)
