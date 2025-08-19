"""
.. Warning::
    Because datamodels are connected each other you will probably not be able to use
    ``dataclasses.asdict`` or ``dataclasses.astuple`` with any of them since these
    methods are recursive and would lead to a recursion limit error (because app A would
    include component Z that would link to app A that would include component Z, etc..).

    Cloning or copying datamodel object may lead to the same issue (unchecked yet).
"""
from dataclasses import dataclass, field, fields as dataclasses_fields
from pathlib import Path
from typing import Any

from ..utils.stackpath import split_stack_path
from .datamodel import Field, DataModel


@dataclass
class Application:
    """
    Application for Components.

    Arguments:
        name (string): Label name
        code (string): Unique (amongst all application modules) code name.
        destination (string): Destination path where all application components will be
            created. This is a relative path to the project directory.

    Keyword Arguments:
        template_dir (pathlib.Path): Although it is an optional argument it must be
            filled to be processed in builder. It is likely to be defined during
            application registering.
        components (string): List of enabled Component objects. May be empty on
            initialize and filled just after.
        models (string): List of DataModel objects. May be empty on
            initialize and filled just after.
    """
    name: str
    code: str
    destination: str = ""
    template_dir: Path = None
    components: list[Any] = field(default_factory=list)
    models: list[Any] = field(default_factory=list)

    def __post_init__(self):
        if ":" in self.code or "@" in self.code:
            msg = "Application.code can not contain characters ':' or '@': {}"
            raise ValueError(msg.format(self.code))

        # Automatically link sub objects relations
        self.set_components(self.components, from_init=True)
        self.set_models(self.models, from_init=True)

    def get_destination(self, context=None):
        """
        Return the full (from app directory) component directory.

        Keyword Arguments:
            context (dict): This argument exist for signature compatibility with other
                ``get_destination`` method but is never used.

        Returns:
            pathlib.Path: The full destination path.
        """
        return Path(self.destination)

    def get_path(self):
        """
        Return object path in the application tree.

        Returns:
            string: Just this application code because at this point of tree there is
                nothing higher.
        """
        return self.code

    def as_dict(self):
        """
        A safe way to convert to a dict without recursion issues.

        Returns:
            dict: ``components`` item are serialized using their ``as_dict()`` method.
        """
        return {
            f.name: (
                getattr(self, f.name)
                if f.name not in ["components", "models"]
                else [c.as_dict() for c in getattr(self, f.name)]
            )
            for f in dataclasses_fields(self)
        }

    def set_components(self, components, from_init=False):
        """
        Append items to components while linking them to this Application.

        Arguments:
            components (list): List of Component objects.

        Keyword Arguments:
            from_init (bool): If true this will not append objects to
                ``Application.components`` list. This is only useful when calling this
                method from class init and avoid recursion. Default value is false.
        """
        for item in components:
            item.app = self

        if not from_init:
            self.components.extend(components)

    def set_models(self, models, from_init=False):
        """
        Append items to models while linking them to this Application.

        Arguments:
            models (list): List of DataModel objects.

        Keyword Arguments:
            from_init (bool): If true this will not append objects to
                ``Application.models`` list. This is only useful when calling this
                method from class init and avoid recursion. Default value is false.
        """
        for item in models:
            item.app = self

        if not from_init:
            self.models.extend(models)

    def load_models(self, declarations):
        """
        Load and set DataModel and Field objects from a declaration dict.

        Arguments:
            declarations (dict): A dictionnary of Model declarations.

        Returns:
            list: A list of ``DataModel`` objects with their ``Field`` objects for
            defined model declarations.
        """
        for modelname, modelopts in declarations.items():
            model = DataModel(
                app=self.name,
                name=modelname,
                # Load fields as Field object
                modelfields=[
                    Field(name=fieldname, **fieldopts)
                    for fieldname, fieldopts in modelopts["fields"].items()
                ],
                # All other model items are passed as keyword arguments however
                # they must be defined as datamodel attribute before.
                **{
                    k: v
                    for k, v in modelopts.items()
                    if k != "fields"
                }
            )
            self.set_models([model])

    def get_model(self, name, **kwargs):
        """
        Get a single model from its name.

        Arguments:
            name (string): Model name.

        Keyword Arguments:
            default (any): Default value to return in case of missing model name. If
                not given a missing model name will raise a ``IndexError`` exception.
        """
        for item in self.models:
            if item.name == name:
                return item

        if "default" in kwargs:
            return kwargs["default"]
        else:
            raise IndexError("There is no model with name: {}".format(name))

    def find(self, path):
        """
        Find a component or a module for this application following a path.

        .. Note::
            Although the application part is accepted, it is useless in the context of
            an application itself. However it is validated.

        Arguments:
            path (string): Path pattern is expected to be: ::

                    [app@]component[:module]

                Where ``app@`` is the application part (ignored) and ``:module`` the
                module part. The only required part is the component.

        Returns:
            object: Depending on given path it may returns:

                * A Component object if no module was in path;
                * A Module object if there was a correct module in path following the
                  component part;

                It won't never return an Application object because it is ignored
                excepted if application code does not match the current one.

                Finally if Component code can not be retrieved from this application or
                if module can not be retrieved for a component from this application
                this will raise an error.
        """
        app, component, module = split_stack_path(path)
        found_component = None
        found_module = None

        # Validate application
        if app and app != self.code:
            msg = "Path is searching for app '{given}' in Application '{current}'"
            raise ValueError(msg.format(given=app, current=self.code))

        # Validate component
        if not component:
            raise ValueError("Empty component part is not allowed")
        elif component not in [v.code for v in self.components]:
            raise ValueError("Component '{}' does not exist".format(component))

        # Find component
        for v in self.components:
            if v.code == component:
                found_component = v
                break

        # If there is no module part return the component
        if not module:
            return found_component

        # Find module from found component
        for v in found_component.modules:
            if v.code == module:
                found_module = v
                break

        # If module does not exist from found component
        if not found_module:
            msg = "Module '{}' does not exist for component '{}'"
            raise ValueError(msg.format(module, component))

        return found_module


