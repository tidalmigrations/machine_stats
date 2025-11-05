{
  inputs = {
    nixpkgs.url = "github:cachix/devenv-nixpkgs/rolling";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    devenv.inputs.nixpkgs.follows = "nixpkgs";
  };

  nixConfig = {
    extra-trusted-public-keys = " devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw= ";
    extra-substituters = " https://devenv.cachix.org ";
  };

  outputs = { self, nixpkgs, devenv, systems, ... } @ inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      devShells = forEachSystem
        (system:
          let
            pkgs = nixpkgs.legacyPackages.${system};
          in
          {
            default = devenv.lib.mkShell {
              inherit inputs pkgs;
              modules = [
                ({ pkgs, config, ... }: {
                  languages.python = {
                    enable = true;
                    package = pkgs.python314;
                    venv.enable = true;
                  };
                  # This is your devenv configuration
                  packages = with pkgs; [
                    python3Packages.venvShellHook
                    python3Packages.python-lsp-server
                    python3Packages.pluggy
                    python3Packages.wheel
                    python3Packages.setuptools
                    pipenv
                    libvirt
                  ];

                  enterShell = ''
                    unset SOURCE_DATE_EPOCH
                    pip install -r ./requirements.txt
                    pip install -r dev-requirements.txt
                    pip install -e .
                    python --version
                  '';
                })
              ];
            };
          });
    };
}
