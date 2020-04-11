=======
History
=======

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
