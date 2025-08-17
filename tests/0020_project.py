import json

from pathlib import Path
from dataclasses import asdict

import pytest

from django_willpower.core import ProjectRegistry, Application, Component, Module


def test_register_application(settings):
    """
    We expect there is no error on Application init if all required arguments are
    given.
    """
    blog_config = json.loads((
        settings.fixtures_path / "appstack_samples/blog.json"
    ).read_text())

    cms_config = json.loads((
        settings.fixtures_path / "appstack_samples/cms.json"
    ).read_text())

    project = ProjectRegistry()
    project.add_application(blog_config)
    project.add_application(cms_config)

    # Reversing registered result to identical config if all default values was defined
    assert blog_config == project.apps["blog"].as_dict()
    assert cms_config == project.apps["cms"].as_dict()

    # Application code must be unique in registry
    with pytest.raises(ValueError) as excinfo:
        project.add_application(blog_config)

    expect_msg = "Given Application code is already registered: blog"
    assert expect_msg == str(excinfo.value)


def test_registry_finding(settings):
    """
    Registry should find application, component or module from given stack path.
    """
    blog_config = json.loads((
        settings.fixtures_path / "appstack_samples/blog.json"
    ).read_text())

    cms_config = json.loads((
        settings.fixtures_path / "appstack_samples/cms.json"
    ).read_text())

    project = ProjectRegistry()
    project.add_application(blog_config)
    project.add_application(cms_config)

    # Empty app part
    with pytest.raises(ValueError) as excinfo:
        project.find("@niet:nope")

    expect_msg = "Empty application part is not allowed"
    assert expect_msg == str(excinfo.value)

    # Unknow app from registry
    with pytest.raises(ValueError) as excinfo:
        project.find("nope@niet:init")

    expect_msg = "Application 'nope' is not registered"
    assert expect_msg == str(excinfo.value)

    # Finding application
    found = project.find("cms@")
    print(found)
    assert found.code == "cms"

    # Finding component
    found = project.find("cms@applugins")
    assert found.code == "applugins"

    # Finding module
    found = project.find("blog@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"


def test_register_shipped_configs(settings):
    """
    Shipped application configurations should not fail to be registered once their
    blank fields are filled.
    """
    project = ProjectRegistry()

    advanced_config = json.loads((
        settings.application_path / "data/stacks/advanced.json"
    ).read_text())

    # Application config must include a name, code and destination (shipped
    # configurations are blank)
    with pytest.raises(ValueError) as excinfo:
        project.add_application(advanced_config)

    # Once correctly filled it just works
    project.add_application(
        advanced_config,
        name="Sample",
        code="sample",
        destination="sample/",
    )

    found = project.find("sample@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"
