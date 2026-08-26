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

Report bugs at https://github.com/openwpm/domain_utils/issues.

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

The best way to send feedback is to file an issue at https://github.com/openwpm/domain_utils/issues.

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

   If you use nix, on any operating system, there is a ``shell.nix`` providing
   just_, uv, ruff and the supported interpreters; ``nix-shell`` (or
   ``direnv allow``) drops you into it. It is what CI uses, so the tooling
   matches exactly. nixpkgs is pinned with npins_; ``npins update``
   refreshes it.

   The shell pins uv to the interpreters from nixpkgs and points ``RUFF`` and
   ``PYRIGHT`` at the nixpkgs binaries. That is required on NixOS, where uv's
   prebuilt CPython downloads and the published ruff and pyright wheels assume
   an FHS layout and will not run; elsewhere it simply keeps your versions the
   same as CI's.

4. Install the pre-commit_ hooks::

    $ just hooks

   They run ruff and pyright over the Python, alejandra_ over the Nix and
   actionlint_ (which delegates the workflows' ``run:`` blocks to shellcheck_)
   over the GitHub Actions workflows. Every hook is ``language: system``, so it uses
   the tool from your environment rather than installing its own; the
   ``nix-shell`` above provides all of them.

5. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

6. When you're done making changes, check that your changes pass the linter and
   the tests::

    $ just ci

   That is the single command CI runs, so a red build reproduces locally. The
   individual steps are available too; ``just`` on its own lists them all::

    $ just lint
    $ just typecheck
    $ just test

   ``just test`` fails if coverage drops below 100%. ``just format`` applies
   the fixes the linter can make on its own. ``just typecheck`` runs pyright_
   in strict mode over both the package and the tests; the package ships a
   ``py.typed`` marker, so its annotations are part of its public interface.

   To test against another interpreter::

    $ just test-python 3.11

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

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
.. _npins: https://github.com/andir/npins
.. _pre-commit: https://pre-commit.com/
.. _alejandra: https://github.com/kamadorueda/alejandra
.. _actionlint: https://github.com/rhysd/actionlint
.. _shellcheck: https://www.shellcheck.net/
.. _pyright: https://microsoft.github.io/pyright/
.. _just: https://just.systems/


Deploying
---------

See `the release process <docs/release.rst>`_.
