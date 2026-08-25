=======
History
=======

0.8.0 (unreleased)
------------------

* Relax the ``tldextract`` pin from ``==2.2.2`` to ``>=5.3`` (#32). The
  pinned version cached the public suffix list inside its own installed package
  directory and refreshed it with an unguarded check-then-act, so any consumer
  running more than one process could race and lose data. Upstream moved the
  cache out of the package directory in 3.1.0.
* Drop support for Python 3.6 to 3.10; the minimum is now 3.11.
* Replace CircleCI with GitHub Actions (#31).
* The test suite now fails below 100% statement and branch coverage (#27).
* Fix url parsing on modern CPython. ``urlparse`` no longer refuses to read
  ``host:port`` as a scheme, which meant ``localhost:8000`` and
  ``example.com:8080`` lost their port, and ``127.0.0.1:8080/a?b=1`` lost its
  host entirely.
* Fix ``scheme_default=None``, which raised ``AttributeError`` on Python 3.11
  to 3.13 because ``urlparse`` gained WHATWG scheme stripping.
* ``stem_url`` now returns the url exactly as it was passed in when
  ``return_unparsed`` is set and the scheme is not parsed, rather than an
  internally rewritten form.
* ``stem_url`` no longer appends a stray trailing slash to a scheme-less url
  that already has a path, e.g. ``10.0.0.1:80/a/b.html``. A scheme-less bare
  host, e.g. ``example.com``, still gets one.


0.7.1 (2020-04-10)
------------------

Fix building on readthedocs.


0.7.0 (2020-04-10)
------------------

Thanks to new contributor @yabirgb for two PRs (#20 and #25) in this release.

API changes: #26 renamed `get_stripped_url` to `stem_url`, and `get_ps_plus_1`
to `get_etld1`. Old method names will continue to work though. #22 updated
keyword arguments to `get_stripped_url` - default behavior is basically the same.

* API changes (#26 and #22)
* Support parsing ws/wss urls (#22)
* Add get_port method (#25)
* Add get_scheme method (#20)
* Correct license declaration in setup.py (#24)


0.6.0 (2020-04-06)
------------------

* Use tldextract for parsing domains (#12)
* Use numpy style docstrings
* Support case of no scheme and port in URL (#13)


0.5.0 (2020-04-03)
------------------

* Remove support for python 3.5
* Handle more cases in get_stripped_url and change default behavior:

  - handle a lack of scheme
  - boolean flag to return or not non http urls - default is to
    return them which is a change of behavior as previously they
    would not return
  - Use netloc by default instead of hostname with a boolean flag
    to use hostname.

0.4.0 (2020-03-25)
------------------

* Remove py27 support

0.3.0 (2020-03-25)
------------------

* Restore py27 support.
* Last version with py27 support.
* Remove tox


0.2.0 (2020-03-24)
------------------

* Extracted from https://github.com/mozilla/openwpm-utils/blob/master/openwpm_utils/domain.py
* Removed python 2 support and dependencies
* Removed broken get_stripped_urls function
* First release on PyPI.
