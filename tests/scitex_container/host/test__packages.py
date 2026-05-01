#!/usr/bin/env python3
# Timestamp: "2026-05-01"
# File: tests/scitex_container/host/test__packages.py
"""Unit tests for scitex_container.host._packages.

check_packages() inspects the host environment for TeX Live and ImageMagick.
The returned shape is fixed regardless of whether the tools are installed.
"""

from __future__ import annotations


class TestCheckPackages:
    """Tests for scitex_container.host.check_packages."""

    def test_returns_dict(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result, dict)

    def test_texlive_key_present(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "texlive" in result

    def test_imagemagick_key_present(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "imagemagick" in result

    def test_texlive_entry_has_installed_key(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "installed" in result["texlive"]

    def test_imagemagick_entry_has_installed_key(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert "installed" in result["imagemagick"]

    def test_installed_field_is_bool(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result["texlive"]["installed"], bool)
        assert isinstance(result["imagemagick"]["installed"], bool)

    def test_binaries_field_is_list(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result["texlive"]["binaries"], list)
        assert isinstance(result["imagemagick"]["binaries"], list)

    def test_version_field_is_string(self):
        from scitex_container.host import check_packages

        result = check_packages()
        assert isinstance(result["texlive"]["version"], str)
        assert isinstance(result["imagemagick"]["version"], str)


# EOF
