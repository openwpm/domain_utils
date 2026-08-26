from tldextract import TLDExtract

from domain_utils import get_etld1, get_ps_plus_1, get_stripped_url, stem_url


def test_get_ps_plus_1_is_an_alias_for_get_etld1() -> None:
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    assert get_ps_plus_1(url) == get_etld1(url) == 'domain.cloudfront.net'


def test_get_ps_plus_1_forwards_kwargs(custom_extractor: TLDExtract) -> None:
    # The kwarg has to be one that changes the answer: `use_netloc` does not,
    # because get_etld1 discards the port either way.
    url = 'http://a.b.moz.illa/path'
    assert get_ps_plus_1(url, extractor=custom_extractor) == 'b.moz.illa'


def test_get_stripped_url_is_an_alias_for_stem_url() -> None:
    url = 'https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1'
    expected = 'my.domain.cloudfront.net/a/path/to/a/file.html'
    assert get_stripped_url(url) == stem_url(url) == expected


def test_get_stripped_url_forwards_kwargs() -> None:
    url = 'https://my.domain.cloudfront.net/a/path?a=1'
    assert get_stripped_url(url, scheme=True, path=False) == 'https://my.domain.cloudfront.net'
