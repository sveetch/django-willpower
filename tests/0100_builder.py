import logging
import os
from pathlib import Path

import pytest

from django_willpower import __pkgname__
from django_willpower.core import ProjectRegistry
from django_willpower.core.builder import ProjectBuilder


def test_build_process(caplog, load_json, settings, tmp_path):
    """
    Project builder should build all component modules from applications at the correct
    location.
    """
    caplog.set_level(logging.DEBUG, logger=__pkgname__)

    # Path to appstack directory
    basic_appstack = settings.configs_path / "appstack_single_component"
    dual_appstack = settings.configs_path / "appstack_dual_components"

    # Load application stack configurations
    basic_appstack_conf = load_json(
        settings.configs_path / "appstack_single_component/appstack.json"
    )
    dual_appstack_conf = load_json(
        settings.configs_path / "appstack_dual_components/appstack.json"
    )

    # Load models declarations
    blog_models = load_json(settings.configs_path / "models_basic_blog.json")
    cms_models = load_json(settings.configs_path / "models_basic_cms.json")

    project = ProjectRegistry()

    # Register applications
    project.add_application(
        basic_appstack_conf,
        basic_appstack,
        name="Blog app",
    )
    project.add_app_models("single-component", blog_models)

    project.add_application(
        dual_appstack_conf,
        dual_appstack,
        name="CMS app",
    )
    project.add_app_models("dual-components", cms_models)

    # Run builder processor
    builder = ProjectBuilder(project, tmp_path)
    builder.process()

    # Check expected component directories
    assert sorted(tmp_path.iterdir()) == [
        tmp_path / "dual-components",
        tmp_path / "single-component",
    ]

    # Check expected module files for all components
    built_files = []
    for root, dirs, files in os.walk(tmp_path):
        built_files.extend([
            str((Path(root) / name).relative_to(tmp_path))
            for name in files
        ])

    assert sorted(built_files) == [
        "dual-components/plugins/page.py",
        "dual-components/views/page.py",
        "single-component/views/__init__.py",
        "single-component/views/article.py",
        "single-component/views/blog.py"
    ]
