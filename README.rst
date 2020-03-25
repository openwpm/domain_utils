==============
`domain_utils`
==============


.. image:: https://img.shields.io/pypi/v/domain_utils.svg
        :target: https://pypi.python.org/pypi/domain_utils

.. image:: https://img.shields.io/travis/mozilla/domain_utils.svg
        :target: https://travis-ci.org/mozilla/domain_utils

.. image:: https://readthedocs.org/projects/domain-utils/badge/?version=latest
        :target: https://domain-utils.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


A collection of util functions for extracting domains from urls.

Repo: https://github.com/mozilla/domain_utils

Install::

    pip install domain_utils

Use::

    import domain_utils as du
    # Return just the url `my.domain.cloudfront.net/a/path/to/a/file.html`
    du.get_stripped_url('https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1')
    # Return just the eTLD+1 `domain.cloudfront.net`
    du.get_stripped_url('https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1')


This package was originally extracted from
openwpm-utils_.


* Free software: Mozilla Public License license
* Documentation: https://domain-utils.readthedocs.io.



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _openwpm-utils: https://github.com/mozilla/openwpm-utils/blob/14edefa360c482ffcffdfeddbf09e2372d459f4c/openwpm_utils/domain.py
