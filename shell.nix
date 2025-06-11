{ pkgs ? import <nixpkgs> {} }
:
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [
      traceroute
      ntp
      busybox
    ];
  }