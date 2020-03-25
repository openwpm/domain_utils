******
`domain_utils` documentation
******

`domain_utils` is a small package for parsing urls.

Repo: https://github.com/mozilla/domain_utils

Install::

    pip install domain_utils

Use::

    import domain_utils as du
    # Return just the url `my.domain.cloudfront.net/a/path/to/a/file.html`
    du.get_stripped_url('https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1')
    # Return just the eTLD+1 `domain.cloudfront.net`
    du.get_stripped_url('https://my.domain.cloudfront.net/a/path/to/a/file.html?a=1')

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   readme
   installation
   modules
   contributing
   history

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
