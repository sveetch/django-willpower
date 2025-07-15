import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape
from jinja2.exceptions import TemplateSyntaxError, UndefinedError, TemplateNotFound

import django_willpower
from .exceptions import ModuleBuilderError
from .models import FieldModel, ModelInventory


class AppBuilder:
    """
    Build everything for the application.

    .. TODO::
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
              └── Component[*]
                  └── Model module[*]
                      └── Field[*]

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

        self.allowed_components = allowed_components or [
            "models",
            #"forms",
            #"views",
            # "indexes",
        ]

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
            autoescape=select_autoescape(),
        )

        # Ensure expected templates exists from available templates directories
        missing_templates = []

        for component in self.allowed_components:
            component_init = "{}/__init__.py".format(component)
            component_module = "{}/module.py".format(component)
            try:
                env.get_template(component_init)
            except TemplateNotFound:
                missing_templates.append(component_init)

            try:
                env.get_template(component_module)
            except TemplateNotFound:
                missing_templates.append(component_module)

        if missing_templates:
            msg = "- Template is missing: {}"
            for item in missing_templates:
                self.logger.critical(msg.format(item))

            raise ModuleBuilderError("Unable to continue")

        return env

    def get_model_inventories(self):
        """
        Get all model inventory for declarations

        .. Todo::
            Model inventorying should be done in its own class because it would allow
            better JSON structure validation and could be executed upstream and passed
            to builder and cookiecutter also.

        Returns:
            list: A list of ``ModelInventory`` object for defined model declarations.
        """
        return [
            ModelInventory(
                app=self.appname,
                name=modelname,
                modelfields=[
                    FieldModel(name=k, **v)
                    for k, v in modelopts["fields"].items()
                ]
            )
            for modelname, modelopts in self.declarations.items()
        ]

    def safe_path_write(self, path, content):
        """
        Safely write content to path even if path parents does not exists yet (they will
        be created on need).
        """
        # Ensure path is always inside the application
        assert path.parent.relative_to(self.appdir) is not None

        # Create path parents if needed
        if not path.parent.exists():
            msg = "          └── Create parents: {}".format(path.parent)
            self.logger.debug(msg)
            path.parent.mkdir(mode=0o755, parents=True)

        # TODO: commented until checked
        msg = "          └── Written to: {}".format(path)
        self.logger.debug(msg)
        path.write_text(content)

        return path

    def build_modules(self, component_name, component_path, inventories):
        """
        Build component modules.

        TODO: Iterate through defined component modules. Majority of components only
        have a single model module to create but some may have more.
        """

        for pattern in ["{}"]:
            module_pattern = component_path / pattern
            self.logger.debug("      └── Module pattern : {}".format(module_pattern))

            component_template = "{}/module.py".format(component_name)
            self.logger.debug("      └── Module template : {}".format(component_template))

            for model_inventory in inventories:
                module_destination = Path(
                    str(module_pattern).format(model_inventory.module_filename)
                )
                msg = "          └── {}: {}".format(model_inventory.name, module_destination)
                self.logger.debug(msg)

                template = self.jinja_env.get_template(component_template)

                rendered = template.render(
                    component=component_name,
                    model_inventory=model_inventory,
                )

                #print("<start>")
                #print(rendered)
                #print("<end>")
                self.safe_path_write(module_destination, rendered)

        # NOTE: This should be the final thing and built once
        global_init = "__init__.py"

        return

    def create_component(self, name, inventories):
        """
        Create a component.
        """
        self.logger.debug("  └── Components:".format(name))
        component_path = self.appdir / name

        if not component_path.exists():
            msg = "Component directory does not exist: {}".format(component_path)
            self.logger.warning("      └── {}".format(msg))
            return

        # TODO
        built = self.build_modules(name, component_path, inventories)

        #init_module = component_path / "__init__.py"
        #self.logger.debug("      └── init_module: {}".format(init_module))

        #component_template = "{}/module.py".format(name)
        #self.logger.debug("      └── component_template : {}".format(component_template))

        #for model_inventory in inventories:
            ## DEPRECATED
            #model_module_path = component_path / model_inventory.module_filename
            #msg = "      └── {}: {}".format(model_inventory.name, model_module_path)
            #self.logger.debug(msg)

            #template = self.jinja_env.get_template(component_template)

            #rendered = template.render(
                #component=name,
                #model_inventory=model_inventory,
            #)

            #print("<start>")
            #print(rendered)
            #print("<end>")

        return

    def process(self):
        """
        TODO

        A model declaration item: ::

            "Blog": {
                "fields": {
                    "title": {
                        "kind": "charfield",
                        "display_in_admin_list": true,
                        "required": true
                    },
                }
            }

        Arguments:
            path (string): A path to a declaration file.

        Returns:
            something: something
        """
        self.logger.debug("Processing")

        appmanifest = self.projectdir / "cookiebacked.json"

        self.logger.debug("- Model inventories")
        inventories = self.get_model_inventories()
        # print(json.dumps([asdict(v) for v in inventories], indent=4))

        # Build components modules
        self.logger.debug("- Components")
        for name in self.allowed_components:
            self.create_component(name, inventories)
