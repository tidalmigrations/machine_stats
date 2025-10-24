{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          venvDir = "./.venv";
          buildInputs = with pkgs.${system}; [
            # A Python interpreter including the 'venv' module is required to bootstrap
            # the environment.
            python3Packages.python
            python3Packages.pytest
            python3Packages.pluggy

            # This execute some shell code to initialize a venv in $venvDir before
            # dropping into the shell
            python3Packages.venvShellHook
            python3Packages.python-lsp-server
            # In this particular example, in order to compile any binary extensions they may
            # require, the Python modules listed in the hypothetical requirements.txt need
            # the following packages to be installed locally:
            python3Packages.wheel
            python3Packages.setuptools
            libvirt
          ];

          # Run this command, only after creating the virtual environment
          postVenvCreation = ''
            unset SOURCE_DATE_EPOCH
            pip install -r ./requirements.txt
            pip install -r dev-requirements.txt
            pip install -e .
          '';

          # Now we can execute any commands within the virtual environment.
          # This is optional and can be left out to run pip manually.
          postShellHook = ''
            # allow pip to install wheels
            unset SOURCE_DATE_EPOCH
          '';
        };
      });
    };
}
