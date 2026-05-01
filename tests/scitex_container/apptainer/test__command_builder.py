#!/usr/bin/env python3
# Timestamp: "2026-03-14"
# File: tests/test_command_builder.py
"""Unit tests for scitex_container.apptainer._command_builder.

All functions tested here are pure command-string builders that produce
deterministic output from their inputs.  No actual Apptainer or SLURM
installation is required.
"""

from __future__ import annotations

from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cb():
    """Import shortcut for the module under test."""
    from scitex_container.apptainer import _command_builder as cb

    return cb


# ---------------------------------------------------------------------------
# build_dev_pythonpath
# ---------------------------------------------------------------------------


class TestBuildDevPythonpath:
    """Tests for build_dev_pythonpath."""

    def test_empty_list_returns_empty_string(self):
        cb = _cb()
        result = cb.build_dev_pythonpath([])
        assert result == ""

    def test_single_repo(self):
        cb = _cb()
        dev_repos = [
            {"name": "scitex-python", "host_path": "/home/user/proj/scitex-python"}
        ]
        result = cb.build_dev_pythonpath(dev_repos)
        assert result == "/opt/dev/scitex-python/src"

    def test_multiple_repos_colon_separated(self):
        cb = _cb()
        dev_repos = [
            {"name": "repo-a", "host_path": "/home/user/proj/repo-a"},
            {"name": "repo-b", "host_path": "/home/user/proj/repo-b"},
        ]
        result = cb.build_dev_pythonpath(dev_repos)
        parts = result.split(":")
        assert len(parts) == 2
        assert "/opt/dev/repo-a/src" in parts
        assert "/opt/dev/repo-b/src" in parts

    def test_src_layout_paths(self):
        """Each repo path must end in /src (src-layout convention)."""
        cb = _cb()
        dev_repos = [{"name": "myrepo", "host_path": "/somewhere/myrepo"}]
        result = cb.build_dev_pythonpath(dev_repos)
        assert result.endswith("/src")

    def test_repo_name_used_not_host_path(self):
        """The container path uses repo['name'], not repo['host_path']."""
        cb = _cb()
        dev_repos = [{"name": "cool-lib", "host_path": "/totally/different/path"}]
        result = cb.build_dev_pythonpath(dev_repos)
        assert "cool-lib" in result
        assert "/totally/different/path" not in result


# ---------------------------------------------------------------------------
# build_host_mount_binds
# ---------------------------------------------------------------------------


class TestBuildHostMountBinds:
    """Tests for build_host_mount_binds."""

    def test_no_args_returns_empty_list(self):
        cb = _cb()
        result = cb.build_host_mount_binds()
        assert result == []

    def test_none_args_returns_empty_list(self):
        cb = _cb()
        result = cb.build_host_mount_binds(host_mounts=None, texlive_prefix="")
        assert result == []

    def test_single_host_mount(self):
        cb = _cb()
        host_mounts = [
            {"host_path": "/data/shared", "container_path": "/mnt/shared", "mode": "ro"}
        ]
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        assert "--bind" in result
        assert "/data/shared:/mnt/shared:ro" in result

    def test_host_mount_produces_alternating_pairs(self):
        """Result should alternate --bind / spec."""
        cb = _cb()
        host_mounts = [{"host_path": "/src", "container_path": "/dst", "mode": "rw"}]
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        assert result[0] == "--bind"
        assert result[1] == "/src:/dst:rw"

    def test_multiple_host_mounts(self):
        cb = _cb()
        host_mounts = [
            {"host_path": "/a", "container_path": "/ca", "mode": "ro"},
            {"host_path": "/b", "container_path": "/cb", "mode": "rw"},
        ]
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Each mount produces 2 elements
        assert len(result) == 4
        assert result.count("--bind") == 2

    def test_texlive_prefix_generates_share_binds(self):
        """Providing texlive_prefix should produce share/texlive bind entries."""
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        specs = [
            result[i + 1] for i in range(0, len(result), 2) if result[i] == "--bind"
        ]
        share_specs = [s for s in specs if "share" in s]
        assert share_specs, "Expected at least one share/ bind for texlive_prefix=/usr"

    def test_texlive_prefix_generates_binary_binds(self):
        """Providing texlive_prefix should produce binary bind entries."""
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        specs = [
            result[i + 1] for i in range(0, len(result), 2) if result[i] == "--bind"
        ]
        bin_specs = [s for s in specs if "/bin/" in s]
        assert bin_specs, "Expected at least one /bin/ bind for texlive_prefix=/usr"

    def test_texlive_prefix_trailing_slash_stripped(self):
        """Trailing slash on prefix must not appear doubled in paths."""
        cb = _cb()
        result_with = cb.build_host_mount_binds(texlive_prefix="/usr/")
        result_without = cb.build_host_mount_binds(texlive_prefix="/usr")
        assert result_with == result_without

    def test_texlive_all_bind_args_start_with_double_dash_bind(self):
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        for i in range(0, len(result), 2):
            assert result[i] == "--bind", (
                f"Expected '--bind' at index {i}, got {result[i]!r}"
            )

    def test_texlive_specs_are_readonly(self):
        """TeX Live bind entries must use :ro mode."""
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        specs = [
            result[i + 1] for i in range(0, len(result), 2) if result[i] == "--bind"
        ]
        for spec in specs:
            assert spec.endswith(":ro"), f"Expected :ro suffix on spec: {spec!r}"


