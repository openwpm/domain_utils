{
  description = "domain_utils - util functions for extracting domains from urls";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # Interpreters the test matrix runs against, oldest first. uv picks
        # one of these up per `uv run --python 3.x`; see UV_PYTHON_* below.
        pythons = with pkgs; [
          python311
          python312
          python313
          python314
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            uv
            # From nixpkgs rather than PyPI: the published ruff wheel is a
            # prebuilt dynamically linked binary that will not run on NixOS.
            ruff
            just
            # nbsphinx shells out to pandoc for the notebook's markdown cells
            pandoc
          ] ++ pythons;

          # uv ships prebuilt CPython builds that assume an FHS layout and so
          # cannot run here. Pin it to the interpreters above instead.
          UV_PYTHON_PREFERENCE = "only-system";
          UV_PYTHON_DOWNLOADS = "never";

          # Let the Makefile use the ruff from this shell instead of the
          # unusable wheel that `uv run ruff` would install.
          RUFF = "ruff";

          # Wheels with compiled extensions (pyzmq, pulled in by nbsphinx)
          # are linked against a generic libstdc++ that is not on the default
          # NixOS search path.
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.zlib
          ];

          shellHook = ''
            echo "domain_utils dev shell - python $(python3 --version 2>&1 | cut -d' ' -f2), uv $(uv --version | cut -d' ' -f2), ruff $(ruff --version | cut -d' ' -f2)"
            echo "  just test | just lint | just docs | just coverage"
          '';
        };

        formatter = pkgs.nixpkgs-fmt;
      });
}
