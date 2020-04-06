from functools import wraps
from ipaddress import ip_address
from tldextract import TLDExtract
from urllib.parse import urlparse


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


@_load_and_update_extractor
def _get_tld_extract(url, **kwargs):
    extractor = kwargs.get('extractor')
    if not isinstance(extractor, TLDExtract):
        raise ValueError(
            "A tldextract::TLDExtract instance must be passed using the "
            "`extractor` keyword argument.")

    scheme = kwargs.get('scheme', True)
    drop_non_http = kwargs.get('drop_non_http', True)
    use_netloc = kwargs.get('use_netloc', True)
    stripped = get_stripped_url(
            url,
            scheme=scheme,
            drop_non_http=drop_non_http,
            use_netloc=use_netloc,
    )
    return extractor(stripped)


def get_ps_plus_1(url, **kwargs):
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
        The method preprocesses the url with ``get_stripped_url`` before
        extracting the domain. You can pass in ``get_stripped_url`` parameters
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
        For example: ``http://a.b.c.d.com/path?query#frag`` would yield:

        * ``["a.b.c.d.com", "b.c.d.com", "c.d.com", "d.com"]`` if ``include_ps == False``
        * ``["a.b.c.d.com", "b.c.d.com", "c.d.com", "d.com", "com"]`` if ``include_ps == True``
    kwargs:
        Additionally all kwargs for get_ps_plus_1, can be passed to this method.

    Returns
    -------
    list (string)
        List of slices of of a url's hostname down to the eTLD+1 / PS+1.
    """
    ext = _get_tld_extract(url, **kwargs)
    ps_plus_1 = get_ps_plus_1(url, **kwargs)

    # If an IP address, just return a single item list with the IP
    if is_ip_address(ext.domain):
        return [ext.domain]

    # We expect all ps_plus_1s to have at least one '.'
    # If they don't, the url was likely malformed, so we'll just
    # return an empty list
    if '.' not in ps_plus_1:
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
def get_stripped_url(url, scheme=False, drop_non_http=False, use_netloc=True, extractor=None):
    """
    Returns a url stripped to just the beginning and end.

    More formally it returns ``(scheme)?+(netloc|hostname)+(path)?``.

    For example ``https://my.domain.net/a/path/to/a/file.html#anchor?a=1``
    becomes ``my.domain.net/a/path/to/a/file.html``
    URL parsing is done using std lib
    `urllib.parse.urlparse
    <https://docs.python.org/3.8/library/urllib.parse.html>`_.

    Empty scheme e.g. ``my.domain.cloudfront.net``
    are assumed to be http schemes.

    If a URL has a port but no scheme, urlparse determines the scheme to
    be the hostname and we do not handle this special case. In this case,
    the url will be treated as a non-http scheme and the return value will
    be determined by the ``drop_non_http`` setting.

    Parameters
    ----------
    url : string
        The URL to be parsed
    scheme : boolean, optional
        If ``True``, scheme will be prepended in returned result.
        Default is ``False``.
    drop_non_http : boolean, optional
        Action to take if scheme is not
        ``http`` or ``https`` e.g. ``file:`` or ``about:blank``.
        If ``True``, the result for non http urls will be an empty string
        If ``False``, the result for non http urls will be the original url,
        not further processed e.g. ``about:blank`` -> ``about:blank`` even
        if ``scheme=False``. The result for http urls will be the stripped
        url with or without the scheme as per scheme param.
        Default is ``False``.
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
    purl = urlparse(url)
    _scheme = purl.scheme

    # To handle the case where we have no scheme, but we have a port
    # we have the following heuristic. Does scheme have a . in it
    # which is stdlib behavior when not recognizing a netloc due to
    # lack of //. If TLDExtract, can find a suffix in the _scheme
    # then it's probably a domain without an http.
    if '.' in _scheme:
        # From the docs: "urlparse recognizes a netloc only
        # if it is properly introduced by ‘//’". So we
        # prepend to get results we expect.
        if extractor(_scheme).suffix != '' or is_ip_address(_scheme):
            url = '//{url}'.format(url=url)

    purl = urlparse(url)
    _scheme = purl.scheme

    # Handle non http schemes
    if _scheme not in ['http', 'https', '']:
        if drop_non_http is True:
            return ''
        else:
            return url

    purl = urlparse(url)
    scheme_out = ''
    loc_out = ''
    path_out = purl.path

    if scheme is True:
        if _scheme in ['http', 'https']:
            scheme_out = '{scheme}://'.format(scheme=_scheme)

    if use_netloc is True:
        loc_out = purl.netloc
    else:
        loc_out = purl.hostname

    return '{scheme_out}{loc_out}{path_out}'.format(
        scheme_out=scheme_out,
        loc_out=loc_out,
        path_out=path_out,
    )
