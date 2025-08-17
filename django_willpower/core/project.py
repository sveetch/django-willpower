"""
NOTE: This is the new to modelize application stack and should replace registry once
finished.

"""
from ..utils.stackpath import split_stack_path

from .appstack import Application, Component, Module


class ProjectRegistry:
    """
    Register application structures.

    Attributes:
        apps (dict): A dictionnary of registered ``Application`` objects.
    """
    def __init__(self, apps=None):
        self.apps = apps or {}

    def add_application(self, appconfig, name=None, code=None, destination=None):
        """
        Add a new application structure configuration.

        Arguments:
            appconfig (dict): Application config with its possible components and
                modules.

        Keyword Arguments:
            name (string):
            code (string):
            destination (pathlib.Path):
        """
        if name:
            appconfig["name"] = name

        if code:
            appconfig["code"] = code

        if destination:
            appconfig["destination"] = destination

        # Validate required application items
        if(
             not appconfig.get("name")
             or not appconfig.get("code")
             or not appconfig.get("destination")
        ):
            raise ValueError((
                "Application configuration must include a non empty 'name', 'code' "
                "and 'destination'."
            ))
        elif appconfig.get("code") in self.apps:
            msg = "Given Application code is already registered: {}"
            raise ValueError(msg.format(appconfig.get("code")))

        code_key = appconfig["code"]

        # First register the application without components
        self.apps[code_key] = Application(**{
            k: v
            for k, v in appconfig.items()
            if k != "components"
        })

        # Then walk through components
        for component in appconfig.get("components", []):
            # Bind component item to a Component object
            cpt_object = Component(**{
                k: v
                for k, v in component.items()
                if k != "modules"
            })

            # Bind component modules as Module object and link them to the component
            for module in component.get("modules", []):
                cpt_object.set_modules([Module(**{
                    k: v
                    for k, v in module.items()
                })])

            # Link component to application
            self.apps[code_key].set_components([cpt_object])

    def find(self, path):
        """
        Find a component or a module for this application following a path.

        Arguments:
            path (string): Path pattern is expected to be: ::

                    app@[component[:module]]

                Where ``app@`` is the application part, ``:component`` the component
                part and ``:module`` the module part. The application is only
                required part.

        Returns:
            object: Depending on given path it may returns:

                * An Application object if no component and no module was in path;
                * A Component object if no module was in path;
                * A Module object if there was a correct module in path following the
                  component part and the application part;

                Finally if part can not be retrieved from registry this will raise an
                error.
        """
        app, component, module = split_stack_path(path)

        # Validate application
        if not app:
            raise ValueError("Empty application part is not allowed")
        elif app not in self.apps:
            raise ValueError("Application '{}' is not registered".format(app))
        # Just searching for an application
        elif not component and not module:
            return self.apps[app]

        # Delegate Component and Module search to 'Application.find()'
        return self.apps[app].find(path)