# ---------------------------------------------------------------------------
# build_exec_args
# ---------------------------------------------------------------------------


class TestBuildExecArgs:
    """Tests for build_exec_args."""

    def _call(self, **kwargs):
        cb = _cb()
        defaults = dict(
            container_path="/opt/scitex/scitex.sif",
            username="alice",
            host_user_dir=Path("/home/alice"),
            host_project_dir=Path("/data/proj/myproject"),
            project_slug="myproject",
        )
        defaults.update(kwargs)
        return cb.build_exec_args(**defaults)

    def test_returns_list(self):
        result = self._call()
        assert isinstance(result, list)

    def test_starts_with_apptainer_exec(self):
        result = self._call()
        assert result[0] == "apptainer"
        assert result[1] == "exec"

    def test_containall_present(self):
        result = self._call()
        assert "--containall" in result

    def test_cleanenv_present(self):
        result = self._call()
        assert "--cleanenv" in result

    def test_writable_tmpfs_present(self):
        result = self._call()
        assert "--writable-tmpfs" in result

    def test_hostname_set_to_scitex_cloud(self):
        result = self._call()
        idx = result.index("--hostname")
        assert result[idx + 1] == "scitex-cloud"

    def test_container_path_is_last(self):
        """Container path must be the last positional argument."""
        container = "/opt/scitex/scitex.sif"
        result = self._call(container_path=container)
        assert result[-1] == container

    def test_username_in_env(self):
        result = self._call(username="bob")
        env_pairs = self._extract_env_pairs(result)
        assert env_pairs.get("USER") == "bob"
        assert env_pairs.get("LOGNAME") == "bob"
        assert env_pairs.get("SCITEX_USER") == "bob"

    def test_project_slug_in_env(self):
        result = self._call(project_slug="cool-proj")
        env_pairs = self._extract_env_pairs(result)
        assert env_pairs.get("SCITEX_PROJECT") == "cool-proj"

    def test_home_bind_mount(self):
        """--home <host_user_dir>:/home/<username> must appear."""
        result = self._call(username="alice", host_user_dir=Path("/home/alice"))
        idx = result.index("--home")
        home_spec = result[idx + 1]
        assert home_spec.startswith("/home/alice")
        assert ":/home/alice" in home_spec

    def test_project_bind_mount(self):
        result = self._call(
            username="alice",
            host_project_dir=Path("/data/proj/myproject"),
            project_slug="myproject",
        )
        bind_specs = self._extract_bind_specs(result)
        project_bind = [s for s in bind_specs if "myproject" in s]
        assert project_bind, "Expected a --bind spec containing the project slug"
        assert ":rw" in project_bind[0]

    def test_dev_repos_add_bind_mounts(self):
        dev_repos = [{"name": "mylib", "host_path": "/home/alice/proj/mylib"}]
        result = self._call(dev_repos=dev_repos)
        bind_specs = self._extract_bind_specs(result)
        dev_bind = [s for s in bind_specs if "/opt/dev/mylib" in s]
        assert dev_bind, "Expected a --bind spec for dev repo mounted at /opt/dev/mylib"

    def test_dev_repos_add_pythonpath_env(self):
        dev_repos = [{"name": "mylib", "host_path": "/home/alice/proj/mylib"}]
        result = self._call(dev_repos=dev_repos)
        env_pairs = self._extract_env_pairs(result)
        assert "PYTHONPATH" in env_pairs
        assert "mylib" in env_pairs["PYTHONPATH"]

    def test_no_dev_repos_no_pythonpath(self):
        result = self._call(dev_repos=None)
        env_pairs = self._extract_env_pairs(result)
        assert "PYTHONPATH" not in env_pairs

    def test_scitex_cloud_env_is_true(self):
        result = self._call()
        env_pairs = self._extract_env_pairs(result)
        assert env_pairs.get("SCITEX_CLOUD") == "true"

    def test_shell_env_is_bash(self):
        result = self._call()
        env_pairs = self._extract_env_pairs(result)
        assert env_pairs.get("SHELL") == "/bin/bash"

    def test_pwd_set_to_project_dir(self):
        result = self._call(username="alice", project_slug="myproject")
        idx = result.index("--pwd")
        pwd_val = result[idx + 1]
        assert "myproject" in pwd_val
        assert pwd_val.startswith("/home/alice")

    # ---- helpers ----

    @staticmethod
    def _extract_env_pairs(args: list[str]) -> dict[str, str]:
        """Extract KEY=VALUE pairs from --env arguments."""
        pairs: dict[str, str] = {}
        for i, token in enumerate(args):
            if token == "--env" and i + 1 < len(args):
                raw = args[i + 1]
                if "=" in raw:
                    k, v = raw.split("=", 1)
                    pairs[k] = v
        return pairs

    @staticmethod
    def _extract_bind_specs(args: list[str]) -> list[str]:
        """Extract all spec strings following --bind."""
        specs: list[str] = []
        for i, token in enumerate(args):
            if token == "--bind" and i + 1 < len(args):
                specs.append(args[i + 1])
        return specs


