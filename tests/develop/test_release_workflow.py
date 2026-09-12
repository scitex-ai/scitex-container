"""Regression tests for the tag-driven release workflow."""

from pathlib import Path

import yaml


WORKFLOW = Path(".github/workflows/pypi-publish-and-github-release-on-tag.yml")


def _workflow() -> dict:
    # PyYAML's YAML 1.1 resolver treats the unquoted key ``on`` as True. That
    # does not affect the jobs inspected by these regression tests.
    return yaml.safe_load(WORKFLOW.read_text())


def test_release_jobs_do_not_depend_on_legacy_runner_state():
    # Arrange
    text = WORKFLOW.read_text()
    workflow = _workflow()

    # Act
    legacy_tokens = (
        "SCITEX_CI_APPTAINER",
        "SCITEX_CI_SIF",
        "exec-in-sif.sh",
        "vars.CI_RUNS_ON",
    )
    release_runners = {
        workflow["jobs"][name]["runs-on"]
        for name in ("test", "build", "publish", "release")
    }

    # Assert
    assert all(token not in text for token in legacy_tokens) and release_runners == {
        "ubuntu-latest"
    }


def test_release_publish_remains_gated_by_tests_and_build():
    # Arrange
    jobs = _workflow()["jobs"]

    # Act
    actual = (
        jobs["build"]["needs"],
        jobs["publish"]["needs"],
        set(jobs["release"]["needs"]),
        jobs["publish"]["steps"][-1]["uses"].split("@", 1)[0],
    )

    # Assert
    assert actual == (
        "test",
        "build",
        {"build", "publish"},
        "pypa/gh-action-pypi-publish",
    )


def test_manual_rerun_checks_out_requested_existing_tag():
    # Arrange
    jobs = _workflow()["jobs"]

    # Act
    refs = {}
    for name in ("test", "build"):
        checkout = next(
            step
            for step in jobs[name]["steps"]
            if step.get("uses", "").startswith("actions/checkout@")
        )
        refs[name] = checkout["with"]["ref"]

    release_checkout = next(
        step
        for step in jobs["release"]["steps"]
        if step.get("uses", "").startswith("actions/checkout@")
    )
    refs["release"] = release_checkout["with"]["ref"]

    # Assert
    assert refs == {
        "test": "${{ steps.version.outputs.tag }}",
        "build": "${{ steps.version.outputs.tag }}",
        "release": "${{ needs.build.outputs.version }}",
    }
