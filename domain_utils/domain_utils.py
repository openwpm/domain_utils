from collections.abc import Callable
from functools import wraps
from ipaddress import ip_address
from typing import ParamSpec, TypedDict, TypeVar, Unpack
from urllib.parse import urlparse

from tldextract import ExtractResult, TLDExtract

__all__ = [
    'HTTP',
    'HTTPS',
    'NO_SCHEME',
    'WS',
    'WSS',
    'get_etld1',
    'get_port',
    'get_ps_plus_1',
    'get_scheme',
    'get_stripped_url',
    'hostname_subparts',
    'is_ip_address',
    'stem_url',
]

NO_SCHEME = 'no_scheme'
HTTP = 'http'
HTTPS = 'https'
WS = 'ws'
WSS = 'wss'

_P = ParamSpec('_P')
_R = TypeVar('_R')
_T = TypeVar('_T')


class _StemKwargs(TypedDict, total=False):
    """The keyword arguments ``stem_url`` takes.

    Spelled out so that the functions forwarding ``**kwargs`` to it stay
    checkable at their call sites.
    """

    return_unparsed: bool
    scheme_default: str | None
    parse_ws: bool
    scheme: bool
    path: bool
    use_netloc: bool
    extractor: TLDExtract


def _require_extractor(extractor: object) -> TLDExtract:
    if not isinstance(extractor, TLDExtract):
        raise ValueError(
            'A tldextract::TLDExtract instance must be passed using the '
            '`extractor` keyword argument.'
        )
    return extractor


def _load_and_update_extractor(function: Callable[_P, _R]) -> Callable[_P, _R]:
    # Note that omitting `extractor` is not the same as passing None: omitting
    # it asks for the shared extractor built here, while passing None is a
    # choice of extractor, and a bad one, which the callee rejects.
    extractor: TLDExtract | None = None

    @wraps(function)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        nonlocal extractor
        if 'extractor' not in kwargs:
            if extractor is None:
                _extractor = TLDExtract(include_psl_private_domains=True)
                _extractor.update()
                extractor = _extractor
            kwargs['extractor'] = extractor
        return function(*args, **kwargs)

    return wrapper


def is_ip_address(hostname: object) -> bool:
    """
    Check if the given string is a valid IP address
    """
    try:
        ip_address(str(hostname))
        return True
    except ValueError:
        return False


def _adapt_url_for_port_and_scheme(url: str, extractor: TLDExtract | None) -> str:
    # From the docs: "urlparse recognizes a netloc only if it is properly
    # introduced by '//'". A url that carries a host but no scheme is
    # therefore parsed either as a scheme plus a path (`example.com:8080/a`,
    # `localhost:5000`) or as a bare path (`127.0.0.1:8080/a`, because a
    # scheme may not start with a digit). Both shapes lose the host and the
    # port, so we prepend the missing `//` and let urlparse try again.
    purl = urlparse(url)
    _scheme = purl.scheme

    if purl.netloc != '':
        return url

    if _scheme != '':
        # The scheme is only really a host if it looks like one: either
        # everything after the colon is a port (`localhost:5000`), or
        # TLDExtract finds a public suffix in it (`example.com:8080/a`).
        # Note that the extractor is what makes this configurable, so it
        # deliberately gets the final say for anything dotted. It is only
        # required once we get this far.
        if not purl.path.isdigit():
            if '.' not in _scheme or _require_extractor(extractor)(_scheme).suffix == '':
                return url

    url = f'//{url}'
    if urlparse(url).path == '':
        # The url is a bare host, e.g. `localhost:5000`; keep the trailing
        # slash that callers of ``stem_url`` have always been given.
        url = f'{url}/'
    return url


@_load_and_update_extractor
def _get_tld_extract(url: str, **kwargs: Unpack[_StemKwargs]) -> ExtractResult:
    extractor = _require_extractor(kwargs.get('extractor'))

    scheme = kwargs.get('scheme', True)
    path = kwargs.get('path', True)
    return_unparsed = kwargs.get('return_unparsed', False)
    use_netloc = kwargs.get('use_netloc', True)
    scheme_default = kwargs.get('scheme_default', HTTP)
    stemmed = stem_url(
        url,
        return_unparsed=return_unparsed,
        scheme_default=scheme_default,
        scheme=scheme,
        path=path,
        use_netloc=use_netloc,
        extractor=extractor,
    )
    return extractor(stemmed)


