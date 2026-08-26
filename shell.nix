{
  sources ? import ./npins,
  pkgs ? import sources.nixpkgs {},
}: let
  # Interpreters the test matrix runs against, oldest first. uv picks
  # one of these up per `uv run --python 3.x`; see UV_PYTHON_* below.
  pythons = with pkgs; [
    python311
    python312
    python313
    python314
  ];
in
  pkgs.mkShell {
    # The interpreters come first so that `python3` is the oldest supported one
    # rather than whichever interpreter a tool below happens to drag in.
    packages =
      pythons
      ++ (with pkgs; [
        uv
        # From nixpkgs rather than PyPI: the published ruff wheel is a
        # prebuilt dynamically linked binary that will not run on NixOS.
        ruff
        just
        # nbsphinx shells out to pandoc for the notebook's markdown cells
        pandoc
        # uv downloads wheels over https; `nix-shell --pure` points SSL_CERT_FILE
        # at a file that does not exist, so ship a trust store of our own.
        cacert

        # The pre-commit hooks are all `language: system`, so every tool they
        # shell out to has to come from here. actionlint delegates the `run:`
        # blocks of a workflow to shellcheck when it can find it on PATH.
        pre-commit
        actionlint
        shellcheck
        alejandra
        # Same story as ruff: the published pyright wheel downloads a node
        # binary at run time, so take the wrapped one from nixpkgs instead.
        pyright
      ]);

    # uv ships prebuilt CPython builds that assume an FHS layout and so
    # cannot run here. Pin it to the interpreters above instead.
    UV_PYTHON_PREFERENCE = "only-system";
    UV_PYTHON_DOWNLOADS = "never";

    # Let the justfile use the ruff and pyright from this shell instead of the
    # unusable wheels that `uv run` would install.
    RUFF = "ruff";
    PYRIGHT = "pyright";

    SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";

    # Wheels with compiled extensions (pyzmq, pulled in by nbsphinx)
    # are linked against a generic libstdc++ that is not on the default
    # NixOS search path.
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
    ];

    shellHook = ''
      echo "domain_utils dev shell - python $(python3 --version 2>&1 | cut -d' ' -f2), uv $(uv --version | cut -d' ' -f2), ruff $(ruff --version | cut -d' ' -f2)"
      echo "  just ci | just test | just lint | just typecheck | just --list"
    '';
  }
