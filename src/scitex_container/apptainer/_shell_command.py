#!/usr/bin/env python3
# Timestamp: "2026-02-25"
# File: src/scitex_container/apptainer/_shell_command.py
"""Interactive shell entry commands for apptainer sessions.

Extracted from ``_command_builder`` to keep that module within the
project file-size budget. Groups the two shell-entry concerns:

- ``_build_shell_command`` — fix the in-container user identity, point
  ``HOME`` at the user's home, ``cd`` into the project, then hand off to
  a login bash shell.
- ``build_shell_in_allocation_command`` — attach a shell inside an
  already-running SLURM allocation via ``srun --overlap``.
"""

from __future__ import annotations

from scitex_container._compat import supports_return_as


def _build_shell_command(username: str) -> list[str]:
    """Build shell entry command: fix user identity, cd to project dir, start bash."""
    setup_script = (
        # Fix user identity when running as root inside container
        'if [ "$(id -u)" = "0" ] && [ -n "$USER" ] && [ "$USER" != "root" ]; then '
        '  sed -i "s|^root:[^:]*:0:0:[^:]*:[^:]*:|$USER:x:0:0:$USER:/home/$USER:|" /etc/passwd 2>/dev/null; '
        "fi; "
        # Ensure HOME points to the user's home directory.
        # apptainer exec instance:// inherits env from the calling process,
        # which may have HOME set to the broker/Django process's home dir
        # rather than the container user's home. Without this, bash -l
        # looks for .bash_profile in the wrong directory and PS1 is never set.
        'if [ -n "$USER" ]; then export HOME="/home/$USER"; fi; '
        # cd to project dir (SCITEX_PROJECT is set by build_exec_args)
        'if [ -n "$SCITEX_PROJECT" ] && [ -n "$USER" ]; then '
        '  _proj="/home/$USER/proj/$SCITEX_PROJECT"; '
        '  if [ -d "$_proj" ]; then cd "$_proj"; '
        '  else echo "⚠ Project directory $_proj not found — project may have changed on SciTeX Cloud"; '
        "  fi; "
        "fi; "
        "exec /bin/bash -l"
    )
    return ["/bin/bash", "-c", setup_script]


@supports_return_as
def build_shell_in_allocation_command(
    job_id: str,
    instance_name: str,
    username: str = "",
) -> list[str]:
    """Build ``srun --overlap`` command to attach a shell inside an existing allocation.

    Parameters
    ----------
    job_id : str
        SLURM job ID of the running allocation.
    instance_name : str
        Name of the apptainer instance to exec into.
    username : str
        Username for the shell session (used for user identity setup).

    Returns
    -------
    list[str]
        Command list ready for ``os.execvpe`` or ``pty.fork``.
    """
    return [
        "srun",
        "--pty",
        "--overlap",
        f"--jobid={job_id}",
        "apptainer",
        "exec",
        f"instance://{instance_name}",
        *_build_shell_command(username),
    ]


# EOF
