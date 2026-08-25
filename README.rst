==============
`domain_utils`
==============


.. image:: https://img.shields.io/pypi/v/domain_utils.svg
        :target: https://pypi.python.org/pypi/domain_utils

.. image:: https://github.com/openwpm/domain_utils/actions/workflows/ci.yml/badge.svg
        :target: https://github.com/openwpm/domain_utils/actions/workflows/ci.yml
        :alt: CI

.. image:: https://readthedocs.org/projects/domain-utils/badge/?version=latest
        :target: https://domain-utils.readthedocs.io/en/latest/
        :alt: Documentation Status


A collection of util functions for extracting domains from urls.

Repo: https://github.com/openwpm/domain_utils

Install::

    pip install domain-utils

Use::

    import domain_utils as du
    # Return just the url `my.domain.cloudfront.net/a/path/to/a/file.html`
    du.stem_url('https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1')
    # Return just the eTLD+1 `domain.cloudfront.net`
    du.get_etld1('https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1')
    # Get the port `5000`
    du.get_port('https://localhost:5000/a/path/to/a/file.html?a=1')
    # Get the scheme `wss`
    du.get_scheme('wss://somedomain.example.com/a/path/to/a/ws')


This package was originally extracted from
openwpm-utils_.


* Free software: Mozilla Public License license
* Documentation: https://domain-utils.readthedocs.io.


Community Participation Guidelines
----------------------------------

This project is governed by Mozilla's code of conduct and etiquette guidelines. 

For more details, please read the `Mozilla Community Participation Guidelines`_. 

For more information on how to report violations of the Community Participation Guidelines, please read our `How to Report`_ page.


.. _openwpm-utils: https://github.com/mozilla/openwpm-utils/blob/14edefa360c482ffcffdfeddbf09e2372d459f4c/openwpm_utils/domain.py
.. _`Mozilla Community Participation Guidelines`: https://www.mozilla.org/about/governance/policies/participation/
.. _`How to Report`: https://www.mozilla.org/about/governance/policies/participation/reporting/
