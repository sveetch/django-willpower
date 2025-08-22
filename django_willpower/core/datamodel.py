"""
.. Warning::
    Because these classes are connected together you will probably not be able to use
    ``dataclasses.asdict`` or ``dataclasses.astuple`` with any of them since these
    methods are recursive and would lead to a recursion limit error (because app A would
    include component Z that would link to app A that would include component Z, etc..).

    Cloning or copying datamodel object may lead to the same issue (unchecked yet).
"""
from dataclasses import (
    dataclass,
    field as dataclasses_field,
    fields as dataclasses_fields
)
from typing import Any

from ..utils.texts import text_to_module_name


@dataclass
class Field:
    """
    Define model field options

    There are many arguments but not all have meaning for all modules, some modules
    may use them or not.

    TODO: There may be too many attributes for various things, may be we should just
    move non essential ones to an attribute 'options' (dict). Beware of mutations.

    .. Todo::
        To be better we would need to make a dataclass for each field, this would be
        more accurate but would make more work opposed to this generic solution.

    Arguments:
        name (string):
    """
    name: str
    label: str = ""
    # Link to its DataModel
    model: Any = None
    # Should be required positionnal argument instead if we dont specialize fields
    # in multiple dataclasses
    kind: str = "CharField"
    modelfield_template: str = ""  # TODO Rename to just 'template'
    default: str = None  # Type should be UNION or ANY to allow for None
    required: bool = False
    nullable: bool = False
    unique: bool = False
    read_only: bool = False  # Not implemented in field templates
    related_to: str = None   # Type should be UNION or ANY to allow for None
    auto_creation: bool = False
    auto_update: bool = False
    min_value: int = None  # Type should be UNION or ANY to allow for None
    max_value: int = None  # Type should be UNION or ANY to allow for None
    # Target value allows for an optional pattern '{app}' to replace with model
    # application name
    # Empty target for a relation should be an error
    target: str = ""
    related_name: str = ""
    on_delete: str = ""
    # May be delegated elsewhere for a list of all displayed fields
    admin_display_in_change: bool = True
    # May be delegated elsewhere for a list of all displayed fields
    admin_display_in_list: bool = False
    # Commentary just for developer, not used in templates
    comment: str = ""
    # A list of choices
    choices_list: list[str] = dataclasses_field(default_factory=list)

    def __post_init__(self):
        """
        Initialize empty positionnal argument values.
        """
        if not self.modelfield_template:
            self.modelfield_template = "models/fields/{}.py".format(self.kind)

        if not self.label:
            self.label = self.name

        if self.target and self.model and self.model.app:
            self.target = self.target.format(app=self.model.app.code)

    def as_dict(self):
        """
        A safe way to convert to a dict without recursion issues.

        Returns:
            dict: ``model`` attribute is omitted.
        """
        return {
            f.name: getattr(self, f.name)
            for f in dataclasses_fields(self)
            if f.name != "model"
        }


@dataclass
class DataModel:
    """
    Model descriptor and its features for components.

    TODO: name should be validated to be a valid Python class name

    TODO: There may be too many attribute for various things, may be we should just
    move non essential ones to an attribute 'options' (dict) or 'admin_options',
    'view_options', etc.. Beware of mutations.

    Arguments:
        name (string): The model name. Commonly it should start with an uppercase
            alphabet character.
        **kwargs: All non positionnal arguments are automatically filled if empty.

    Keyword Arguments:
        app (Application): The application object which this model is linked to.

    """
    # The model class name
    name: str
    # Link to its Application
    app: Any = None
    # The verbose label in single and plural forms
    verbose_single: str = ""
    verbose_plural: str = ""
    # List of Field objects to define model fields
    modelfields: list[Field] = dataclasses_field(default_factory=list)
    # List of model inline admin classes to include
    admin_inline_models: list[str] = dataclasses_field(default_factory=list)
    # Define if model should provide an inline admin (NOT IMPLEMENTED YET)
    provide_inline: bool = False
    # Default order to define in model and to apply in views
    default_order: list[str] = dataclasses_field(default_factory=list)
    # The fields where to performing search like for admin or generate haystack index
    search_fields: list[str] = dataclasses_field(default_factory=list)
    # List of read only field names
    readonly_fields: list[str] = dataclasses_field(default_factory=list)
    # List of field prepopulation
    prepopulated_fields: dict = dataclasses_field(default_factory=dict)
    # List of field autocompleted relation fields
    autocompleted_fields: list = dataclasses_field(default_factory=list)
    # For the admin only
    list_filter: list[str] = dataclasses_field(default_factory=list)
    # Usually only for admin
    admin_list_display: list[str] = dataclasses_field(default_factory=list)
    # Common name for a Python module or Python variable
    module_name: str = ""
    module_name_plural: str = ""
    module_filename: str = ""
    # Components names, empty component name will be built from name if empty
    admin_name: str = ""
    admin_form_name: str = ""
    factory_name: str = ""
    form_name: str = ""
    # Is a pattern of a pattern, it must include a '{{}}' that will be replaced with
    # the component name
    view_basename: str = ""
    # Model attribute to use as string representation ('__str__')
    # Can be a string for a Model attribute to use or a list for model attributes to
    # join with a whitespace
    string_representation: str = ""

    def __post_init__(self):
        """
        Initialize empty positionnal argument value except if they are none which is
        assumed to avoid a component.
        """
        if not self.verbose_single:
            self.verbose_single = self.name.lower()

        if not self.verbose_plural:
            self.verbose_plural = self.verbose_single + "s"

        if not self.module_name:
            self.module_name = text_to_module_name(self.name)

        if not self.module_name_plural:
            self.module_name_plural = self.module_name + "s"

        if not self.module_filename and self.module_filename is not None:
            self.module_filename = self.module_name

        if not self.admin_name and self.admin_name is not None:
            self.admin_name = "{}Admin".format(self.name)

        if not self.admin_form_name and self.admin_form_name is not None:
            self.admin_form_name = "{}AdminForm".format(self.name)

        if not self.factory_name and self.factory_name is not None:
            self.factory_name = "{}Factory".format(self.name)

        if not self.form_name and self.form_name is not None:
            self.form_name = "{}Form".format(self.name)

        if not self.view_basename and self.view_basename is not None:
            self.view_basename = "{}{{}}View".format(self.name)

        # Automatically link fields
        self.set_fields(self.modelfields, from_init=True)

    def set_fields(self, fields, from_init=False):
        """
        Append items to model fields while linking them to this model.
        """
        for item in fields:
            item.model = self

        if not from_init:
            self.modelfields.extend(fields)

    def as_dict(self):
        """
        Safe way to convert to a dict without recursion issues.

        Returns:
            dict: ``app`` attribute is omitted and ``modelfields`` items are serialized
            using their ``as_dict()`` method.
        """
        return {
            f.name: (
                getattr(self, f.name)
                if f.name != "modelfields"
                else [c.as_dict() for c in getattr(self, f.name)]
            )
            for f in dataclasses_fields(self)
            if f.name != "app"
        }
