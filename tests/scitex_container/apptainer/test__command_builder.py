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
        # Arrange
        cb = _cb()
        # Act
        result = cb.build_dev_pythonpath([])
        # Assert
        assert result == ""

    def test_single_repo_result_equals_opt_dev_scitex_pytho(self):
        # Arrange
        cb = _cb()
        dev_repos = [
            {"name": "scitex-python", "host_path": "/home/user/proj/scitex-python"}
        ]
        # Act
        result = cb.build_dev_pythonpath(dev_repos)
        # Assert
        assert result == "/opt/dev/scitex-python/src"

    def test_multiple_repos_colon_separated_len_parts_is_2(self):
        # Arrange
        cb = _cb()
        dev_repos = [
            {"name": "repo-a", "host_path": "/home/user/proj/repo-a"},
            {"name": "repo-b", "host_path": "/home/user/proj/repo-b"},
        ]
        result = cb.build_dev_pythonpath(dev_repos)
        # Act
        parts = result.split(":")
        # Act
        # Assert
        assert len(parts) == 2

    def test_multiple_repos_colon_separated_opt_dev_repo_a_src_in_parts(self):
        # Arrange
        cb = _cb()
        dev_repos = [
            {"name": "repo-a", "host_path": "/home/user/proj/repo-a"},
            {"name": "repo-b", "host_path": "/home/user/proj/repo-b"},
        ]
        result = cb.build_dev_pythonpath(dev_repos)
        # Act
        parts = result.split(":")
        # Act
        # Assert
        assert "/opt/dev/repo-a/src" in parts

    def test_multiple_repos_colon_separated_opt_dev_repo_b_src_in_parts(self):
        # Arrange
        cb = _cb()
        dev_repos = [
            {"name": "repo-a", "host_path": "/home/user/proj/repo-a"},
            {"name": "repo-b", "host_path": "/home/user/proj/repo-b"},
        ]
        result = cb.build_dev_pythonpath(dev_repos)
        # Act
        parts = result.split(":")
        # Act
        # Assert
        assert "/opt/dev/repo-b/src" in parts


    def test_src_layout_paths(self):
        """Each repo path must end in /src (src-layout convention)."""
        # Arrange
        cb = _cb()
        dev_repos = [{"name": "myrepo", "host_path": "/somewhere/myrepo"}]
        # Act
        result = cb.build_dev_pythonpath(dev_repos)
        # Assert
        assert result.endswith("/src")

    def test_repo_name_used_not_host_path_cool_lib_in_result(self):
        # Arrange
        cb = _cb()
        dev_repos = [{"name": "cool-lib", "host_path": "/totally/different/path"}]
        # Act
        result = cb.build_dev_pythonpath(dev_repos)
        # Act
        # Assert
        assert "cool-lib" in result

    def test_repo_name_used_not_host_path_totally_different_path_not_in_result(self):
        # Arrange
        cb = _cb()
        dev_repos = [{"name": "cool-lib", "host_path": "/totally/different/path"}]
        # Act
        result = cb.build_dev_pythonpath(dev_repos)
        # Act
        # Assert
        assert "/totally/different/path" not in result



# ---------------------------------------------------------------------------
# build_host_mount_binds
# ---------------------------------------------------------------------------


