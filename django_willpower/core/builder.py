import logging

from jinja2 import Environment, FileSystemLoader

from ..exceptions import ProjectBuildError
from ..utils.jinja import wobject_render, str_format
from .. import __pkgname__


class ProjectBuilder:
    """
    Project builder.

    This will build all components modules of each project application.

    * An application have many components (model, form, view, etc..);
    * An application have many models;
    * A model have many fields;
    * Each component have a module for each application model;
    * A field describes model field and form field but may also defines what to
        test on model from a component, what to display in template, etc..

    Structure of a project dataclasses ::

        - Application
        ├── Component{1,n}
        │   └── Module{1,n}
        └── DataModel{1,n}
            └── Field{1,n}

    Arguments:
        registry (ProjectRegistry):
        projectdir (Path):

    """
    def __init__(self, registry, projectdir):
        self.logger = logging.getLogger(__pkgname__)

        self.registry = registry
        self.projectdir = projectdir.resolve()

    def get_jinja_environment(self, template_dir):
        """
        Initialize Jinja environment with the right template directory.
        """
        env = Environment(loader=FileSystemLoader(template_dir))
        env.filters["str_format"] = str_format
        env.filters["wobject_render"] = wobject_render

        return env

    def safe_module_write(self, path, content):
        """
        Safely write content to path even if path parents does not exists yet (they will
        be created on need).
        """
        # Ensure path is always inside the project
        if not path.is_relative_to(self.projectdir):
            msg = "Resolved module path is not a child of the project directory: {}"
            raise ProjectBuildError(msg.format(path))

        # Create path parents if needed
        if not path.parent.exists():
            msg = "          └── Created path parents: {}".format(path.parent)
            self.logger.debug(msg)
            path.parent.mkdir(mode=0o755, parents=True)

        msg = "              Written to: {}".format(path)
        self.logger.debug(msg)
        path.write_text(content)

        return path

    def get_module_path_context(self, module, modelname=None):
        context = {
            "app": module.component.app.code,
            "component": module.component.code,
            "module": module.code,
        }

        if modelname:
            context["model"] = modelname

        return context

    def build_module(self, jinja_env, module, inventories):
        """
        Build component module for a model declaration.
        """
        self.logger.debug("      └── Module pattern : {}".format(
            module.get_destination()
        ))

        self.logger.debug("      └── Module template : {}".format(module.template))

        if module.once:
            # Will be built once with the full inventories in context
            module_destination = (self.projectdir / module.get_destination(
                self.get_module_path_context(module)
            )).resolve()
            msg = "          └── For all models: {}".format(module.template)
            self.logger.debug(msg)

            # Render module template with context and write it to the FS
            template = jinja_env.get_template(module.template)
            rendered = template.render(
                app=module.component.app,
                component=module.component,
                module=module,
                inventories=inventories,
            )
            self.safe_module_write(module_destination, rendered)
        else:
            self.logger.debug("      └── For models:")
            for model in inventories:
                module_destination = (self.projectdir / module.get_destination(
                    self.get_module_path_context(
                        module,
                        modelname=model.module_filename
                    )
                )).resolve()
                msg = "          └── {}: {}".format(model.name, module_destination)
                self.logger.debug(msg)

                # Render module template with context and write it to the FS
                template = jinja_env.get_template(module.template)
                rendered = template.render(
                    app=module.component.app,
                    component=module.component,
                    module=module,
                    model_inventory=model,
                )
                self.safe_module_write(module_destination, rendered)

        return

    def create_component(self, jinja_env, component):
        """
        Create a component.
        """
        self.logger.debug("  └── Component: {}".format(component.name))

        for module in component.modules:
            self.build_module(jinja_env, module, component.app.models)

        return

    def process(self, names=None):
        """
        Create all application components with their modules.

        Arguments:
            path (string): A path to a declaration file.

        Returns:
            something: something
        """
        names = names or self.registry.apps.keys()
        self.logger.debug("Processing into: {}".format(self.projectdir))

        for appname in names:
            app = self.registry.apps[appname]
            self.logger.debug("- Application: {}".format(app.name))

            # Load a new jinja env for each application since each one has its
            # own template dir
            jinja_env = self.get_jinja_environment(app.template_dir)

            for component in app.components:
                self.create_component(jinja_env, component)
