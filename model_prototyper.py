"""
Proof of concept to programmatically build a Python module using "ast" module.

The concept is that we would have to define specialized class for each of module to
build (model module, model "__init__" ? view, url, test (sic) etc..). This is a
workaround using Jinja to write code that demonstrated some limit (with the spaces and
indentations is a huge pain).

Actually this is laboratory stuff to see if a basic module with imports, class, method
can be easily script. If it works, we will need to have a base abstract class to help
building all the module prototypes.

At the end, all the written code should be passed to linter alike that rewrite it to
pass Flake and other conventions like tools like Blake, autopep8/yapf and isort.
"""
import ast

from pathlib import Path


class ImportCrafterAbstract:
    TOPLEVEL_IMPORTS = []

    def craft_alias(self, payload):
        """
        Generic way to create an alias instruction for an import.

        Expected payload structure is either a string for a simple name or a tuple
        ``NAME, ALIAS`` for a name with an alias.
        """
        if isinstance(payload, str):
            keywords = {"name": payload}
        elif isinstance(payload, list) or  isinstance(payload, tuple):
            keywords = {"name": payload[0], "asname": payload[1]}
        else:
            raise NotImplementedError("Alias data must be a string, a list or a tuple")

        return ast.alias(**keywords)

    def craft_import(self, payload):
        """
        Generic way to create an import instruction.

        Expected payload structure: ::

            {
                "level": 1,
                "module": "machin",
                # Required
                "names": [
                    "NAME",
                    ("NAME", "ALIAS"),
                ]
            }

        """

        if payload.get("module", None):
            return ast.ImportFrom(
                module=payload["module"],
                names=[self.craft_alias(item) for item in payload["names"]],
                level=payload.get("level", 0),
            )
        else:
            return ast.Import(
                names=[self.craft_alias(item) for item in payload["names"]],
                level=payload.get("level", 0),
            )

    def create_imports(self, items):
        """
        Generic way to create a list of import instructions
        """
        return [self.craft_import(item) for item in items]

    def get_toplevel_imports(self, descriptor):
        """
        Get list of top level import definitions commonly defined class attribute
        ``TOPLEVEL_IMPORTS``.
        """
        return self.TOPLEVEL_IMPORTS

    def create_toplevel_imports(self, descriptor):
        """
        Create all import instructions to append at the top level space of module.
        """
        return self.create_imports(self.get_toplevel_imports(descriptor))


class ModelClassCrafterAbstract:
    def create_docstring(self, content):
        """
        Create the model class

        Arguments:
            content (list): List of sentence string that will be joined with a line
                break character. Indentation will need to be included into each line
                that need it.

        Returns:
            ast.Expr: Expression object.

        .. Todo::
            This should be shared for every crafter because docstring is common to
            many other objects.
        """
        return ast.Expr(value=ast.Constant(value="\n".join(content)))

    def create_main_class(self, descriptor):
        """
        Create the model class
        """
        main_class = ast.ClassDef(
            name="Comment",
            bases=[
                ast.Attribute(
                    value=ast.Name(id="models", ctx=ast.Load()),
                    attr="Model",
                    ctx=ast.Load()
                )
            ],
            keywords=[],
            body=[
                self.create_docstring([
                    "",
                    "    Comment model.",
                    "",
                    "    Attributes:",
                    "        title (CharField):",
                    "        created (DateTimeField):",
                    ""
                ])
            ],
            decorator_list=[],
        )

        return [main_class]

    def create_toplevel_objects(self, descriptor):
        return [self.create_main_class(descriptor)]


class ModulePrototyperMixin(ImportCrafterAbstract, ModelClassCrafterAbstract):
    """
    The base mixin class to inherit for a Django model prototyper.
    """
    def build_tree(self, descriptor):
        """
        Build tree from given module descriptor
        """
        return ast.Module(
            body=(
                self.create_toplevel_imports(descriptor)
                + self.create_toplevel_objects(descriptor)
            ),
            type_ignores=[],
        )

    def build(self, descriptor, destination=None):
        """
        Output module code from built tree, either as a print out or a file.
        """
        tree = self.build_tree(descriptor)

        # Convert tree to Python code
        return ast.unparse(tree)


class ModelPrototyper(ModulePrototyperMixin):
    """
    Concrete model prototyper
    """
    TOPLEVEL_IMPORTS = [
        {
            "module": "django.db",
            "names": ["models"]
        },
        {
            "module": "django.utils.translation",
            "names": [("gettext_lazy", "_")]
        },
        {
            "module": "django.urls",
            "names": ["reverse"]
        },
        # This one should be conditionned to existence of a datetime field using
        # the timezone as a default value
        {
            "module": "django.utils",
            "names": ["timezone"]
        },
        # Dummy tests below
        {
            "names": ["foobar"]
        },
        {
            "level": 1,
            "module": "machin",
            "names": ["bidule"]
        },
    ]


if __name__ == "__main__":
    prototyper = ModelPrototyper()
    code = prototyper.build({})
    print(code)
