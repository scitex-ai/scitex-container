# Python API

## apptainer module

| Function | Purpose |
|----------|---------|
| `build_exec_args()` | Build Apptainer exec command with mounts |
| `build_host_mount_binds()` | Format host mount bindings |
| `build_sbatch_command()` | Build SLURM sbatch command with container |
| `build_srun_command()` | Build SLURM srun command with container |
| `build_shell_in_allocation_command()` | Shell command in SLURM allocation |
| `build_dev_pythonpath()` | Construct PYTHONPATH for development repos |
| `build_instance_start_script()` | Generate instance startup script |
| `detect_container_cmd()` | Detect Apptainer/Singularity CLI |
| `find_containers_dir()` | Auto-locate containers directory |
| `freeze()` | Capture SIF metadata (hash, .def, lock files) |
| `list_versions()` | List all SIF versions |
| `get_active_version()` | Get active SIF version |
| `switch_version()` | Switch active SIF version |
| `list_sandboxes()` | List all sandbox versions |
| `get_active_sandbox()` | Get active sandbox version |
| `switch_sandbox()` | Switch active sandbox |
| `rollback_sandbox()` | Roll back to previous sandbox |
| `sandbox_to_sif()` | Convert sandbox to SIF image |
| `sandbox_update()` | Update packages in sandbox |
| `sandbox_maintain()` | Run maintenance in sandbox with fakeroot |
| `sandbox_configure_ps1()` | Configure sandbox shell prompt |
| `cleanup_sandboxes()` | Remove old sandbox versions |
| `cleanup_sifs()` | Remove old SIF versions |
| `is_sandbox()` | Check if path is a sandbox |

## docker module

| Function | Purpose |
|----------|---------|
| `rebuild()` | Rebuild Docker images without cache |
| `restart()` | Restart Docker containers (compose down/up) |
| `status()` | Get Docker container status |
| `get_dev_mounts()` | Convert dev repo list to mount arguments |

## host module

| Function | Purpose |
|----------|---------|
| `get_mount_config()` | Get texlive/imagemagick mount configuration |
| `get_texlive_binds()` | Get TeXLive binary mount paths |
