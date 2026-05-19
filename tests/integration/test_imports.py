#!/usr/bin/env python3
"""Basic import tests for scitex-container."""


def test_import_package_hasattr_scitex_container_version():
    # Arrange
    # Act
    import scitex_container

    # Assert
    assert hasattr(scitex_container, "__version__")


def test_import_submodules_apptainer_is_not_none():
    # Arrange
    # Act
    from scitex_container import apptainer, docker, host
    # Act
    # Assert
    assert apptainer is not None


def test_import_submodules_docker_is_not_none():
    # Arrange
    # Act
    from scitex_container import apptainer, docker, host
    # Act
    # Assert
    assert docker is not None


def test_import_submodules_host_is_not_none():
    # Arrange
    # Act
    from scitex_container import apptainer, docker, host
    # Act
    # Assert
    assert host is not None




def test_import_env_snapshot():
    # Arrange
    # Act
    from scitex_container import env_snapshot

    # Assert
    assert callable(env_snapshot)


def test_import_verify_callable_verify():
    # Arrange
    # Act
    from scitex_container.apptainer import verify

    # Assert
    assert callable(verify)


def test_cli_entry_point():
    # Arrange
    # Act
    from scitex_container._cli import main

    # Assert
    assert main is not None


# EOF