@dataclass
class Component:
    """
    An application component.

    Arguments:
        name (string): Label name
        code (string): Unique (amongst all components) code name (used internally)

    Keyword Arguments:
        directory (string): Directory name where to write modules. May be empty for
            some specific component like search or urls that have only a single module
            to write at application root but be careful to not overwrite other modules.
        app (Application): Application which this Component is linked to.
        modules (list): List of Module objects.
    """
    name: str
    code: str
    directory: str = ""
    app: Any = field(default=None, repr=False)
    modules: list[Any] = field(default_factory=list)

    def __post_init__(self):
        if ":" in self.code or "@" in self.code:
            msg = "Component.code can not contain characters ':' or '@': {}"
            raise ValueError(msg.format(self.code))

        # Automatically link modules
        self.set_modules(self.modules, from_init=True)

    def set_modules(self, modules, from_init=False):
        """
        Append to modules while linking them to this component.

        Arguments:
            modules (list): List of Module objects.

        Keyword Arguments:
            from_init (bool): If true this will not append objects to
                ``Component.modules`` list. This is only useful when calling this
                method from class init and avoid recursion. Default value is false.
        """
        for item in modules:
            item.component = self

        if not from_init:
            self.modules.extend(modules)

    def get_destination(self, context=None):
        """
        Return the full (from app directory) component directory.

        Keyword Arguments:
            context (dict): This argument exist for signature compatibility with other
                ``get_destination`` method but is never used.

        Returns:
            pathlib.Path: The full destination path from the application to this
            component.
        """
        if not self.app:
            raise ValueError(
                "A component without link to application can not use the method '{}'".format(
                    "get_destination()"
                )
            )

        return self.app.get_destination() / self.directory

    def get_path(self):
        """
        Return object path in the application tree.

        Returns:
            string: The application code followed by this object code, divided by
                ``@`` character.
        """
        return "{app}@{component}".format(
            app=(self.app.get_path() if self.app else "null"),
            component=self.code,
        )

    def as_dict(self):
        """
        Safe way to convert to a dict without recursion issues.

        Returns:
            dict: ``app`` attribute is omitted and ``modules`` items are serialized
            using their ``as_dict()`` method.
        """
        return {
            f.name: (
                getattr(self, f.name)
                if f.name != "modules"
                else [c.as_dict() for c in getattr(self, f.name)]
            )
            for f in dataclasses_fields(self)
            if f.name != "app"
        }


@dataclass
class Module:
    """
    Module for a component.

    Arguments:
        name (string): Label name
        code (string): Unique (amongst all component modules) code name (used
            internally)
        template (string): The template to render to build module
        destination_pattern (string): A pattern to build the module name for each
            model. It can contains a pattern item ``{modelname}`` that will be replaced
            by the Model name from a declaration. If attribute ``once`` is true, it
            should no include pattern ``{modelname}`` because it is expected to
            be built outside a model and so the pattern item will still left
            unchanged in final destination path.

    Keyword Arguments:
        once (bool): If true the module is to be built once for all models. Default
            value is false so the module is build for each model.
        component (Component): Component which this Module is linked to.
    """
    name: str
    code: str
    template: str
    destination_pattern: str
    once: bool = False
    component: Any = field(default=None, repr=False)

    def __post_init__(self):
        if ":" in self.code or "@" in self.code:
            msg = "Module.code can not contain characters ':' or '@': {}"
            raise ValueError(msg.format(self.code))

    def get_destination(self, context=None):
        """
        Return the full (from app directory) module directory with patterns resolved.

        Keyword Arguments:
            context (dict): A dictionnary of pattern values for formatting destination.

        Returns:
            pathlib.Path: The full destination path from the application to this module.
        """
        if not self.component:
            raise ValueError(
                "A module without link to component can not use the method '{}'".format(
                    "get_destination()"
                )
            )
        context = context or {}

        if not context:
            path = self.destination_pattern
        else:
            path = self.destination_pattern.format(**context)

        return self.component.get_destination() / path

    def get_path(self):
        """
        Return object path in the application tree.

        Returns:
            string: The component path followed by this object code, divided by
                ``:`` character.
        """
        return "{component_path}:{module}".format(
            component_path=(self.component.get_path() if self.component else "null"),
            module=self.code,
        )

    def as_dict(self):
        """
        A safe way to convert to a dict without recursion issues.

        Returns:
            dict: ``component`` attribute is omitted.
        """
        return {
            f.name: getattr(self, f.name)
            for f in dataclasses_fields(self)
            if f.name != "component"
        }
