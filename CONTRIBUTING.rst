.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/mozilla/domain_utils/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Domain Utils could always use more documentation, whether as part of the
official Domain Utils docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/mozilla/domain_utils/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `domain_utils` for local development.

1. Fork the `domain_utils` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/domain_utils.git

3. Set up the development environment. The project uses uv_ for dependency
   management::

    $ cd domain_utils/
    $ just install-dev

   On NixOS there is a flake providing uv, ruff and the supported
   interpreters; ``nix develop`` (or ``direnv allow``) drops you into it.
   The flake pins uv to the interpreters from nixpkgs, because uv's own
   prebuilt CPython downloads assume an FHS layout and will not run.

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass the linter and
   the tests::

    $ just lint
    $ just test

   ``just test`` fails if coverage drops below 100%. ``just format`` applies
   the fixes the linter can make on its own.

   To test against another interpreter, pass it to uv::

    $ uv run --python 3.11 --group test pytest

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for every supported Python version. CI runs the
   suite against all of them; check
   https://github.com/openwpm/domain_utils/actions.

Tips
----

To run a subset of tests::

$ just test tests/test_get_port.py

``just test`` does not measure coverage, so a subset run is not failed by a
whole-suite gate. ``just coverage`` runs everything under the gate, which is
what CI enforces.

.. _uv: https://docs.astral.sh/uv/


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags

Travis will then deploy to PyPI if tests pass.
