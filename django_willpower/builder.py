"""
DEPRECATED: in favor of core.builder
"""
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape
from jinja2.exceptions import TemplateSyntaxError, UndefinedError, TemplateNotFound

import django_willpower
from .exceptions import ProjectBuildError
from .datamodels import Field, DataModel
from .available_components import DEFAULTS as DEFAULT_COMPONENTS


class AppBuilder:
    """
    DEPRECATED

    Build everything for the application.

    Principle is to build model modules for each component of an application.

    * Only a single application can be managed;
    * An application have many components (model, form, view, etc..);
    * An application have many models;
    * A model have many fields;
    * Each component have a module for each application model;
    * A field describes model field and form field but may also defines what to
        test on model from a component, what to display in template, etc..

    Structure ::

        - Application
        └── Component{1,n}
            └── Module{1,n}
                └── DataModel{1,n}
                    └── Field{1,n}

    """
    def __init__(self, logger, appmanifest, projectdir, declarations,
                 custom_template_dir=None, allowed_components=None):
        self.logger = logger
        self.appmanifest = appmanifest
        self.appname = self.appmanifest["app_name"]
        self.projectdir = projectdir
        self.appdir = self.projectdir / self.appname
        self.declarations = declarations
        self.custom_template_dir = custom_template_dir
        self.willpower_basepath = Path(django_willpower.__file__).parent
        self.base_templates = self.willpower_basepath / "app_templates"

        # Careful because this is mutable objects
        self.allowed_components = allowed_components or DEFAULT_COMPONENTS

        self.jinja_env = self.get_jinja_environment()

    def get_templates_directories(self, custom_templates=None):
        """
        Return the available templates directories
        """
        template_dir = [self.base_templates]

        if self.custom_template_dir:
            template_dir.append(self.custom_template_dir)

        return template_dir

    def get_jinja_environment(self):
        """
        Initialize Jinja environment with the right template directory.
        """
        env = Environment(
            loader=FileSystemLoader(
                self.get_templates_directories(
                    custom_templates=self.custom_template_dir
                )
            ),
        )

        # Ensure expected templates from enabled modules exist from available templates
        # directories
        missing_templates = []
        for component in self.allowed_components:
            for mod in component.modules:
                try:
                    env.get_template(mod.template)
                except TemplateNotFound:
                    missing_templates.append(mod.template)

        if missing_templates:
            msg = "- Template is missing: {}"
            for item in missing_templates:
                self.logger.critical(msg.format(item))

            raise ProjectBuildError("Unable to continue")

        return env

    def bind_datamodels(self):
        """
        Get all model inventory for declarations

        .. TODO::
            Model inventorying should be done in its own class because it would allow
            better JSON structure validation and could be executed upstream and passed
            to builder and cookiecutter also.

        .. TODO::
            * Field should know about its Model
            * Module should know about its Component
            * There may be a App datamodel, if so the Component should know about it

        Returns:
            list: A list of ``DataModel`` object for defined model declarations.
        """
        datamodels = []

        for modelname, modelopts in self.declarations.items():
            model = DataModel(
                app=self.appname,
                name=modelname,
                verbose_single=modelopts.get("label", modelname),
                modelfields=[
                    Field(name=fieldname, **fieldopts)
                    for fieldname, fieldopts in modelopts["fields"].items()
                ],
                # All other model payload items are passed as keyword arguments however
                # they must be defined as datamodel attribute before.
                **{
                    k: v
                    for k, v in modelopts.items()
                    if k != "fields"
                }
            )
            datamodels.append(model)

        return datamodels

    def safe_path_write(self, path, content):
        """
        Safely write content to path even if path parents does not exists yet (they will
        be created on need).
        """
        # Ensure path is always inside the application
        assert path.parent.relative_to(self.appdir) is not None

        # Create path parents if needed
        if not path.parent.exists():
            msg = "          └── Created path parents: {}".format(path.parent)
            self.logger.debug(msg)
            path.parent.mkdir(mode=0o755, parents=True)

        msg = "              Written to: {}".format(path)
        self.logger.debug(msg)
        path.write_text(content)

        return path

    def build_module(self, component, module, inventories):
        """
        Build component module for a model declaration.
        """
        module_pattern = (
            self.appdir / Path(component.directory) / module.destination_pattern
        )
        self.logger.debug("      └── Module pattern : {}".format(module_pattern))

        self.logger.debug("      └── Module template : {}".format(module.template))

        if module.once:
            # It would be built once with the full inventories in context
            module_destination = Path(
                str(module_pattern).format(appname=self.appname)
            )
            msg = "          └── For all models: {}".format(module.template)
            self.logger.debug(msg)

            # Render module template with context and write it to the FS
            template = self.jinja_env.get_template(module.template)
            rendered = template.render(
                app=self.appname,
                component=component,
                module=module,
                inventories=inventories,
            )
            self.safe_path_write(module_destination, rendered)
        else:
            self.logger.debug("      └── For models:")
            for inventory in inventories:
                module_destination = Path(
                    str(module_pattern).format(
                        appname=self.appname,
                        modelname=inventory.module_filename
                    )
                )
                msg = "          └── {}: {}".format(inventory.name, module_destination)
                self.logger.debug(msg)

                # Render module template with context and write it to the FS
                template = self.jinja_env.get_template(module.template)
                rendered = template.render(
                    app=self.appname,
                    component=component,
                    module=module,
                    model_inventory=inventory,
                )
                self.safe_path_write(module_destination, rendered)

        return

    def create_component(self, component, inventories):
        """
        Create a component.
        """
        self.logger.debug("  └── Components:".format(component.name))
        component_path = self.appdir / component.directory

        if not component_path.exists():
            msg = "Creating missing directory: {}".format(component_path)
            self.logger.warning("      └── {}".format(msg))
            component_path.mkdir(mode=0o755, parents=True)

        for module in component.modules:
            self.build_module(component, module, inventories)

        return

    def process(self):
        """
        Create all application components with their modules.

        A model declaration item: ::

            "Blog": {
                "fields": {
                    "title": {
                        "kind": "charfield",
                        "display_in_admin_list": true,
                        "required": true,
                        [...]
                    },
                }
            }

        Arguments:
            path (string): A path to a declaration file.

        Returns:
            something: something
        """
        self.logger.debug("Processing")

        self.logger.debug("- Model inventories")
        inventories = self.bind_datamodels()
        # print(json.dumps([asdict(v) for v in inventories], indent=4))

        # Build components modules
        self.logger.debug("- Components")
        for component in self.allowed_components:
            self.create_component(component, inventories)
