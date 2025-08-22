import json

from pathlib import Path
from dataclasses import asdict

import pytest

from django_willpower.core import Application, Component, Module
from django_willpower.utils.jsons import ExtendedJsonEncoder


def test_initialize_application(tmp_path):
    """
    We except no error on Application init if all required arguments are given.
    """
    # Without required arguments
    with pytest.raises(TypeError) as excinfo:
        Application()

    expect_msg = "required positional arguments: 'name' and 'code'"
    assert expect_msg in str(excinfo.value)

    # The righ way
    app = Application(name="Dummy", code="dummy")
    assert app.code == "dummy"


def test_initialize_component():
    """
    We except no error on Component init if all required arguments are given.
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
    We except no error on Module init if all required arguments are given.
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


def test_appstack_glue(settings):
    """
    The application stack should be correctly initialized with deep linking and a
    safe way to represent it as a dict.
    """
    # Build application just like from data fixture single_component appstack
    view_module = Module(
        name="Views module",
        code="module",
        template="views/module.py",
        destination_pattern="{model}.py",
    )

    view_init = Module(
        name="Views init",
        code="init",
        template="views/__init__.py",
        destination_pattern="__init__.py",
        once=True,
    )

    basic_app = Application(
        name="Single component",
        code="single-component",
        destination="single-component",
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
    assert [v.app.code for v in basic_app.components] == ["single-component"]

    # App can reach all its components modules
    mods = []
    for item in basic_app.components:
        mods.extend([k for k in item.modules])
    assert [v for v in mods] == [view_module, view_init]

    # Recursion error is expected with 'dataclasses.asdict' or 'dataclasses.astuple'
    with pytest.raises(RecursionError):
        asdict(basic_app)

    # print(json.dumps(basic_app.as_dict(), indent=4))

    # Reversing registered app returns identical config (if default values was defined)
    serialized = json.loads(json.dumps(basic_app.as_dict(), cls=ExtendedJsonEncoder))
    assert serialized == json.loads((
        settings.configs_path / "appstack_single_component/appstack.json"
    ).read_text())

    # Each object can return a path to reach them
    assert basic_app.get_path() == "single-component"
    assert view_module.get_path() == "single-component@appviews:module"
    assert view_init.get_path() == "single-component@appviews:init"


def test_finding(settings):
    """
    Application should find component or module from given stack path.
    """
    basic_app = Application(
        name="Single component",
        code="single-component",
        destination="single-component/",
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
                        destination_pattern="{model}.py",
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
        basic_app.find("nope@appviews:init")

    expect_msg = "Path is searching for app 'nope' in Application 'single-component'"
    assert expect_msg == str(excinfo.value)

    # Empty component part
    with pytest.raises(ValueError) as excinfo:
        basic_app.find("single-component@:nope")

    expect_msg = "Empty component part is not allowed"
    assert expect_msg == str(excinfo.value)

    # Unknow component from application
    with pytest.raises(ValueError) as excinfo:
        basic_app.find("nope:init")

    expect_msg = "Component 'nope' does not exist"
    assert expect_msg == str(excinfo.value)

    # Unknow module from component
    with pytest.raises(ValueError) as excinfo:
        basic_app.find("single-component@appviews:nope")

    expect_msg = "Module 'nope' does not exist for component 'appviews'"
    assert expect_msg == str(excinfo.value)

    # Finding component
    assert basic_app.find("single-component@appviews").code == "appviews"

    # Finding module
    found = basic_app.find("single-component@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"

    # Finding component (without useless application part)
    found = basic_app.find("appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"


def test_load_models(settings):
    """
    Models should be correctly loaded in Application from a dict.
    """
    models_payload = json.loads((
        settings.fixtures_path / "config_samples/models_basic_blog.json"
    ).read_text())

    basic_app = Application(name="Blog", code="blog", destination="blog/")

    basic_app.load_models(models_payload)
    # print(json.dumps(basic_app.as_dict(), indent=4))

    assert basic_app.models[0].app.code == basic_app.code
    assert [v.name for v in basic_app.models] == ["Blog", "Article"]

    assert basic_app.get_model("Blog").readonly_fields == ["created"]


def test_get_destination():
    """
    Method 'get_destination' from dataclasses should resolve their full destination
    path when they are correctly linked to their parent.
    """
    # Craft independant modules
    view_module = Module(
        name="Views module",
        code="module",
        template="views/module.py",
        destination_pattern="{model}.py",
    )

    view_init = Module(
        name="Views init",
        code="init",
        template="views/__init__.py",
        destination_pattern="__init__.py",
        once=True,
    )

    # Method need object to be linked to component
    with pytest.raises(ValueError) as excinfo:
        view_module.get_destination()

    expect_msg = (
        "A module without link to component can not use the method "
        "'get_destination()'"
    )
    assert expect_msg == str(excinfo.value)

    # Craft independant component but link modules
    view_component = Component(
        name="Application views",
        code="appviews",
        directory="views",
        modules=[view_module, view_init],
    )

    # Method need object to be linked to application
    with pytest.raises(ValueError) as excinfo:
        view_component.get_destination()

    expect_msg = (
        "A component without link to application can not use the method "
        "'get_destination()'"
    )
    assert expect_msg == str(excinfo.value)

    # Craft application and link component
    basic_app = Application(
        name="Single component",
        code="single-component",
        destination="single-component",
        components=[view_component],
    )

    assert basic_app.get_destination() == Path("single-component")
    assert view_component.get_destination() == Path("single-component/views")

    # Without context destination formatting patterns won't be resolved
    assert view_module.get_destination() == Path(
        "single-component/views/{model}.py"
    )

    # Once context include required pattern values they are resolved
    assert view_module.get_destination({"model": "foo"}) == Path(
        "single-component/views/foo.py"
    )