# ---------------------------------------------------------------------------
# build_sbatch_command
# ---------------------------------------------------------------------------


class TestBuildSbatchCommand:
    """Tests for build_sbatch_command."""

    def _call(self, **kwargs):
        cb = _cb()
        defaults = dict(
            instance_name="scitex-alice-myproj",
            script_path="/tmp/start_instance.sh",
            slurm_partition="compute",
            slurm_time_limit="8:00:00",
            slurm_cpus=4,
            slurm_memory_gb=16,
            username="alice",
            project_slug="myproj",
        )
        defaults.update(kwargs)
        return cb.build_sbatch_command(**defaults)

    def test_starts_with_sbatch(self):
        result = self._call()
        assert result[0] == "sbatch"

    def test_parsable_flag(self):
        result = self._call()
        assert "--parsable" in result

    def test_partition_arg(self):
        result = self._call(slurm_partition="gpu")
        assert "--partition=gpu" in result

    def test_time_limit_arg(self):
        result = self._call(slurm_time_limit="2:00:00")
        assert "--time=2:00:00" in result

    def test_cpus_arg(self):
        result = self._call(slurm_cpus=8)
        assert "--cpus-per-task=8" in result

    def test_memory_arg(self):
        result = self._call(slurm_memory_gb=32)
        assert "--mem=32G" in result

    def test_job_name_includes_username_and_slug(self):
        result = self._call(username="alice", project_slug="myproj")
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        assert job_name_args
        assert "alice" in job_name_args[0]
        assert "myproj" in job_name_args[0]

    def test_job_name_falls_back_to_instance_name_when_no_username(self):
        result = self._call(username="", instance_name="my-instance")
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        assert job_name_args
        assert "my-instance" in job_name_args[0]

    def test_output_is_dev_null(self):
        result = self._call()
        assert "--output=/dev/null" in result

    def test_script_path_is_last(self):
        result = self._call(script_path="/tmp/myscript.sh")
        assert result[-1] == "/tmp/myscript.sh"

    def test_returns_list_of_strings(self):
        result = self._call()
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)


# ---------------------------------------------------------------------------
# build_shell_in_allocation_command
# ---------------------------------------------------------------------------


