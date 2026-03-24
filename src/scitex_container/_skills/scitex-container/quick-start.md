## Quick Start

```bash
# Build container from definition
scitex-container build ./Singularity.def -o container.sif

# Run command in container
scitex-container run container.sif python train.py

# Push to registry
scitex-container push container.sif oras://registry/image:tag
```

```python
from scitex_container import apptainer, docker

# List SIF versions
versions = apptainer.list_versions()

# Switch active version
apptainer.switch_version("v2.1")

# Freeze container metadata (hash, def, lock files)
apptainer.freeze("container.sif")

# Docker operations
docker.restart()
docker.status()
```
