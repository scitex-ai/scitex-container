MCP Reference
=============

scitex-container exposes an MCP (Model Context Protocol) server so that
AI agents can manage containers autonomously.

Starting the Server
-------------------

.. code-block:: bash

   scitex-container-mcp

Or via the CLI helper:

.. code-block:: bash

   scitex-container mcp install  # Install to Claude Code config

Available MCP Tools (16 total)
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Tool
     - Description
   * - ``container_build``
     - Build a SIF or sandbox from a .def file
   * - ``container_list_versions``
     - List versioned SIFs with active marker
   * - ``container_switch``
     - Switch active SIF version
   * - ``container_rollback``
     - Roll back to previous SIF version
   * - ``container_deploy``
     - Copy active SIF to production target dir
   * - ``container_cleanup``
     - Remove old SIF versions (keep N most recent)
   * - ``container_verify``
     - Verify SIF SHA256, .def origin, and lock file consistency
   * - ``container_status``
     - Unified dashboard: Apptainer + host packages + Docker
   * - ``container_env_snapshot``
     - Capture environment snapshot (container + host + git)
   * - ``container_skills_get``
     - Get content of a bundled skill file by name
   * - ``container_skills_list``
     - List bundled skill files
   * - ``sandbox_create``
     - Convert a SIF to a writable timestamped sandbox directory
   * - ``docker_rebuild``
     - Rebuild Docker images without cache
   * - ``docker_restart``
     - Restart Docker containers (compose down + up -d)
   * - ``host_install``
     - Install TeXLive / ImageMagick on the host
   * - ``host_check``
     - Check which host packages are installed
