from dataclasses import dataclass, field, asdict


@dataclass
class Module:
    """
    Module type for a component.

    Arguments:
        name (string): Label name
        code (string): Unique (amongst all component modules) code name (used
            internally)
        template (string): The template to render to build module
        destination_pattern (string): A pattern to build the module name for each
            model. It can contains a pattern item ``{modelname}`` that will be replaced
            by the Model name from a declaration. If attribute ``once`` is true, there
            should be not pattern item ``{modelname}`` because it is not expected to
            be built for each model and so the pattern item won't be resolved and left
            unchanged in final destination path.
        once (bool): If true the module is to be built once for all models. Default
            value is false so the module is build for each model.
    """
    name: str
    code: str
    template: str
    destination_pattern: str
    once: bool = False


@dataclass
class Component:
    """
    An application component.

    Arguments:
        name (string): Label name
        code (string): Unique (amongst all components) code name (used internally)
        directory (string): Directory name where to write modules. May be empty for
            some specific component like search or urls that have only a single module
            to write at application root but be careful to not overwrite other modules.
        modules (list): List of Module objects.
    """
    name: str
    code: str
    directory: str
    modules: list[Module] = field(default_factory=list)


@dataclass
class FieldModel:
    """
    Define model field options

    There are many arguments but not all have meaning for all modules, some modules
    may use them or not.

    .. Todo::
        To be better we would need to make a dataclass for each field, this would be
        more accurate but would make more work opposed to this generic solution.

    Arguments:
        name (string):
    """
    name: str
    label: str = ""
    kind: str = "CharField"
    default: str = None  # Type should be UNION or ANY to allow for None
    required: bool = False
    nullable: bool = False
    unique: bool = False
    read_only: bool = False
    related_to: str = None  # Type should be UNION or ANY to allow for None
    display_in_admin_change: bool = True
    display_in_admin_list: bool = False
    auto_creation: bool = False
    auto_update: bool = False
    modelfield_template: str = ""
    min_value: int = None  # Type should be UNION or ANY to allow for None
    max_value: int = None  # Type should be UNION or ANY to allow for None
    target: str = "" # Empty target for a relation should be an error
    related_name: str = ""
    on_delete: str = ""

    def __post_init__(self):
        """
        Initialize empty positionnal argument values.
        """
        if not self.modelfield_template:
             self.modelfield_template = "models/fields/{}.py".format(self.kind)

        if not self.label:
             self.label = self.name


@dataclass
class ModelInventory:
    """
    Model descriptor and its features for components.

    Arguments:
        app (string): The model application module name.
        name (string): The model name. Commonly it should start with an uppercase
            alphabet character.
        **kwargs: All non positionnal arguments are automatically built if empty.
    """
    # The application name this model belong to
    app: str
    # The model name
    name: str
    # Default order to define in model and to apply in views
    default_order: list[str] = field(default_factory=list)
    # The model fields
    modelfields: list[FieldModel] = field(default_factory=list)
    # Common name for the Python module of components
    module_name: str = ""
    module_filename: str = ""
    # Components names, empty component name will be build from name if empty
    admin_name: str = ""
    admin_form_name: str = ""
    factory_name: str = ""
    form_name: str = ""
    view_basename: str = "" # Is a pattern of a pattern, it must include a '{{}}'

    def __post_init__(self):
        """
        Initialize empty positionnal argument value except if they are none which is
        assumed to avoid a component.

        NOTE: Not all these args should be optional with null value.
        """
        if not self.module_name:
             self.module_name = self.name.lower()

        if not self.module_filename and self.module_filename is not None:
             self.module_filename = "{}".format(self.module_name)

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
