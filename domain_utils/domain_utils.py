from functools import wraps
from ipaddress import ip_address
from tldextract import TLDExtract
from urllib.parse import urlparse


def load_and_update_extractor(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'extractor' not in kwargs:
            if wrapper.extractor is None:
                extractor = TLDExtract(include_psl_private_domains=True)
                extractor.update()
                wrapper.extractor = extractor
            return function(*args, extractor=wrapper.extractor, **kwargs)
        else:
            return function(*args, extractor=wrapper.extractor, **kwargs)
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


@load_and_update_extractor
def get_ps_plus_1(url, extractor=None, **kwargs):
    """
    Returns the eTLD+1 (aka PS+1) of the url. This will also return
    an IP address if the hostname of the url is a valid IP address.

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
        an empty string will be returned.
    """
    if extractor is None:
        raise ValueError(
            "A tldextract::TLDExtract instance must be passed using the "
            "`extractor` keyword argument.")

    scheme = kwargs.get('scheme', True)
    drop_non_http = kwargs.get('drop_non_http', True)
    use_netloc = kwargs.get('use_netloc', True)
    include_path = kwargs.get('include_path', False)
    stripped = get_stripped_url(
            url,
            scheme=scheme,
            drop_non_http=drop_non_http,
            use_netloc=use_netloc,
            include_path=include_path,
    )
    if stripped == '':
        return ''
    parsed = extractor(stripped)
    if is_ip_address(parsed.domain):
        return parsed.domain
    else:
        return f'{parsed.domain}.{parsed.suffix}'


@load_and_update_extractor
def hostname_subparts(url, include_ps=False, **kwargs):
    """
    Returns a list of slices of a url's hostname down to the PS+1
    If `include_ps` is set, the hostname slices will include the public suffix
    For example: http://a.b.c.d.com/path?query#frag would yield:
        [a.b.c.d.com, b.c.d.com, c.d.com, d.com] if include_ps == False
        [a.b.c.d.com, b.c.d.com, c.d.com, d.com, com] if include_ps == True
    An (optional) PublicSuffixList object can be passed with keyword arg 'psl'.
    otherwise a version cached in the system temp directory is used.
    """
    if 'psl' not in kwargs:
        raise ValueError(
            "A PublicSuffixList must be passed as a keyword argument.")
    hostname = urlparse(url).hostname

    # If an IP address, just return a single item list with the IP
    if is_ip_address(hostname):
        return [hostname]

    subparts = list()
    ps_plus_1 = kwargs['psl'].get_public_suffix(hostname)

    # We expect all ps_plus_1s to have at least one '.'
    # If they don't, the url was likely malformed, so we'll just return an
    # empty list
    if '.' not in ps_plus_1:
        return []
    subdomains = hostname[:-(len(ps_plus_1)+1)].split('.')
    if subdomains == ['']:
        subdomains = []
    for i in range(len(subdomains)):
        subparts.append('.'.join(subdomains[i:])+'.'+ps_plus_1)
    subparts.append(ps_plus_1)
    if include_ps:
        try:
            subparts.append(ps_plus_1[ps_plus_1.index('.')+1:])
        except Exception:
            pass
    return subparts


def get_stripped_url(url, scheme=False, drop_non_http=False, use_netloc=True, include_path=True):
    """
    Returns a url stripped to just the beginning and end, or more formally,
    ``(scheme)?+(netloc|hostname)+(path)?``.
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
    :param url: URL to be parsed
    :type url: str
    :param scheme: If ``True``, scheme will be prepended in
        returned result. Defaults is ``False``.
    :type scheme: bool, optional
    :param drop_non_http: Action to take if scheme is not
        ``http`` or ``https`` e.g. ``file:`` or ``about:blank``.
        If ``True``, the result for non http urls will be an empty string
        If ``False``, the result for non http urls will be the original url,
        not further processed e.g. ``about:blank`` -> ``about:blank`` even
        if ``scheme=False``. The result for http urls will be the stripped
        url with or without the scheme as per scheme param.
        Default is ``False``.
    :type drop_non_http: bool, optional
    :param use_netloc: If ``True`` urlparse's netloc will be used.
        If ``False`` urlparse's host will be returned. Using netloc means
        that a port is included, for example, if it was in the path.
        Default is ``True``.
    :type use_netloc: bool, optional
    :param include_path: If ``True`` return value will include the 
        url path. Default is ``True``.
    :type include_path: bool, optional
    :return: Returns a url stripped to (scheme)?+(netloc|hostname)+(path)?.
        Returns empty string if appropriate.
    :rtype: str
    """
    purl = urlparse(url)
    _scheme = purl.scheme

    # Handle non http schemes
    if _scheme not in ['http', 'https', '']:
        if drop_non_http is True:
            return ''
        if drop_non_http is False:
            return url

    if _scheme == '':
        # From the docs: "urlparse recognizes a netloc only
        # if it is properly introduced by ‘//’". So we
        # prepend to get results we expect.
        url = '//{url}'.format(url=url)

    purl = urlparse(url)
    scheme_out = ''
    loc_out = ''
    path_out = ''

    if scheme is True:
        if _scheme in ['http', 'https']:
            scheme_out = '{scheme}://'.format(scheme=_scheme)
        else:
            # Should only get here if scheme is ''
            scheme_out = '{scheme}'.format(scheme=_scheme)

    if use_netloc is True:
        loc_out = purl.netloc
    else:
        loc_out = purl.hostname

    if include_path is True:
        path_out = purl.path

    return '{scheme_out}{loc_out}{path_out}'.format(
        scheme_out=scheme_out,
        loc_out=loc_out,
        path_out=path_out,
    )
