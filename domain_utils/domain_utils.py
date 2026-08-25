from functools import wraps
from ipaddress import ip_address
from tldextract import TLDExtract
from urllib.parse import urlparse

NO_SCHEME = 'no_scheme'
HTTP = 'http'
HTTPS = 'https'
WS = 'ws'
WSS = 'wss'


def _load_and_update_extractor(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'extractor' not in kwargs:
            if wrapper.extractor is None:
                _extractor = TLDExtract(include_psl_private_domains=True)
                _extractor.update()
                wrapper.extractor = _extractor
            return function(*args, extractor=wrapper.extractor, **kwargs)
        else:
            return function(*args, **kwargs)
    wrapper.extractor = None
    return wrapper


def is_ip_address(hostname):
    """
    Check if the given string is a valid IP address
    """
    try:
        ip_address(str(hostname))
        return True
    except ValueError:
        return False


def _adapt_url_for_port_and_scheme(url, extractor):
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
        # deliberately gets the final say for anything dotted.
        if not purl.path.isdigit():
            if '.' not in _scheme or extractor(_scheme).suffix == '':
                return url

    url = '//{url}'.format(url=url)
    if urlparse(url).path == '':
        # The url is a bare host, e.g. `localhost:5000`; keep the trailing
        # slash that callers of ``stem_url`` have always been given.
        url = '{url}/'.format(url=url)
    return url


@_load_and_update_extractor
def _get_tld_extract(url, **kwargs):
    extractor = kwargs.get('extractor')
    if not isinstance(extractor, TLDExtract):
        raise ValueError(
            "A tldextract::TLDExtract instance must be passed using the "
            "`extractor` keyword argument.")

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


def get_etld1(url, **kwargs):
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


def get_ps_plus_1(url, **kwargs):
    """An alias for ``get_etld1``."""
    return get_etld1(url, **kwargs)


@_load_and_update_extractor
def hostname_subparts(url, include_ps=False, **kwargs):
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
    domain_less_ps = '.'.join([
        url_part for url_part
        in [ext.subdomain, ext.domain]
        if url_part != ''
    ])

    # Assemble subparts list
    subparts = []

    if domain_less_ps != '':
        domain_parts_to_pop = list(reversed(domain_less_ps.split('.')))
        while len(domain_parts_to_pop) > 0:
            domain_parts = list(reversed(domain_parts_to_pop)) + [ext.suffix]
            subparts.append('.'.join(domain_parts))
            domain_parts_to_pop.pop()

    if include_ps:
        subparts.append(ext.suffix)

    return subparts


@_load_and_update_extractor
def stem_url(
        url,
        return_unparsed=True,
        scheme_default=HTTP,
        parse_ws=True,
        scheme=False,
        path=True,
        use_netloc=True,
        extractor=None):
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
    loc_out = ''
    path_out = ''

    if scheme is True:
        if _scheme in schemes_to_parse:
            scheme_out = '{scheme}://'.format(scheme=_scheme)

    if path is True:
        path_out = purl.path

    if use_netloc is True:
        loc_out = purl.netloc
    else:
        loc_out = purl.hostname

    return '{scheme_out}{loc_out}{path_out}'.format(
        scheme_out=scheme_out,
        loc_out=loc_out,
        path_out=path_out,
    )


def get_stripped_url(url, **kwargs):
    """Alias for ``stem_url``."""
    return stem_url(url, **kwargs)


def get_scheme(url, no_scheme=NO_SCHEME):
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
def get_port(url, extractor=None):
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