class TestBuildHostMountBinds:
    """Tests for build_host_mount_binds."""

    def test_no_args_returns_empty_list(self):
        # Arrange
        cb = _cb()
        # Act
        result = cb.build_host_mount_binds()
        # Assert
        assert result == []

    def test_none_args_returns_empty_list(self):
        # Arrange
        cb = _cb()
        # Act
        result = cb.build_host_mount_binds(host_mounts=None, texlive_prefix="")
        # Assert
        assert result == []

    def test_single_host_mount_bind_in_result(self):
        # Arrange
        cb = _cb()
        host_mounts = [
            {"host_path": "/data/shared", "container_path": "/mnt/shared", "mode": "ro"}
        ]
        # Act
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Act
        # Assert
        assert "--bind" in result

    def test_single_host_mount_data_shared_mnt_shared_ro_in_result(self):
        # Arrange
        cb = _cb()
        host_mounts = [
            {"host_path": "/data/shared", "container_path": "/mnt/shared", "mode": "ro"}
        ]
        # Act
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Act
        # Assert
        assert "/data/shared:/mnt/shared:ro" in result


    def test_host_mount_produces_alternating_pairs_result_0_bind(self):
        # Arrange
        cb = _cb()
        host_mounts = [{"host_path": "/src", "container_path": "/dst", "mode": "rw"}]
        # Act
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Act
        # Assert
        assert result[0] == "--bind"

    def test_host_mount_produces_alternating_pairs_result_1_src_dst_rw(self):
        # Arrange
        cb = _cb()
        host_mounts = [{"host_path": "/src", "container_path": "/dst", "mode": "rw"}]
        # Act
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Act
        # Assert
        assert result[1] == "/src:/dst:rw"


    def test_multiple_host_mounts_len_result_is_4(self):
        # Arrange
        cb = _cb()
        host_mounts = [
            {"host_path": "/a", "container_path": "/ca", "mode": "ro"},
            {"host_path": "/b", "container_path": "/cb", "mode": "rw"},
        ]
        # Act
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Act
        # Assert
        assert len(result) == 4

    def test_multiple_host_mounts_result_count_bind_2(self):
        # Arrange
        cb = _cb()
        host_mounts = [
            {"host_path": "/a", "container_path": "/ca", "mode": "ro"},
            {"host_path": "/b", "container_path": "/cb", "mode": "rw"},
        ]
        # Act
        result = cb.build_host_mount_binds(host_mounts=host_mounts)
        # Act
        # Assert
        assert result.count("--bind") == 2


    def test_texlive_prefix_generates_share_binds(self):
        """Providing texlive_prefix should produce share/texlive bind entries."""
        # Arrange
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        specs = [
            result[i + 1] for i in range(0, len(result), 2) if result[i] == "--bind"
        ]
        # Act
        share_specs = [s for s in specs if "share" in s]
        # Assert
        assert share_specs, "Expected at least one share/ bind for texlive_prefix=/usr"

    def test_texlive_prefix_generates_binary_binds(self):
        """Providing texlive_prefix should produce binary bind entries."""
        # Arrange
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        specs = [
            result[i + 1] for i in range(0, len(result), 2) if result[i] == "--bind"
        ]
        # Act
        bin_specs = [s for s in specs if "/bin/" in s]
        # Assert
        assert bin_specs, "Expected at least one /bin/ bind for texlive_prefix=/usr"

    def test_texlive_prefix_trailing_slash_stripped(self):
        """Trailing slash on prefix must not appear doubled in paths."""
        # Arrange
        cb = _cb()
        result_with = cb.build_host_mount_binds(texlive_prefix="/usr/")
        # Act
        result_without = cb.build_host_mount_binds(texlive_prefix="/usr")
        # Assert
        assert result_with == result_without

    def test_texlive_all_bind_args_start_with_double_dash_bind(self):
        # Arrange
        # Act
        # Assert
        cb = _cb()
        # Act
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        # Assert
        assert all(result[i] == '--bind' for i in range(0, len(result), 2)), f"Expected '--bind' at index {i}, got {result[i]!r}"

    def test_texlive_specs_are_readonly(self):
        """TeX Live bind entries must use :ro mode."""
        # Arrange
        # Act
        # Assert
        cb = _cb()
        result = cb.build_host_mount_binds(texlive_prefix="/usr")
        specs = [
            result[i + 1] for i in range(0, len(result), 2) if result[i] == "--bind"
        ]
        assert all(spec.endswith(':ro') for spec in specs), f'Expected :ro suffix on spec: {spec!r}'


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

    def test_returns_list_result_is_list(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert isinstance(result, list)

    def test_starts_with_apptainer_exec_result_0_apptainer(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert result[0] == "apptainer"

    def test_starts_with_apptainer_exec_result_1_exec(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert result[1] == "exec"


    def test_containall_present_containall_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--containall" in result

    def test_cleanenv_present_cleanenv_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--cleanenv" in result

    def test_writable_tmpfs_present(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--writable-tmpfs" in result

    def test_hostname_set_to_scitex_cloud(self):
        # Arrange
        result = self._call()
        # Act
        idx = result.index("--hostname")
        # Assert
        assert result[idx + 1] == "scitex-cloud"

    def test_container_path_is_last(self):
        """Container path must be the last positional argument."""
        # Arrange
        container = "/opt/scitex/scitex.sif"
        # Act
        result = self._call(container_path=container)
        # Assert
        assert result[-1] == container

    def test_username_in_env_env_pairs_get_user_bob(self):
        # Arrange
        result = self._call(username="bob")
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Act
        # Assert
        assert env_pairs.get("USER") == "bob"

    def test_username_in_env_env_pairs_get_logname_bob(self):
        # Arrange
        result = self._call(username="bob")
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Act
        # Assert
        assert env_pairs.get("LOGNAME") == "bob"

    def test_username_in_env_env_pairs_get_scitex_user_bob(self):
        # Arrange
        result = self._call(username="bob")
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Act
        # Assert
        assert env_pairs.get("SCITEX_USER") == "bob"


    def test_project_slug_in_env(self):
        # Arrange
        result = self._call(project_slug="cool-proj")
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Assert
        assert env_pairs.get("SCITEX_PROJECT") == "cool-proj"

    def test_home_bind_mount_home_spec_startswith_home_alice(self):
        # Arrange
        result = self._call(username="alice", host_user_dir=Path("/home/alice"))
        idx = result.index("--home")
        # Act
        home_spec = result[idx + 1]
        # Act
        # Assert
        assert home_spec.startswith("/home/alice")

    def test_home_bind_mount_home_alice_in_home_spec(self):
        # Arrange
        result = self._call(username="alice", host_user_dir=Path("/home/alice"))
        idx = result.index("--home")
        # Act
        home_spec = result[idx + 1]
        # Act
        # Assert
        assert ":/home/alice" in home_spec


    def test_project_bind_mount_project_bind(self):
        # Arrange
        result = self._call(
            username="alice",
            host_project_dir=Path("/data/proj/myproject"),
            project_slug="myproject",
        )
        bind_specs = self._extract_bind_specs(result)
        # Act
        project_bind = [s for s in bind_specs if "myproject" in s]
        # Act
        # Assert
        assert project_bind, "Expected a --bind spec containing the project slug"

    def test_project_bind_mount_rw_in_project_bind_0(self):
        # Arrange
        result = self._call(
            username="alice",
            host_project_dir=Path("/data/proj/myproject"),
            project_slug="myproject",
        )
        bind_specs = self._extract_bind_specs(result)
        # Act
        project_bind = [s for s in bind_specs if "myproject" in s]
        # Act
        # Assert
        assert ":rw" in project_bind[0]


    def test_dev_repos_add_bind_mounts(self):
        # Arrange
        dev_repos = [{"name": "mylib", "host_path": "/home/alice/proj/mylib"}]
        result = self._call(dev_repos=dev_repos)
        bind_specs = self._extract_bind_specs(result)
        # Act
        dev_bind = [s for s in bind_specs if "/opt/dev/mylib" in s]
        # Assert
        assert dev_bind, "Expected a --bind spec for dev repo mounted at /opt/dev/mylib"

    def test_dev_repos_add_pythonpath_env_pythonpath_in_env_pairs(self):
        # Arrange
        dev_repos = [{"name": "mylib", "host_path": "/home/alice/proj/mylib"}]
        result = self._call(dev_repos=dev_repos)
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Act
        # Assert
        assert "PYTHONPATH" in env_pairs

    def test_dev_repos_add_pythonpath_env_mylib_in_env_pairs_pythonpath(self):
        # Arrange
        dev_repos = [{"name": "mylib", "host_path": "/home/alice/proj/mylib"}]
        result = self._call(dev_repos=dev_repos)
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Act
        # Assert
        assert "mylib" in env_pairs["PYTHONPATH"]


    def test_no_dev_repos_no_pythonpath(self):
        # Arrange
        result = self._call(dev_repos=None)
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Assert
        assert "PYTHONPATH" not in env_pairs

    def test_scitex_cloud_env_is_true(self):
        # Arrange
        result = self._call()
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Assert
        assert env_pairs.get("SCITEX_CLOUD") == "true"

    def test_shell_env_is_bash(self):
        # Arrange
        result = self._call()
        # Act
        env_pairs = self._extract_env_pairs(result)
        # Assert
        assert env_pairs.get("SHELL") == "/bin/bash"

    def test_pwd_set_to_project_dir_myproject_in_pwd_val(self):
        # Arrange
        result = self._call(username="alice", project_slug="myproject")
        idx = result.index("--pwd")
        # Act
        pwd_val = result[idx + 1]
        # Act
        # Assert
        assert "myproject" in pwd_val

    def test_pwd_set_to_project_dir_pwd_val_startswith_home_alice(self):
        # Arrange
        result = self._call(username="alice", project_slug="myproject")
        idx = result.index("--pwd")
        # Act
        pwd_val = result[idx + 1]
        # Act
        # Assert
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
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert result[0] == "sbatch"

    def test_parsable_flag_parsable_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--parsable" in result

    def test_partition_arg_partition_highmem_in_result(self):
        # Arrange
        # Act
        result = self._call(slurm_partition="gpu")
        # Assert
        assert "--partition=gpu" in result

    def test_time_limit_arg(self):
        # Arrange
        # Act
        result = self._call(slurm_time_limit="2:00:00")
        # Assert
        assert "--time=2:00:00" in result

    def test_cpus_arg_cpus_per_task_16_in_result(self):
        # Arrange
        # Act
        result = self._call(slurm_cpus=8)
        # Assert
        assert "--cpus-per-task=8" in result

    def test_memory_arg_mem_64g_in_result(self):
        # Arrange
        # Act
        result = self._call(slurm_memory_gb=32)
        # Assert
        assert "--mem=32G" in result

    def test_job_name_includes_username_and_slug_job_name_args(self):
        # Arrange
        result = self._call(username="alice", project_slug="myproj")
        # Act
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        # Act
        # Assert
        assert job_name_args

    def test_job_name_includes_username_and_slug_alice_in_job_name_args_0(self):
        # Arrange
        result = self._call(username="alice", project_slug="myproj")
        # Act
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        # Act
        # Assert
        assert "alice" in job_name_args[0]

    def test_job_name_includes_username_and_slug_myproj_in_job_name_args_0(self):
        # Arrange
        result = self._call(username="alice", project_slug="myproj")
        # Act
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        # Act
        # Assert
        assert "myproj" in job_name_args[0]


    def test_job_name_falls_back_to_instance_name_when_no_username_job_name_args(self):
        # Arrange
        result = self._call(username="", instance_name="my-instance")
        # Act
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        # Act
        # Assert
        assert job_name_args

    def test_job_name_falls_back_to_instance_name_when_no_username_my_instance_in_job_name_args_0(self):
        # Arrange
        result = self._call(username="", instance_name="my-instance")
        # Act
        job_name_args = [a for a in result if a.startswith("--job-name=")]
        # Act
        # Assert
        assert "my-instance" in job_name_args[0]


    def test_output_is_dev_null(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--output=/dev/null" in result

    def test_script_path_is_last(self):
        # Arrange
        # Act
        result = self._call(script_path="/tmp/myscript.sh")
        # Assert
        assert result[-1] == "/tmp/myscript.sh"

    def test_returns_list_of_strings_result_is_list(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert isinstance(result, list)

    def test_returns_list_of_strings_all_isinstance_t_str_for_t_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
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
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert result[0] == "srun"

    def test_pty_flag_pty_in_result_2(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--pty" in result

    def test_overlap_flag_overlap_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--overlap" in result

    def test_jobid_flag_jobid_99999_in_result(self):
        # Arrange
        # Act
        result = self._call(job_id="99999")
        # Assert
        assert "--jobid=99999" in result

    def test_apptainer_exec_in_command_apptainer_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert "apptainer" in result

    def test_apptainer_exec_in_command_exec_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert "exec" in result


    def test_instance_uri_in_command(self):
        # Arrange
        # Act
        result = self._call(instance_name="scitex-alice-myproj")
        # Assert
        assert "instance://scitex-alice-myproj" in result

    def test_returns_list_of_strings_result_is_list(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert isinstance(result, list)

    def test_returns_list_of_strings_all_isinstance_t_str_for_t_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
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

    def test_returns_string_result_is_str(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert isinstance(result, str)

    def test_shebang_present_result_startswith_bin_bash(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert result.startswith("#!/bin/bash")

    def test_instance_start_command_in_script(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "apptainer instance start" in result

    def test_instance_name_in_script(self):
        # Arrange
        # Act
        result = self._call(instance_name="my-test-instance")
        # Assert
        assert "my-test-instance" in result

    def test_instance_ready_marker_in_script(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "INSTANCE_READY" in result

    def test_instance_failed_marker_in_script(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "INSTANCE_FAILED" in result

    def test_keepalive_loop_present_while_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert "while" in result

    def test_keepalive_loop_present_sleep_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert "sleep" in result


    def test_container_path_in_script(self):
        # Arrange
        container = "/opt/scitex/scitex.sif"
        # Act
        result = self._call(container_path=container)
        # Assert
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
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert result[0] == "srun"

    def test_pty_flag_pty_in_result_2(self):
        # Arrange
        # Act
        result = self._call()
        # Assert
        assert "--pty" in result

    def test_partition_arg_partition_highmem_in_result(self):
        # Arrange
        # Act
        result = self._call(slurm_partition="highmem")
        # Assert
        assert "--partition=highmem" in result

    def test_time_limit_arg(self):
        # Arrange
        # Act
        result = self._call(slurm_time_limit="4:00:00")
        # Assert
        assert "--time=4:00:00" in result

    def test_cpus_arg_cpus_per_task_16_in_result(self):
        # Arrange
        # Act
        result = self._call(slurm_cpus=16)
        # Assert
        assert "--cpus-per-task=16" in result

    def test_memory_arg_mem_64g_in_result(self):
        # Arrange
        # Act
        result = self._call(slurm_memory_gb=64)
        # Assert
        assert "--mem=64G" in result

    def test_job_name_includes_username_job_name_args(self):
        # Arrange
        result = self._call(username="bob")
        # Act
        job_name_args = [a for a in result if "job-name" in a]
        # Act
        # Assert
        assert job_name_args

    def test_job_name_includes_username_bob_in_job_name_args_0(self):
        # Arrange
        result = self._call(username="bob")
        # Act
        job_name_args = [a for a in result if "job-name" in a]
        # Act
        # Assert
        assert "bob" in job_name_args[0]


    def test_apptainer_exec_in_command_apptainer_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert "apptainer" in result

    def test_apptainer_exec_in_command_exec_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert "exec" in result


    def test_container_path_included(self):
        # Arrange
        container = "/opt/scitex/scitex.sif"
        # Act
        result = self._call(container_path=container)
        # Assert
        assert container in result

    def test_deprecated_screen_session_ignored(self):
        """screen_session parameter is deprecated and should not affect output."""
        # Arrange
        result_with = self._call(screen_session="scitex-0")
        # Act
        result_without = self._call()
        # Assert
        assert result_with == result_without

    def test_returns_list_of_strings_result_is_list(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert isinstance(result, list)

    def test_returns_list_of_strings_all_isinstance_t_str_for_t_in_result(self):
        # Arrange
        # Act
        result = self._call()
        # Act
        # Assert
        assert all(isinstance(t, str) for t in result)



# EOF
