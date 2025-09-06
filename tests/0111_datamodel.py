import pytest

from django_willpower.core import Application, Component, Module, DataModel, Field
from django_willpower.utils.parsing import WillpowerStringObject


def test_initialize_datamodel():
    """
    We expect no error on DataModel init if all required arguments are given.
    """
    # Without required arguments
    with pytest.raises(TypeError) as excinfo:
        DataModel()

    expect_msg = "required positional argument: 'name'"
    assert expect_msg in str(excinfo.value)

    # The righ way
    model = DataModel(name="DummyThing")
    assert model.name == "DummyThing"
    assert model.verbose_single == "dummything"
    assert model.verbose_plural == "dummythings"
    assert model.module_name == "dummything"
    assert model.module_filename == "dummything"


def test_initialize_field():
    """
    We except no error on Field init if all required arguments are given.
    """
    # Without required arguments
    with pytest.raises(TypeError) as excinfo:
        Field()

    expect_msg = "required positional argument: 'name'"
    assert expect_msg in str(excinfo.value)

    # The righ way
    field = Field(name="DummyThing")
    assert field.name == "DummyThing"
    assert field.modelfield_template == "models/fields/CharField.py"


def test_glue_modelfield():
    """
    Model and Field objects should be linked together.
    """
    # Create some model fields
    field_title = Field(name="title")
    field_content = Field(name="content")

    model = DataModel(name="Article", modelfields=[field_title])

    assert field_title.model.name == "Article"

    model.set_fields([field_content])

    assert field_content.model.name == "Article"

    assert [v.name for v in model.modelfields] == ["title", "content"]


def test_glue_appstack_modelfield():
    """
    Everything should be linked together.
    """
    # Create a full application stack
    app = Application(
        name="Blog",
        code="blog",
        destination="blog/",
        components=[
            Component(
                name="Views",
                code="views",
                modules=[
                    Module(
                        name="Detail",
                        code="detail",
                        template="detail.py",
                        destination_pattern="dummy/"
                    ),
                ],
            ),
        ],
    )

    # Create some model fields apart
    field_title = Field(name="title")
    field_content = Field(name="content")
    # Create model
    model = DataModel(name="Article", modelfields=[field_title, field_content])

    app.set_models([model])

    # Model is well linked to app
    assert model.app.code == "blog"
    # And so the field can reach up to app to dig into stack
    assert field_title.model.app.find("blog@views:detail").component.code == "views"


def test_modelfield_introspection():
    """
    Model should introspect its values and field values to find informations about
    some behaviors (imports, etc..)
    """
    # Create some model fields
    field_title = Field(name="title")
    field_content = Field(name="content", target="Nope")
    field_label = Field(
        name="label",
        target="w-object://datetime/datetime.now()",
    )
    field_author = Field(
        name="author",
        target="w-object://django.conf/settings/AUTH_USER_MODEL",
    )
    field_created = Field(
        name="created",
        default="w-object://django.utils/timezone/now",
    )
    field_publisher = Field(
        name="publisher",
        target="w-object://django.conf/settings/AUTH_USER_MODEL",
    )

    # Ensure everything is parsed as expected
    assert type(field_created.default) is WillpowerStringObject
    assert field_created.default.parsed_object == "timezone.now"

    assert type(field_content.target) is WillpowerStringObject
    assert field_content.target.parsed_object == "Nope"

    assert type(field_author.target) is WillpowerStringObject
    assert field_author.target.parsed_object == "settings.AUTH_USER_MODEL"

    assert type(field_publisher.target) is WillpowerStringObject
    assert field_publisher.target.parsed_object == "settings.AUTH_USER_MODEL"

    assert field_content.get_required_imports() == []
    assert field_author.get_required_imports() == [("django.conf", "settings")]
    assert field_publisher.get_required_imports() == [("django.conf", "settings")]

    # Set fields onto model
    model = DataModel(name="Article", modelfields=[
        field_title,
        field_content,
        field_created,
        field_label,
        field_author,
        field_publisher,
    ])

    # Find all implied imports from fields values
    assert model.get_required_imports() == [
        (None, "datetime"),
        ("django.conf", "settings"),
        ("django.utils", "timezone"),
    ]
