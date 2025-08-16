"""
NOTE: This is the new to modelize application stack and should replace the old ones
from "available_components" once finished.

.. Warning::
    Because datamodels are connected each other you will probably not be able to use
    ``dataclasses.asdict`` or ``dataclasses.astuple`` with any of them since these
    methods are recursive and would lead to a recursion limit error (because app A would
    include component Z that would link to app A that would include component Z, etc..).

    Cloning or copying datamodel object may lead to the same issue (unchecked yet).
"""
from dataclasses import dataclass, field, fields as get_fields
from pathlib import Path
from typing import Any

from ..utils.stackpath import split_stack_path


@dataclass
class Application:
    """
    Application for Components.

    Arguments:
        name (string): Label name
        code (string): Unique (amongst all application modules) code name.
        destination (string):

    Keyword Arguments:
        components (string): List of enabled Component objects. May be empty on
            initialize and filled just after.
    """
    name: str
    code: str
    destination: Path
    components: list[Any] = field(default_factory=list)

    def __post_init__(self):
        if ":" in self.code or "@" in self.code:
            msg = "Application.code can not contain characters ':' or '@': {}"
            raise ValueError(msg.format(self.code))

        # Automatically link components
        self.set_components(self.components, from_init=True)

    def set_components(self, components, from_init=False):
        """
        Append to components while linking them to this Application.
        """
        for item in components:
            item.app = self

        if not from_init:
            self.components.extend(components)

    def get_path(self):
        """
        Return object path in the application tree.

        Returns:
            string: Just this application code because at this point of tree there is
                nothing higher.
        """
        return self.code

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

    def as_dict(self):
        """
        A safe way to convert to a dict without recursion issues.

        Returns:
            dict: ``components`` item are serialized using their ``as_dict()`` method.
        """
        return {
            f.name: (
                getattr(self, f.name)
                if f.name != "components"
                else [c.as_dict() for c in getattr(self, f.name)]
            )
            for f in get_fields(self)
        }


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
        """
        for item in modules:
            item.component = self

        if not from_init:
            self.modules.extend(modules)

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
            for f in get_fields(self)
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
            for f in get_fields(self)
            if f.name != "component"
        }
