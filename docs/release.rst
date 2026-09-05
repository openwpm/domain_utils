====================
PyPI Release Process
====================

Releases are cut by pushing a ``v``-prefixed tag. The
``.github/workflows/release.yml`` workflow builds the distributions, checks
them, installs the wheel and runs the test suite against it, publishes to PyPI
and then creates the GitHub release. Nothing is uploaded by hand, and no PyPI
credentials exist anywhere in the repository.


One-time setup: trusted publishing
----------------------------------

PyPI is configured to trust this repository's release workflow directly, so
there is no API token to store or rotate. A maintainer with owner rights on the
`domain-utils PyPI project <https://pypi.org/manage/project/domain-utils/settings/publishing/>`_
adds a *pending* or *existing* GitHub publisher with:

============================  ==============================
Owner                         ``openwpm``
Repository name               ``domain_utils``
Workflow name                 ``release.yml``
Environment name              ``pypi``
============================  ==============================

Then, in the GitHub repository settings, create an environment named ``pypi``
and restrict it to the ``v*`` *tag* pattern, with required reviewers. A branch
rule would be dead weight: the workflow only triggers on a tag push, so a
branch can never reach the publish job. The required reviewer is what makes a
release wait for a maintainer to approve the deployment.

Create it before the first tag. GitHub silently creates an environment that a
workflow names but that does not exist, with no protection rules at all, so a
release succeeding is not by itself evidence that the gate is in place.

The workflow requests an OIDC token via ``permissions: id-token: write`` and
exchanges it for a short-lived, project-scoped PyPI credential. See the
`PyPA guide <https://docs.pypi.org/trusted-publishers/>`_ for background.


Cutting a release
-----------------

#. Make sure ``master`` is green, both in
   `CI <https://github.com/openwpm/domain_utils/actions/workflows/ci.yml>`_ and
   on `Read the Docs <https://readthedocs.org/projects/domain-utils/>`_. CI is
   a single ``just ci`` inside the nix shell, so you can run the same thing
   locally:

    .. code-block:: bash

        nix-shell --run 'just ci'

#. Add the release notes to ``HISTORY.rst``, under the existing
   ``0.8.0 (unreleased)`` heading.

#. Set the version and date the changelog:

    .. code-block:: bash

        just bump 0.8.0

   That rewrites ``__version__`` in ``domain_utils/__init__.py`` and turns
   ``0.8.0 (unreleased)`` into ``0.8.0 (<today>)``. ``__version__`` is the
   single source of truth for the version: the packaging metadata reads it,
   and the release workflow refuses to publish if it disagrees with the tag
   or if the changelog section is still undated. The changelog is part of
   the published description, so an undated heading would be the first thing
   on the PyPI page. The check is ``just check-version v0.8.0``, which
   ``just bump`` runs for you.

#. Commit and push both changes:

    .. code-block:: bash

        git commit -am "Release 0.8.0"
        git push

#. Tag and push the tag:

    .. code-block:: bash

        git tag -a v0.8.0 -m "v0.8.0"
        git push origin v0.8.0

#. Approve the ``pypi`` deployment when the workflow asks for it, if required
   reviewers are configured.

#. Check the `PyPI listing <https://pypi.org/project/domain-utils/>`_ renders
   correctly, and activate the new version on
   `Read the Docs <https://readthedocs.org/projects/domain-utils/versions/>`_.


If the release fails
--------------------

PyPI will not accept a re-upload of a version it already has, so a broken
release cannot be fixed in place. Bump to the next patch version, tag again,
and yank the bad release on PyPI.