def get_etld1(url: str, **kwargs: Unpack[_StemKwargs]) -> str:
    """
    Returns the eTLD+1 (aka PS+1) of the url.

    Parameters
    ----------
    url : string
        The url from which to extract the eTLD+1 / PS+1
    extractor : tldextract::TLDExtract, optional
        An (optional) tldextract::TLDExtract instance can be passed with
        keyword `extractor`, otherwise we create and update one automatically.
    kwargs:
        The method preprocesses the url with ``stem_url`` before
        extracting the domain. You can pass in ``stem_url`` parameters
        if you wish to change the behavior in some specific way.

    Returns
    -------
    string
        The eTLD+1 / PS+1 of the url passed in. If no eTLD+1 is detectable,
        an empty string will be returned. Returns an IP address if the hostname
        of the url is a valid IP address.
    """
    parsed = _get_tld_extract(url, **kwargs)
    if parsed.suffix == '':
        return parsed.domain
    else:
        return f'{parsed.domain}.{parsed.suffix}'


def get_ps_plus_1(url: str, **kwargs: Unpack[_StemKwargs]) -> str:
    """An alias for ``get_etld1``."""
    return get_etld1(url, **kwargs)


@_load_and_update_extractor
def hostname_subparts(
    url: str, include_ps: bool = False, **kwargs: Unpack[_StemKwargs]
) -> list[str]:
    """
    Returns a list of slices of a url's hostname down to the eTLD+1 / PS+1.


    Parameters
    ----------
    url : string
        The url from which to extract the hostname parts
    include_ps : boolean, optional
        If ``include_ps`` is set, the hostname slices will include the public suffix
        For example, ``http://a.b.c.d.com/path?query#frag`` would yield:

        * ``["a.b.c.d.com", "b.c.d.com", "c.d.com", "d.com"]`` if ``include_ps == False``
        * ``["a.b.c.d.com", "b.c.d.com", "c.d.com", "d.com", "com"]`` if ``include_ps == True``
    kwargs:
        Additionally, all kwargs for ``get_etld1`` can be passed to this
        method.

    Returns
    -------
    list (string)
        List of slices of of a url's hostname down to the eTLD+1 / PS+1.
    """
    ext = _get_tld_extract(url, **kwargs)
    etld1 = get_etld1(url, **kwargs)

    # If an IP address, just return a single item list with the IP
    if is_ip_address(ext.domain):
        return [ext.domain]

    # We expect all eTLD+1s to have at least one '.'
    # If they don't, the url was likely malformed, so we'll just
    # return an empty list
    if '.' not in etld1:
        return []

    # Build a string of the URL except the suffix
    domain_less_ps = '.'.join(
        [url_part for url_part in [ext.subdomain, ext.domain] if url_part != '']
    )

    # Assemble subparts list
    subparts: list[str] = []

    if domain_less_ps != '':
        domain_parts_to_pop = list(reversed(domain_less_ps.split('.')))
        while len(domain_parts_to_pop) > 0:
            domain_parts = [*reversed(domain_parts_to_pop), ext.suffix]
            subparts.append('.'.join(domain_parts))
            domain_parts_to_pop.pop()

    if include_ps:
        subparts.append(ext.suffix)

    return subparts


