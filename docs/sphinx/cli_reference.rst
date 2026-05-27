CLI Reference
=============

The ``scitex-container`` CLI provides unified container management for
Apptainer and Docker.

Global Options
--------------

.. code-block:: text

   scitex-container [OPTIONS] COMMAND [ARGS]...

   Options:
     -V, --version         Show version and exit.
     --help-recursive      Show help for all commands recursively.
     --json                Emit machine-readable JSON output (where supported).
     -h, --help            Show this message and exit.

Apptainer Commands
------------------

All Apptainer commands are nested under the ``apptainer`` sub-group:

.. code-block:: bash

   scitex-container apptainer COMMAND [ARGS]...

build
~~~~~

Build a SIF or sandbox from a definition (``.def``) file.

.. code-block:: bash

   scitex-container apptainer build [OPTIONS] [NAME]

Options:

* ``--sandbox`` — build a sandbox directory instead of SIF
* ``--force`` / ``-f`` — force rebuild even if up-to-date
* ``--output-dir`` / ``-o`` — output directory (default: parent of .def)
* ``--dry-run`` — preview without building

freeze
~~~~~~

Extract pinned package versions (pip, dpkg, npm) from a built SIF.

.. code-block:: bash

   scitex-container apptainer freeze [OPTIONS] SIF_PATH

Options:

* ``--output-dir`` / ``-o`` — output directory for lock files

list
~~~~

List all versioned SIF files with metadata.

.. code-block:: bash

   scitex-container apptainer list [OPTIONS]

Options:

* ``--dir`` / ``-d`` — containers directory
* ``--json`` — machine-readable JSON output

switch
~~~~~~

Switch the active container version (updates ``current.sif`` symlink).

.. code-block:: bash

   scitex-container apptainer switch [OPTIONS] VERSION

Options:

* ``--dir`` / ``-d`` — containers directory
* ``--sudo`` — use sudo for symlink operations

rollback
~~~~~~~~

Revert to the previous container version.

.. code-block:: bash

   scitex-container apptainer rollback [OPTIONS]

Options:

* ``--dir`` / ``-d`` — containers directory
* ``--sudo`` — use sudo for symlink operations
* ``--dry-run`` — preview without executing

deploy
~~~~~~

Copy active SIF to a production target directory.

.. code-block:: bash

   scitex-container apptainer deploy [OPTIONS]

Options:

* ``--target`` / ``-t`` — deployment target directory (default: /opt/scitex/singularity)
* ``--dir`` / ``-d`` — source containers directory

clean
~~~~~

Remove old container versions, keeping the N most recent.

.. code-block:: bash

   scitex-container apptainer clean [OPTIONS]

Options:

* ``--keep`` / ``-k`` — number of recent versions to keep (default: 3)
* ``--dir`` / ``-d`` — containers directory
* ``--dry-run`` — preview without executing

verify
~~~~~~

Verify container integrity: SHA256 hash, .def origin, lock file comparison.

.. code-block:: bash

   scitex-container apptainer verify [OPTIONS] [SIF_PATH]

Options:

* ``--def`` — path to .def file to verify against
* ``--lock-dir`` — directory containing lock files
* ``--json`` — output raw JSON

Sandbox Commands
----------------

.. code-block:: bash

   scitex-container sandbox COMMAND [ARGS]...

create
~~~~~~

Build a timestamped sandbox from a SIF image or .def file.

.. code-block:: bash

   scitex-container sandbox create [OPTIONS]

Options:

* ``--source`` / ``-s`` — source .sif or .def file (required)
* ``--dir`` / ``-d`` — containers directory
* ``--output`` / ``-o`` — explicit output directory
* ``--dry-run`` — preview without executing

maintain
~~~~~~~~

Run a maintenance command inside a sandbox (writable + fakeroot).

.. code-block:: bash

   scitex-container sandbox maintain [OPTIONS] COMMAND...

Options:

* ``--sandbox-dir`` / ``-s`` — sandbox directory path (required)

list
~~~~

List versioned sandbox directories.

.. code-block:: bash

   scitex-container sandbox list [OPTIONS]

Options:

* ``--dir`` / ``-d`` — containers directory
* ``--json`` — machine-readable JSON output

switch
~~~~~~

Switch active sandbox to a specific version (timestamp).

.. code-block:: bash

   scitex-container sandbox switch [OPTIONS] VERSION

Options:

* ``--dir`` / ``-d`` — containers directory
* ``--sudo`` — use sudo for symlink operations

rollback
~~~~~~~~

Revert to the previous sandbox version.

.. code-block:: bash

   scitex-container sandbox rollback [OPTIONS]

Options:

* ``--dir`` / ``-d`` — containers directory
* ``--sudo`` — use sudo for symlink operations
* ``--dry-run`` — preview without executing

clean
~~~~~

Remove old sandbox directories, keeping the N most recent.

.. code-block:: bash

   scitex-container sandbox clean [OPTIONS]

Options:

* ``--keep`` / ``-k`` — number of recent sandboxes to keep (default: 5)
* ``--dir`` / ``-d`` — containers directory
* ``--dry-run`` — preview without executing

update
~~~~~~

Incrementally update ecosystem packages inside an existing sandbox.

.. code-block:: bash

   scitex-container sandbox update [OPTIONS]

Options:

* ``--sandbox-dir`` / ``-s`` — sandbox directory path (required)
* ``--proj-root`` / ``-r`` — project root containing repos (default: ~/proj)
* ``--pkg`` / ``-p`` — update only this package
* ``--deps`` — install dependencies too (slower)

configure-ps1
~~~~~~~~~~~~~

Configure PS1 prompt in a sandbox environment script.

.. code-block:: bash

   scitex-container sandbox configure-ps1 [OPTIONS]

Options:

* ``--sandbox-dir`` / ``-s`` — sandbox directory path
* ``--ps1`` — PS1 prompt string (default: \W $ )

Docker Commands
---------------

.. code-block:: bash

   scitex-container docker COMMAND [ARGS]...

rebuild
~~~~~~~

Rebuild Docker Compose services without cache.

.. code-block:: bash

   scitex-container docker rebuild [OPTIONS]

Options:

* ``--env`` / ``-e`` — environment (dev/prod, default: dev)
* ``--dry-run`` — preview without executing

restart
~~~~~~~

Restart Docker Compose services (down then up -d).

.. code-block:: bash

   scitex-container docker restart [OPTIONS]

Options:

* ``--env`` / ``-e`` — environment (dev/prod, default: dev)
* ``--dry-run`` — preview without executing

Host Commands
-------------

.. code-block:: bash

   scitex-container host COMMAND [ARGS]...

install
~~~~~~~

Install host-side packages (TeX Live, ImageMagick) — requires sudo.

.. code-block:: bash

   scitex-container host install [OPTIONS]

Options:

* ``--texlive`` — install only TeX Live
* ``--imagemagick`` — install only ImageMagick
* ``--all`` — install all packages (default when no specific flag given)
* ``--dry-run`` — preview without executing

check
~~~~~

Check status of required host packages.

.. code-block:: bash

   scitex-container host check [OPTIONS]

show-mounts
~~~~~~~~~~~

Show bind mount configuration for host packages.

.. code-block:: bash

   scitex-container host show-mounts [OPTIONS]

Options:

* ``--texlive-prefix`` — TeX Live installation prefix (default: /usr)
* ``--json`` — machine-readable JSON output

Status Dashboard
----------------

.. code-block:: bash

   scitex-container show-status [OPTIONS]
   scitex-container show-status --json

Displays a unified dashboard showing the status of Apptainer containers,
Docker services, and host package installations.

Environment Snapshot
--------------------

.. code-block:: bash

   scitex-container save-env-snapshot [OPTIONS]

Capture a reproducibility snapshot of the current environment (container
version + SIF hash + host packages + git commits + lock files). Output is
a JSON-serializable dict.

Options:

* ``--json`` — output raw JSON
* ``--dev-repo`` — git repo path to include (repeatable)
* ``--containers-dir`` — containers directory (auto-detected if not given)
* ``--dry-run`` — preview without executing

Skills
------

.. code-block:: bash

   scitex-container skills COMMAND [ARGS]...

list
~~~~

List available skill files bundled with the package.

.. code-block:: bash

   scitex-container skills list [OPTIONS]

Options:

* ``--json`` — machine-readable JSON output

get
~~~

Print the contents of a skill file by name (stem or path).

.. code-block:: bash

   scitex-container skills get [OPTIONS] NAME

Options:

* ``--json`` — machine-readable JSON output

install
~~~~~~~

Install skills to a target directory (default: ~/.scitex/dev/skills/scitex-container/).

.. code-block:: bash

   scitex-container skills install [OPTIONS]

Options:

* ``--dest`` — destination directory
* ``--no-link`` — copy files instead of symlinking
* ``--claude-symlink`` — also expose at ~/.claude/skills/scitex/
* ``--dry-run`` — preview without linking/copying

MCP Commands
------------

.. code-block:: bash

   scitex-container mcp COMMAND [ARGS]...

start
~~~~~

Start the MCP (Model Context Protocol) server.

.. code-block:: bash

   scitex-container mcp start [OPTIONS]

Options:

* ``--transport`` / ``-t`` — transport type (stdio/sse/http, default: stdio)
* ``--host`` / ``-h`` — host to bind (default: 0.0.0.0)
* ``--port`` / ``-p`` — port to bind (default: 8086)

doctor
~~~~~~

Check FastMCP availability and tool health.

.. code-block:: bash

   scitex-container mcp doctor [OPTIONS]

list-tools
~~~~~~~~~~

List all registered MCP tools with signatures.

.. code-block:: bash

   scitex-container mcp list-tools [OPTIONS]

Options:

* ``-v`` / ``-vv`` — verbosity (signatures, descriptions)
* ``--json`` — machine-readable JSON output

install
~~~~~~~

Show MCP server installation instructions for Claude Code.

.. code-block:: bash

   scitex-container mcp install [OPTIONS]

Options:

* ``--claude-code`` — show Claude Code config snippet
* ``--json`` — output as JSON

Additional Commands
-------------------

list-python-apis
~~~~~~~~~~~~~~~~

List all public Python APIs (apptainer, docker, host modules) with signatures.

.. code-block:: bash

   scitex-container list-python-apis [OPTIONS]

Options:

* ``-v`` / ``-vv`` — verbosity (signatures, docstrings)
* ``--json`` — machine-readable JSON output