class TestBuildShellInAllocationCommand:
    """Tests for build_shell_in_allocation_command."""

    def _call(self, **kwargs):
        cb = _cb()
        defaults = dict(
            job_id="12345",
            instance_name="scitex-alice-myproj",
            username="alice",
        )
        defaults.update(kwargs)
        return cb.build_shell_in_allocation_command(**defaults)

    def test_starts_with_srun(self):
        result = self._call()
        assert result[0] == "srun"

    def test_pty_flag(self):
        result = self._call()
        assert "--pty" in result

    def test_overlap_flag(self):
        result = self._call()
        assert "--overlap" in result

    def test_jobid_flag(self):
        result = self._call(job_id="99999")
        assert "--jobid=99999" in result

    def test_apptainer_exec_in_command(self):
        result = self._call()
        assert "apptainer" in result
        assert "exec" in result

    def test_instance_uri_in_command(self):
        result = self._call(instance_name="scitex-alice-myproj")
        assert "instance://scitex-alice-myproj" in result

    def test_returns_list_of_strings(self):
        result = self._call()
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)


# ---------------------------------------------------------------------------
# build_instance_start_script
# ---------------------------------------------------------------------------


class TestBuildInstanceStartScript:
    """Tests for build_instance_start_script."""

    def _call(self, **kwargs):
        cb = _cb()
        defaults = dict(
            container_path="/opt/scitex/scitex.sif",
            username="alice",
            host_user_dir=Path("/home/alice"),
            host_project_dir=Path("/data/proj/myproject"),
            project_slug="myproject",
            instance_name="scitex-alice-myproject",
        )
        defaults.update(kwargs)
        return cb.build_instance_start_script(**defaults)

    def test_returns_string(self):
        result = self._call()
        assert isinstance(result, str)

    def test_shebang_present(self):
        result = self._call()
        assert result.startswith("#!/bin/bash")

    def test_instance_start_command_in_script(self):
        result = self._call()
        assert "apptainer instance start" in result

    def test_instance_name_in_script(self):
        result = self._call(instance_name="my-test-instance")
        assert "my-test-instance" in result

    def test_instance_ready_marker_in_script(self):
        result = self._call()
        assert "INSTANCE_READY" in result

    def test_instance_failed_marker_in_script(self):
        result = self._call()
        assert "INSTANCE_FAILED" in result

    def test_keepalive_loop_present(self):
        """Script must contain a loop to keep the allocation alive."""
        result = self._call()
        assert "while" in result
        assert "sleep" in result

    def test_container_path_in_script(self):
        container = "/opt/scitex/scitex.sif"
        result = self._call(container_path=container)
        assert container in result


# ---------------------------------------------------------------------------
# build_srun_command
# ---------------------------------------------------------------------------


class TestBuildSrunCommand:
    """Tests for build_srun_command."""

    def _call(self, **kwargs):
        cb = _cb()
        defaults = dict(
            container_path="/opt/scitex/scitex.sif",
            username="alice",
            host_user_dir=Path("/home/alice"),
            host_project_dir=Path("/data/proj/myproject"),
            project_slug="myproject",
            slurm_partition="compute",
            slurm_time_limit="8:00:00",
            slurm_cpus=4,
            slurm_memory_gb=16,
        )
        defaults.update(kwargs)
        return cb.build_srun_command(**defaults)

    def test_starts_with_srun(self):
        result = self._call()
        assert result[0] == "srun"

    def test_pty_flag(self):
        result = self._call()
        assert "--pty" in result

    def test_partition_arg(self):
        result = self._call(slurm_partition="highmem")
        assert "--partition=highmem" in result

    def test_time_limit_arg(self):
        result = self._call(slurm_time_limit="4:00:00")
        assert "--time=4:00:00" in result

    def test_cpus_arg(self):
        result = self._call(slurm_cpus=16)
        assert "--cpus-per-task=16" in result

    def test_memory_arg(self):
        result = self._call(slurm_memory_gb=64)
        assert "--mem=64G" in result

    def test_job_name_includes_username(self):
        result = self._call(username="bob")
        job_name_args = [a for a in result if "job-name" in a]
        assert job_name_args
        assert "bob" in job_name_args[0]

    def test_apptainer_exec_in_command(self):
        result = self._call()
        assert "apptainer" in result
        assert "exec" in result

    def test_container_path_included(self):
        container = "/opt/scitex/scitex.sif"
        result = self._call(container_path=container)
        assert container in result

    def test_deprecated_screen_session_ignored(self):
        """screen_session parameter is deprecated and should not affect output."""
        result_with = self._call(screen_session="scitex-0")
        result_without = self._call()
        assert result_with == result_without

    def test_returns_list_of_strings(self):
        result = self._call()
        assert isinstance(result, list)
        assert all(isinstance(t, str) for t in result)


# EOF
