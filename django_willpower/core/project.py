import json
from pathlib import Path

from ..utils.stackpath import split_stack_path
from ..exceptions import ProjectValidationError
from .appstack import Application, Component, Module


class ProjectRegistry:
    """
    Register application structures.

    Attributes:
        apps (dict): A dictionnary of registered ``Application`` objects.
    """
    # Required field for an 'apps' item
    _APP_CONF_REQUIRED_ITEMS = [
        "appstack",
        "declarations",
        "destination",
        "name",
        "template_dir",
    ]

    def __init__(self, apps=None):
        self.apps = apps or {}

    def add_application(self, appconfig, template_dir, name=None, code=None,
                        destination=None):
        """
        Add a new application structure configuration.

        Arguments:
            appconfig (dict): Application config with its possible components and
                modules.
            template_dir (pathlib.Path): Directory where to search for templates. This
                should be an absolute path.

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

        # Template directory is resolved and will be set onto Application object.
        appconfig["template_dir"] = Path(template_dir).resolve()
        if not appconfig["template_dir"].exists():
            msg = (
                "Template directory of application '{}' does not exists: {}"
            )
            raise ProjectValidationError(msg.format(
                appconfig["name"],
                appconfig["template_dir"],
            ))

        # Validate required application items
        if(
             not appconfig.get("name")
             or not appconfig.get("code")
             or not appconfig.get("destination")
        ):
            raise ProjectValidationError((
                "Application configuration must include a non empty 'name', 'code' "
                "and 'destination'."
            ))
        elif appconfig.get("code") in self.apps:
            msg = "Given Application code is already registered: {}"
            raise ProjectValidationError(msg.format(appconfig.get("code")))

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

    def add_app_models(self, appcode, models):
        """
        Load and link models to an application.

        Arguments:
            appcode (string):
            models (dict):
        """
        self.apps[appcode].load_models(models)

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

    def load_configuration(self, payload):
        """
        Load and validate a project configuration.

        NOTE: We skip the real deep validation for now, we should do it probably with a
        JSON schema and the right library.

        Arguments:
            payload (any): Either a ``pathlib.Path object`` for a file to unserialize
                to a dictionnary or directly a dictionnary. Finally the dictionnary
                must follows the following structure: ::

                    {
                        "apps": {
                            <CODE>: {
                                "name": <NAME>,
                                "destination": <DESTINATION>,
                                "template_dir": <TEMPLATEDIR>,
                                "declarations": <MODELS>,
                                "appstack": <APPSTACK>
                            },
                        }
                    }

                Where:

                * ``CODE`` (string) is a unique Application code to set;
                * ``NAME`` (string) is the Application name to set;
                * ``DESTINATION`` (string) is the Application destination directory
                  (relative to the project) to set;
                * ``TEMPLATEDIR`` (string) is the Application template directory to
                  set;
                * ``MODELS``is either a dictionnary of model declarations to use for
                  the application or a filepath (as a string) to a JSON model
                  declarations to load in place;
                * ``APPSTACK`` is either a dictionnary of appstack configuration
                  or a filepath (as a string) to a JSON appstack configuration to
                  load in place;

                Obviously the list from ``apps`` can contains one or many application
                definitions.

        Returns:
            object: The given payload possibly altered with some special paths resolved
                as include content.
        """
        cwd = Path.cwd()

        if isinstance(payload, Path):
            if not payload.exists():
                msg = (
                    "Unable to find given project configuration file path: {}"
                )
                raise ProjectValidationError(msg.format(payload.resolve()))
            payload = json.loads(payload.read_text())

        if not isinstance(payload, dict):
            msg = (
                "Project configuration must be a dictionnary."
            )
            raise ProjectValidationError(msg)

        if not payload.get("apps", {}):
            msg = (
                "Project configuration requires at least a non empty dict in 'apps' "
                "item."
            )
            raise ProjectValidationError(msg)

        # Resolve apps values
        for appcode, appdata in payload["apps"].items():
            missing = [
                k
                for k in self._APP_CONF_REQUIRED_ITEMS
                if k not in appdata.keys()
            ]
            if missing:
                msg = (
                    "Application item '{}' is missing one or more required items: {}."
                )
                raise ProjectValidationError(msg.format(
                    appcode,
                    ", ".join(missing)
                ))

            # TODO: A string may be accepted also and turned to a Path (because JSON
            # does not allow for Path type)
            if isinstance(appdata["declarations"], str):
                appdata["declarations"] = Path(appdata["declarations"])

            if isinstance(appdata["declarations"], Path):
                if not appdata["declarations"].exists():
                    msg = (
                        "Unable to find given declarations file path: {}"
                    )
                    raise ProjectValidationError(msg.format(
                        appdata["declarations"].resolve()
                    ))

                appdata["declarations"] = json.loads(
                    appdata["declarations"].read_text()
                )

            if isinstance(appdata["appstack"], str):
                appdata["appstack"] = Path(appdata["appstack"])

            if isinstance(appdata["appstack"], Path):
                if not appdata["appstack"].exists():
                    msg = (
                        "Unable to find given appstack file path: {}"
                    )
                    raise ProjectValidationError(msg.format(
                        appdata["appstack"].resolve()
                    ))

                appdata["appstack"] = json.loads(
                    appdata["appstack"].read_text()
                )

            self.add_application(
                appdata["appstack"],
                appdata["template_dir"],
                name=appdata["name"],
                code=appcode,
                destination=appdata["destination"]
            )
            self.add_app_models(appcode, appdata["declarations"])

        #print(json.dumps(payload, indent=4))

        return payload
