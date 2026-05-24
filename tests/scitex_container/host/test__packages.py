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

    def test_returns_dict_result_is_dict(self):
        # Arrange
        from scitex_container.host import check_packages

        # Act
        result = check_packages()
        # Assert
        assert isinstance(result, dict)

    def test_texlive_key_present(self):
        # Arrange
        from scitex_container.host import check_packages

        # Act
        result = check_packages()
        # Assert
        assert "texlive" in result

    def test_imagemagick_key_present(self):
        # Arrange
        from scitex_container.host import check_packages

        # Act
        result = check_packages()
        # Assert
        assert "imagemagick" in result

    def test_texlive_entry_has_installed_key(self):
        # Arrange
        from scitex_container.host import check_packages

        # Act
        result = check_packages()
        # Assert
        assert "installed" in result["texlive"]

    def test_imagemagick_entry_has_installed_key(self):
        # Arrange
        from scitex_container.host import check_packages

        # Act
        result = check_packages()
        # Assert
        assert "installed" in result["imagemagick"]

    def test_installed_field_is_bool_isinstance_result_texlive_installed_bool(self):
        # Arrange
        from scitex_container.host import check_packages
        # Act
        result = check_packages()
        # Act
        # Assert
        assert isinstance(result["texlive"]["installed"], bool)

    def test_installed_field_is_bool_isinstance_result_imagemagick_installed_bool(self):
        # Arrange
        from scitex_container.host import check_packages
        # Act
        result = check_packages()
        # Act
        # Assert
        assert isinstance(result["imagemagick"]["installed"], bool)


    def test_binaries_field_is_list_isinstance_result_texlive_binaries_list(self):
        # Arrange
        from scitex_container.host import check_packages
        # Act
        result = check_packages()
        # Act
        # Assert
        assert isinstance(result["texlive"]["binaries"], list)

    def test_binaries_field_is_list_isinstance_result_imagemagick_binaries_list(self):
        # Arrange
        from scitex_container.host import check_packages
        # Act
        result = check_packages()
        # Act
        # Assert
        assert isinstance(result["imagemagick"]["binaries"], list)


    def test_version_field_is_string_isinstance_result_texlive_version_str(self):
        # Arrange
        from scitex_container.host import check_packages
        # Act
        result = check_packages()
        # Act
        # Assert
        assert isinstance(result["texlive"]["version"], str)

    def test_version_field_is_string_isinstance_result_imagemagick_version_str(self):
        # Arrange
        from scitex_container.host import check_packages
        # Act
        result = check_packages()
        # Act
        # Assert
        assert isinstance(result["imagemagick"]["version"], str)



# EOF
