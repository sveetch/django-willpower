import json

from pathlib import Path
from dataclasses import asdict

import pytest

from django_willpower.core import AppRegistry, Application, Component, Module


def test_register_application(settings):
    """
    We except there is no error on Application init if all required arguments are
    given.
    """
    blog_config = json.loads((
        settings.fixtures_path / "appstack_samples/blog.json"
    ).read_text())

    cms_config = json.loads((
        settings.fixtures_path / "appstack_samples/cms.json"
    ).read_text())

    registry = AppRegistry()
    registry.add_application(blog_config)
    registry.add_application(cms_config)

    # Reversing registered result to identical config if all default values was defined
    assert blog_config == registry.apps["blog"].as_dict()
    assert cms_config == registry.apps["cms"].as_dict()


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

    registry = AppRegistry()
    registry.add_application(blog_config)
    registry.add_application(cms_config)

    # Empty app part
    with pytest.raises(ValueError) as excinfo:
        registry.find("@niet:nope")

    expect_msg = "Empty application part is not allowed"
    assert expect_msg == str(excinfo.value)

    # Unknow app from registry
    with pytest.raises(ValueError) as excinfo:
        registry.find("nope@niet:init")

    expect_msg = "Application 'nope' is not registered"
    assert expect_msg == str(excinfo.value)

    # Finding application
    found = registry.find("cms@")
    print(found)
    assert found.code == "cms"

    # Finding component
    found = registry.find("cms@applugins")
    assert found.code == "applugins"

    # Finding module
    found = registry.find("blog@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"
