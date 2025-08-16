import json

from pathlib import Path
from dataclasses import asdict

import pytest

from django_willpower.core import Application, Component, Module


def test_initialize_application(tmp_path):
    """
    We except there is no error on Application init if all required arguments are
    given.
    """
    # Without required arguments
    with pytest.raises(TypeError) as excinfo:
        Application()

    expect_msg = "required positional arguments: 'name', 'code', and 'destination'"
    assert expect_msg in str(excinfo.value)

    # The righ way
    app = Application(name="Dummy", code="dummy", destination=tmp_path)
    assert app.code == "dummy"


def test_initialize_component():
    """
    We except there is no error on Component init if all required arguments are
    given.
    """
    # Without required arguments
    with pytest.raises(TypeError) as excinfo:
        Component()

    expect_msg = "required positional arguments: 'name' and 'code'"
    assert expect_msg in str(excinfo.value)

    # The righ way
    app = Component(name="Dummy", code="dummy")
    assert app.code == "dummy"


def test_initialize_module():
    """
    We except there is no error on Module init if all required arguments are
    given.
    """
    # Without required arguments
    with pytest.raises(TypeError) as excinfo:
        Module()

    expect_msg = (
        "required positional arguments: 'name', 'code', 'template', and "
        "'destination_pattern'"
    )
    assert expect_msg in str(excinfo.value)

    # The righ way
    app = Module(
        name="Dummy",
        code="dummy",
        template="dummy.html",
        destination_pattern="dummy/"
    )
    assert app.code == "dummy"


def test_initialize_appstack(settings):
    """
    The application stack should be correctly initialized with deep linking and a
    safe way to represent it as a dict.
    """
    # Build application just like from data fixture 'blog.json'
    view_module = Module(
        name="Views module",
        code="module",
        template="views/module.py",
        destination_pattern="{modelname}.py",
    )

    view_init = Module(
        name="Views init",
        code="init",
        template="views/__init__.py",
        destination_pattern="__init__.py",
        once=True,
    )

    blog_app = Application(
        name="Blog",
        code="blog",
        destination="blog/",
        components=[
            Component(
                name="Application views",
                code="appviews",
                directory="views",
                modules=[view_module, view_init],
            ),
        ],
    )

    # Module can reach up to its component app
    assert [v.app.code for v in blog_app.components] == ["blog"]

    # App can reach all its components modules
    mods = []
    for item in blog_app.components:
        mods.extend([k for k in item.modules])
    assert [v for v in mods] == [view_module, view_init]

    # Recursion error is expected with 'dataclasses.asdict' or 'dataclasses.astuple'
    with pytest.raises(RecursionError):
        asdict(blog_app)

    # print(json.dumps(blog_app.as_dict(), indent=4))

    # Reversing registered app returns identical config (if default values was defined)
    assert blog_app.as_dict() == json.loads((
        settings.fixtures_path / "appstack_samples/blog.json"
    ).read_text())

    # Each object can return a path to reach them
    assert blog_app.get_path() == "blog"
    assert view_module.get_path() == "blog@appviews:module"
    assert view_init.get_path() == "blog@appviews:init"


def test_finding(settings):
    """
    Application should find component or module from given stack path.
    """
    blog_app = Application(
        name="Blog",
        code="blog",
        destination="blog/",
        components=[
            Component(
                name="Application views",
                code="appviews",
                directory="views",
                modules=[
                    Module(
                        name="Views module",
                        code="module",
                        template="views/module.py",
                        destination_pattern="{modelname}.py",
                    ),
                    Module(
                        name="Views init",
                        code="init",
                        template="views/__init__.py",
                        destination_pattern="__init__.py",
                        once=True,
                    ),
                ],
            ),
        ],
    )

    # Application part is optional but validated
    with pytest.raises(ValueError) as excinfo:
        blog_app.find("nope@appviews:init")

    expect_msg = "Path is searching for app 'nope' in Application 'blog'"
    assert expect_msg == str(excinfo.value)

    # Empty component part
    with pytest.raises(ValueError) as excinfo:
        blog_app.find("blog@:nope")

    expect_msg = "Empty component part is not allowed"
    assert expect_msg == str(excinfo.value)

    # Unknow component from application
    with pytest.raises(ValueError) as excinfo:
        blog_app.find("nope:init")

    expect_msg = "Component 'nope' does not exist"
    assert expect_msg == str(excinfo.value)

    # Unknow module from component
    with pytest.raises(ValueError) as excinfo:
        blog_app.find("blog@appviews:nope")

    expect_msg = "Module 'nope' does not exist for component 'appviews'"
    assert expect_msg == str(excinfo.value)

    # Finding component
    assert blog_app.find("blog@appviews").code == "appviews"

    # Finding module
    found = blog_app.find("blog@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"

    # Finding component (without useless application part)
    found = blog_app.find("appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"
