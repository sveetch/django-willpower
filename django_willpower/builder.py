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
        sys.exit usage should be replaced with internal exception.
    """
    def __init__(self, logger, appmanifest, basedir, declarations,
                 custom_template_dir=None):
        self.logger = logger
        self.appmanifest = appmanifest
        self.appname = self.appmanifest["app_name"]
        self.appdir = basedir / self.appname
        self.basedir = basedir
        self.declarations = declarations
        self.custom_template_dir = custom_template_dir
        self.willpower_basepath = Path(django_willpower.__file__).parent
        self.base_templates = self.willpower_basepath / "app_templates"

        self.allowed_components = [
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

    def build_component(self, name, inventories):
        self.logger.debug("  └── Components:", name)
        component_path = self.appdir / name

        if not component_path.exists():
            msg = "Component directory does not exist: {}".format(component_path)
            self.logger.warning("      └── {}".format(msg))
            return

        init_module = component_path / "__init__.py"
        self.logger.debug("      └── init_module: {}".format(init_module))

        component_template = "{}/module.py".format(name)
        self.logger.debug("      └── component_template : {}".format(component_template))

        for model_inventory in inventories:
            model_module_path = component_path / model_inventory.module_filename
            self.logger.debug("      └── {}: {}".format(model_inventory.name, model_module_path))
            template = self.jinja_env.get_template(component_template)
            rendered = template.render(
                component=name,
                model_inventory=model_inventory,
            )
            print("<start>")
            print(rendered)
            print("<end>")



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

        appmanifest = self.basedir / "cookiebacked.json"

        self.logger.debug("- Model inventories")
        inventories = self.get_model_inventories()
        # print(json.dumps([asdict(v) for v in inventories], indent=4))

        # Discover structure
        self.logger.debug("- Components")
        for name in self.allowed_components:
            self.build_component(name, inventories)
