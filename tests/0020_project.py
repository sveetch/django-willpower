import pytest

from django_willpower.core import ProjectRegistry, Application, Component, Module


def test_register_application(settings, load_json):
    """
    We expect there is no error on Application init if all required arguments are
    given.
    """
    basic_appstack = load_json(
        settings.configs_path / "appstack_single_component/appstack.json"
    )
    dual_appstack = load_json(
        settings.configs_path / "appstack_dual_components/appstack.json"
    )

    project = ProjectRegistry()
    project.add_application(
        basic_appstack,
        settings.configs_path / "appstack_single_component"
    )
    project.add_application(
        dual_appstack,
        settings.configs_path / "appstack_dual_components"
    )

    assert len(basic_appstack["components"]) == len(
        project.apps["single-component"].components
    )
    assert len(dual_appstack["components"]) == len(
        project.apps["dual-components"].components
    )

    # Application code must be unique in registry
    with pytest.raises(ValueError) as excinfo:
        project.add_application(
            basic_appstack,
            settings.configs_path / "appstack_single_component"
        )

    expect_msg = "Given Application code is already registered: single-component"
    assert expect_msg == str(excinfo.value)


def test_registry_finding(settings, load_json):
    """
    Registry should find application, component or module from given stack path.
    """
    basic_appstack = load_json(
        settings.configs_path / "appstack_single_component/appstack.json"
    )
    dual_appstack = load_json(
        settings.configs_path / "appstack_dual_components/appstack.json"
    )

    project = ProjectRegistry()
    project.add_application(
        basic_appstack,
        settings.configs_path / "appstack_single_component"
    )
    project.add_application(
        dual_appstack,
        settings.configs_path / "appstack_dual_components"
    )

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
    found = project.find("dual-components@")
    print(found)
    assert found.code == "dual-components"

    # Finding component
    found = project.find("dual-components@applugins")
    assert found.code == "applugins"

    # Finding module
    found = project.find("single-component@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"


def test_register_shipped_configs(settings, load_json):
    """
    Shipped application configurations should not fail to be registered once their
    blank fields are filled.
    """
    project = ProjectRegistry()

    advanced_config = load_json(settings.data_path / "default_stack/appstack.json")

    # Application config must include a name, code and destination (shipped
    # configurations are blank)
    with pytest.raises(ValueError) as excinfo:
        project.add_application(advanced_config, settings.data_path / "default_stack")

    # Once correctly filled it just works
    project.add_application(
        advanced_config,
        settings.data_path / "default_stack/appstack.json",
        name="Sample",
        code="sample",
        destination="sample/",
    )

    found = project.find("sample@appviews:init")
    assert found.component.code == "appviews"
    assert found.code == "init"
