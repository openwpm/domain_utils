"""
This file exists solely to be an intermediary between the python tests
and the js script.

"""
import subprocess

HTTP = 'http'


def get_etld1(url,
        return_unparsed=True,
        scheme_default=HTTP,
        parse_ws=True,
        scheme=False,
        path=True,
        use_netloc=True,
        extractor=None
    ):
    proc = subprocess.run([
        "npm",
        "run",
        "get_etld1",
        url,
        f"return_unparsed={return_unparsed}",
        f"scheme_default={scheme_default}",
        f"parse_ws={parse_ws}",
        f"scheme={scheme}",
        f"path={path}",
        #f"use_netloc={use_netloc}", -- option not supported
        #f"extractor={extractor}", -- option not supported
    ], capture_output=True)
    return proc.stdout.decode().split('\n')[-2]


def stem_url(url,
        return_unparsed=True,
        scheme_default=HTTP,
        parse_ws=True,
        scheme=False,
        path=True,
        use_netloc=True,
        extractor=None
    ):
    proc = subprocess.run([
        "npm",
        "run",
        "stem_url",
        url,
        f"return_unparsed={return_unparsed}",
        f"scheme_default={scheme_default}",
        f"parse_ws={parse_ws}",
        f"scheme={scheme}",
        f"path={path}",
        #f"use_netloc={use_netloc}", -- option not supported
        #f"extractor={extractor}", -- option not supported
    ], capture_output=True)
    return proc.stdout.decode().split('\n')[-2]



# Aliases


def get_ps_plus_1(url, **kwargs):
    return get_etld1(url, **kwargs)


def get_stripped_url(url, **kwargs):
    return stem_url(url, **kwargs)