@_load_and_update_extractor
def stem_url(
    url: str,
    return_unparsed: bool = True,
    scheme_default: str | None = HTTP,
    parse_ws: bool = True,
    scheme: bool = False,
    path: bool = True,
    use_netloc: bool = True,
    extractor: TLDExtract | None = None,
) -> str:
    """
    Returns a url stripped to just the beginning and end.

    More formally it returns ``(scheme)?+(netloc|hostname)+(path)?``.

    For example ``https://my.domain.net/a/path/to/a/file.html#anchor?a=1``
    becomes ``my.domain.net/a/path/to/a/file.html``
    URL parsing is done using std lib
    `urllib.parse.urlparse
    <https://docs.python.org/3.8/library/urllib.parse.html>`_.

    A url is parsed if it has a qualifying scheme. The qualifying schemes are
    ``http``, ``https``, ``ws`` and ``wss``. Websocket schemes can be omitted using
    the ``parse_ws`` parameter. Additionally, the ``scheme_default`` parameter
    provides a scheme where the url doesn't contain one. The default is ``http``
    and so urls without a scheme will, by default, be considered as http and therefore
    parsed.

    What is returned for unparsed urls is determined by the ``return_unparsed``
    parameter.

    Parameters
    ----------
    url : string
        The URL to be parsed
    return_unparsed : boolean, optional
        Action to take if scheme is not parsed e.g. ``file:`` or ``about:blank``.
        If ``False``, the result for non parsed urls will be an empty string
        If ``True``, the result will be the original url, e.g.
        ``about:blank`` -> ``about:blank`` even if ``scheme=False``.
        See method description to understand whether a URL is parsed or not.
        Default is ``True``.
    scheme_default : string, optional
        This parameter is passed to scheme parameter of `urllib.parse.urlparse`. This
        causes urls without a scheme to return the scheme default.
        Default is ``http``.
    parse_ws : boolean, optional
        If ``True``, then ``ws`` and ``wss`` urls are parsed.
        Default is ``True``.
    scheme : boolean, optional
        If ``True``, scheme will be prepended in parsed result.
        Default is ``False``.
    path : boolean, optional
        If ``True``, path will be included in parsed result.
        Default is ``True``.
    use_netloc : boolean, optional
        If ``True`` urlparse's netloc will be used.
        If ``False`` urlparse's host will be returned. Using netloc means
        that a port is included, for example, if it was in the path.
        Default is ``True``.
    extractor : tldextract::TLDExtract, optional
        An (optional) tldextract::TLDExtract instance can be passed with
        keyword `extractor`, otherwise we create and update one automatically.

    Returns
    -------
    string
        Returns a url stripped to (scheme)?+(netloc|hostname)+(path)?.
        Returns empty string if appropriate.
    """
    if scheme_default is None:
        # `urlparse` raises on a None scheme before Python 3.14. An empty
        # scheme means the same thing here: do not assume one.
        scheme_default = ''

    purl = urlparse(_adapt_url_for_port_and_scheme(url, extractor), scheme=scheme_default)
    _scheme = purl.scheme

    # Will we parse
    schemes_to_parse = [HTTP, HTTPS]
    if parse_ws is True:
        schemes_to_parse += [WS, WSS]
    if _scheme not in schemes_to_parse:
        if return_unparsed is True:
            # The url as the caller gave it to us, not as we adapted it.
            return url
        return ''

    scheme_out = ''
    loc_out: str | None = ''
    path_out = ''

    if scheme is True:
        # No need to re-check the scheme: anything unparseable returned above.
        scheme_out = f'{_scheme}://'

    if path is True:
        path_out = purl.path

    if use_netloc is True:
        loc_out = purl.netloc
    else:
        loc_out = purl.hostname

    return f'{scheme_out}{loc_out}{path_out}'


def get_stripped_url(url: str, **kwargs: Unpack[_StemKwargs]) -> str:
    """Alias for ``stem_url``."""
    return stem_url(url, **kwargs)


def get_scheme(url: str, no_scheme: _T = NO_SCHEME) -> str | _T:
    """
    Given a url, extract from it the scheme.

    Parameters
    ----------
    url: string
        The URL from where we want to get the scheme
    no_scheme: any
        The value to use if no scheme is detected.
        Default is ``no_scheme``

    Returns
    -------
    string
        Returns the scheme with a default of ``no_scheme`` if no scheme
        is provided
    """

    scheme = urlparse(url).scheme

    if scheme:
        return scheme
    else:
        return no_scheme


@_load_and_update_extractor
def get_port(url: str, extractor: TLDExtract | None = None) -> int | None:
    """
    Given a url, extract from it the port if present.

    Parameters
    ----------
    url: string
        The URL from where we want to get the port
    extractor : tldextract::TLDExtract, optional
        An (optional) tldextract::TLDExtract instance can be passed with
        keyword `extractor`, otherwise we create and update one automatically.

    Returns
    ----------
    int
        Returns port in the url. If port not found, returns ``None``.
    """

    url = _adapt_url_for_port_and_scheme(url, extractor)
    return urlparse(url).port
