from dataclasses import dataclass, field, asdict


@dataclass
class FieldModel:
    """
    A model field descriptor.

    Arguments:
        name (string):
    """
    name: str
    kind: str = "varchar"
    display_in_admin_change: bool = True
    display_in_admin_list: bool = False
    read_only: bool = False
    required: bool = False
    related_to: str = None
    default: str = None


@dataclass
class ModelInventory:
    """
    Model descriptor and its features for components.

    Arguments:
        app (string): The model application module name.
        name (string): The model name. Commonly it should start with an uppercase
            alphabet character.
    """
    # The application name this model belong to
    app: str
    # The model name
    name: str
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
    # Optional API stuff
    serializer_name: str = ""
    # Optional DjangoCMS stuff
    cmsplugin_name: str = ""
    cmsplugin_model_name: str = ""

    def __post_init__(self):
        """
        Initialize empty positionnal argument value except if they are none which is
        assumed to avoid a component.

        NOTE: Not all these args should be optional with null value.
        """
        if not self.module_name and self.module_name is not None:
             self.module_name = self.name.lower()

        if not self.module_filename and self.module_filename is not None:
             self.module_filename = "{}.py".format(self.module_name)

        if not self.admin_name and self.admin_name is not None:
             self.admin_name = "{}Admin".format(self.name)

        if not self.admin_form_name and self.admin_form_name is not None:
             self.admin_form_name = "{}AdminForm".format(self.name)

        if not self.factory_name and self.factory_name is not None:
             self.factory_name = "{}Factory".format(self.name)

        if not self.form_name and self.form_name is not None:
             self.form_name = "{}Form".format(self.name)

        if not self.serializer_name and self.serializer_name is not None:
             self.serializer_name = "{}Serializer".format(self.name)

        if not self.cmsplugin_name and self.cmsplugin_name is not None:
             self.cmsplugin_name = "{}Plugin".format(self.name)

        if not self.cmsplugin_model_name and self.cmsplugin_model_name is not None:
             self.cmsplugin_model_name = "{}PluginModel".format(self.name)

        if not self.view_basename and self.view_basename is not None:
             self.view_basename = "{}{{}}View".format(self.name)
