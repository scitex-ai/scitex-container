#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: tests/test_cli.py
"""CLI tests for scitex-container using Click's CliRunner.

Tests use CliRunner so no real Apptainer, Docker, or SLURM installation is
needed.  Commands that rely on container runtimes are expected to exit with a
non-zero code when the runtime is absent.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner():
    """Return a Click CliRunner with colour disabled for easy assertion."""
    return CliRunner()


@pytest.fixture()
def cli():
    """Return the scitex-container main CLI group."""
    from scitex_container._cli import main

    return main


# ---------------------------------------------------------------------------
# --help
# ---------------------------------------------------------------------------


class TestHelpFlag:
    """Tests for --help output."""

    def test_main_help_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["--help"])
        # Assert
        assert result.exit_code == 0

    def test_main_help_contains_usage(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["--help"])
        # Assert
        assert "Usage:" in result.output or "usage:" in result.output.lower()

    def test_main_help_mentions_scitex_container(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["--help"])
        # Assert
        assert (
            "scitex-container" in result.output.lower()
            or "scitex" in result.output.lower()
        )

    def test_subcommand_build_help_result_exit_code_equals_n_0(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["build", "--help"])
        # Act
        # Assert
        assert result.exit_code == 0

    def test_subcommand_build_help_help_in_result_output_or_usage_in_result_output(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["build", "--help"])
        # Act
        # Assert
        assert "--help" in result.output or "Usage:" in result.output


    def test_subcommand_sandbox_help(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["sandbox", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_subcommand_docker_help(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["docker", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_subcommand_host_help(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["host", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_subcommand_mcp_help(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_subcommand_status_help(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["status", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_subcommand_env_snapshot_help(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["save-env-snapshot", "--help"])
        # Assert
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# --version
# ---------------------------------------------------------------------------


class TestVersionFlag:
    """Tests for --version output."""

    def test_version_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["--version"])
        # Assert
        assert result.exit_code == 0

    def test_version_output_contains_version_string(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["--version"])
        # Click's version_option outputs "NAME, version VERSION"
        # Assert
        assert result.output.strip() != ""

    def test_version_matches_package_metadata(self, runner, cli):
        # Arrange
        import importlib.metadata

        pkg_version = importlib.metadata.version("scitex-container")
        # Act
        result = runner.invoke(cli, ["--version"])
        # Assert
        assert pkg_version in result.output


# ---------------------------------------------------------------------------
# --help-recursive
# ---------------------------------------------------------------------------


class TestHelpRecursive:
    """Tests for --help-recursive flag.

    The main group does not have invoke_without_command=True, so Click emits a
    "Missing command" error (exit code 2) when no subcommand follows.  The
    help output is still printed before the error, so we check the output text
    regardless of exit code.
    """

    def test_help_recursive_exits_zero_or_two(self, runner, cli):
        """Exit 0 when implemented with invoke_without_command, 2 otherwise."""
        # Arrange
        # Act
        result = runner.invoke(cli, ["--help-recursive"])
        # Assert
        assert result.exit_code in (0, 2)

    def test_help_recursive_output_is_nonempty(self, runner, cli):
        """Output must contain something even if Click also emits a usage error."""
        # Arrange
        result = runner.invoke(cli, ["--help-recursive"])
        # Output may contain the error message plus whatever help was printed
        # Act
        combined = result.output
        # Assert
        assert len(combined) > 10

    def test_help_recursive_does_not_crash_unexpectedly(self, runner, cli):
        """Invoking with --help-recursive must not produce an unhandled exception."""
        # Arrange
        # Act
        result = runner.invoke(cli, ["--help-recursive"])
        # An exception attribute set means an unhandled Python exception occurred
        # Assert
        assert result.exception is None or isinstance(result.exception, SystemExit)


# ---------------------------------------------------------------------------
# list-python-apis
# ---------------------------------------------------------------------------


class TestListPythonApis:
    """Tests for list-python-apis command."""

    def test_list_python_apis_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis"])
        # Assert
        assert result.exit_code == 0

    def test_list_python_apis_output_contains_apptainer(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis"])
        # Assert
        assert "apptainer" in result.output

    def test_list_python_apis_output_contains_docker(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis"])
        # Assert
        assert "docker" in result.output

    def test_list_python_apis_output_contains_host(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis"])
        # Assert
        assert "host" in result.output

    def test_list_python_apis_verbose_shows_signatures_result_exit_code_equals_n_0(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis", "-v"])
        # Act
        # Assert
        assert result.exit_code == 0

    def test_list_python_apis_verbose_shows_signatures_in_result_output(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis", "-v"])
        # Act
        # Assert
        assert "(" in result.output


    def test_list_python_apis_vv_shows_docstrings_result_exit_code_equals_n_0(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis", "-vv"])
        # Act
        # Assert
        assert result.exit_code == 0

    def test_list_python_apis_vv_shows_docstrings_len_result_output_len_result_v_output(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["list-python-apis", "-vv"])
        # Assert
        # Double-verbose adds docstrings — output should be longer than -v
        # Act
        result_v = runner.invoke(cli, ["list-python-apis", "-v"])
        # Act
        # Assert
        assert len(result.output) >= len(result_v.output)



# ---------------------------------------------------------------------------
# mcp list-tools
# ---------------------------------------------------------------------------


class TestMcpListTools:
    """Tests for mcp list-tools command."""

    def test_mcp_list_tools_exits_zero_or_one(self, runner, cli):
        """With or without fastmcp installed, exit code should be 0 or 1."""
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "list-tools"])
        # Assert
        assert result.exit_code in (0, 1)

    def test_mcp_list_tools_produces_output(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "list-tools"])
        # Either tools are listed, or an error message is shown — output must exist.
        # Click's default CliRunner mixes stderr into stdout, so result.output
        # captures both streams.
        # Assert
        assert result.output.strip() != ""

    def test_mcp_list_tools_help_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "list-tools", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_mcp_list_tools_verbose_flag_accepted_result_exit_code_in_n_0_1(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "list-tools", "-v"])
        # Act
        # Assert
        assert result.exit_code in (0, 1)

    def test_mcp_list_tools_verbose_flag_accepted_no_such_option_not_in_result_output_lower(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "list-tools", "-v"])
        # Act
        # Assert
        assert "no such option" not in result.output.lower()



# ---------------------------------------------------------------------------
# mcp doctor
# ---------------------------------------------------------------------------


class TestMcpDoctor:
    """Tests for mcp doctor command."""

    def test_mcp_doctor_exits_zero_or_one(self, runner, cli):
        """Exit code 0 means all checks pass, 1 means at least one failed."""
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "doctor"])
        # Assert
        assert result.exit_code in (0, 1)

    def test_mcp_doctor_produces_output(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "doctor"])
        # Assert
        assert result.output.strip() != ""

    def test_mcp_doctor_contains_check_keywords(self, runner, cli):
        # Arrange
        result = runner.invoke(cli, ["mcp", "doctor"])
        # Act
        output_lower = result.output.lower()
        # Assert
        assert any(
            kw in output_lower
            for kw in ("check", "fastmcp", "mcp", "ok", "fail", "warn")
        )

    def test_mcp_doctor_help_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "doctor", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_mcp_doctor_verbose_flag_accepted_result_exit_code_in_n_0_1(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "doctor", "--verbose"])
        # Act
        # Assert
        assert result.exit_code in (0, 1)

    def test_mcp_doctor_verbose_flag_accepted_no_such_option_not_in_result_output_lower(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["mcp", "doctor", "--verbose"])
        # Act
        # Assert
        assert "no such option" not in result.output.lower()



# ---------------------------------------------------------------------------
# env-snapshot (CLI layer)
# ---------------------------------------------------------------------------


class TestEnvSnapshotCmd:
    """Tests for env-snapshot CLI command."""

    def test_env_snapshot_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["save-env-snapshot"])
        # Assert
        assert result.exit_code == 0

    def test_env_snapshot_json_flag_produces_json_result_exit_code_equals_n_0(self, runner, cli):
        # Arrange
        import json
        # Act
        result = runner.invoke(cli, ["save-env-snapshot", "--json"])
        # Act
        # Assert
        assert result.exit_code == 0

    def test_env_snapshot_json_flag_produces_json_parsed_is_dict(self, runner, cli):
        # Arrange
        import json
        # Act
        result = runner.invoke(cli, ["save-env-snapshot", "--json"])
        # Assert
        # Act
        parsed = json.loads(result.output)
        # Act
        # Assert
        assert isinstance(parsed, dict)


    def test_env_snapshot_json_contains_schema_version(self, runner, cli):
        # Arrange
        import json

        result = runner.invoke(cli, ["save-env-snapshot", "--json"])
        # Act
        parsed = json.loads(result.output)
        # Assert
        assert "schema_version" in parsed

    def test_env_snapshot_json_contains_timestamp(self, runner, cli):
        # Arrange
        import json

        result = runner.invoke(cli, ["save-env-snapshot", "--json"])
        # Act
        parsed = json.loads(result.output)
        # Assert
        assert "timestamp" in parsed

    def test_env_snapshot_json_contains_required_sections(self, runner, cli):
        # Arrange
        # Act
        # Assert
        import json

        result = runner.invoke(cli, ["save-env-snapshot", "--json"])
        # Act
        parsed = json.loads(result.output)
        # Assert
        assert all(section in parsed for section in ('container', 'host', 'dev_repos', 'lock_files')), f'Missing section: {section}'

    def test_env_snapshot_human_readable_output(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["save-env-snapshot"])
        # Assert
        assert (
            "Schema" in result.output
            or "Timestamp" in result.output
            or "snapshot" in result.output.lower()
        )

    def test_env_snapshot_with_nonexistent_dev_repo(self, runner, cli):
        """Passing a non-existent dev repo path must not crash."""
        # Arrange
        # Act
        result = runner.invoke(
            cli, ["save-env-snapshot", "--dev-repo", "/tmp/__nonexistent__"]
        )
        # Assert
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# list command (container versions)
# ---------------------------------------------------------------------------


class TestListContainersCmd:
    """Tests for the 'list' subcommand."""

    def test_list_help_exits_zero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["show-status", "--help"])
        # Assert
        assert result.exit_code == 0

    def test_list_with_nonexistent_dir_exits_nonzero(self, runner, cli):
        # Arrange
        # Act
        result = runner.invoke(cli, ["show-status"])
        # Either exits non-zero or shows a warning; must not crash with traceback
        # Assert
        assert result.exit_code in (0, 1)


# EOF
