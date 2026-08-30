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

Then, in the GitHub repository settings, create an environment named ``pypi``.
Restricting that environment to the ``master`` branch and to tags, and adding
required reviewers, means a release cannot be published without a maintainer
approving the deployment.

The workflow requests an OIDC token via ``permissions: id-token: write`` and
exchanges it for a short-lived, project-scoped PyPI credential. See the
`PyPA guide <https://docs.pypi.org/trusted-publishers/>`_ for background.


Cutting a release
-----------------

#. Make sure ``master`` is green, both in
   `CI <https://github.com/openwpm/domain_utils/actions/workflows/ci.yml>`_ and
   on `Read the Docs <https://readthedocs.org/projects/domain-utils/>`_.

#. Add the release notes to ``HISTORY.rst``.

#. Bump ``__version__`` in ``domain_utils/__init__.py``. That is the single
   source of truth for the version; the packaging metadata reads it and the
   release workflow refuses to publish if it disagrees with the tag.

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
