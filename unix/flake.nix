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
                    uv.enable = true;
                  };
                  # This is your devenv configuration
                  packages = with pkgs; [
                    python3Packages.python-lsp-server
                  ];

                  enterShell = ''
                    unset SOURCE_DATE_EPOCH
                    python --version
                  '';
                })
              ];
            };
          });
    };
}
