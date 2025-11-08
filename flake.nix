{
  description = "Volt Demo";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs { system = system; config.allowUnfree = true; };

        nativeBuildInputs = with pkgs; [
          tailwindcss_4
        ];

        buildInputs = with pkgs; [];
      in {
        devShells.default = pkgs.mkShell {
          name = "volt-demo-shell";

          inherit nativeBuildInputs;
        };
      }
    );
}
