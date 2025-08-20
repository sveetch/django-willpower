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

    project = ProjectRegistry()

    project.load_configuration({
        "apps": {
            "blog": {
                "name": "Blog app",
                "destination": "the-blog",
                "template_dir": settings.configs_path / "appstack_single_component",
                "declarations": settings.configs_path / "models_basic_blog.json",
                "appstack": (
                    settings.configs_path / "appstack_single_component"
                    / "appstack.json"
                )
            },
            "cms": {
                "name": "CMS app",
                "destination": "the-cms",
                "template_dir": settings.configs_path / "appstack_dual_components",
                "declarations": settings.configs_path / "models_basic_cms.json",
                "appstack": (
                    settings.configs_path / "appstack_dual_components"
                    / "appstack.json"
                )
            },
        },
    })

    # Run builder processor
    builder = ProjectBuilder(project, tmp_path)
    builder.process()

    # Check expected component directories
    assert sorted(tmp_path.iterdir()) == [
        tmp_path / "the-blog",
        tmp_path / "the-cms",
    ]

    # Check expected module files for all components
    built_files = []
    for root, dirs, files in os.walk(tmp_path):
        built_files.extend([
            str((Path(root) / name).relative_to(tmp_path))
            for name in files
        ])

    assert sorted(built_files) == [
        "the-blog/views/__init__.py",
        "the-blog/views/article.py",
        "the-blog/views/blog.py",
        "the-cms/plugins/page.py",
        "the-cms/views/page.py",
    ]
