from .datamodels import Component, Module


DEFAULTS = [
    Component(
        name="R&D",
        code="willpower_dev",
        directory="willpowerdev",
        modules=[
            Module(
                name="Jinja whitespace control sample",
                code="jinja_whitespace",
                template="jinja_whitespace.html",
                destination_pattern="jinja_whitespace.html",
                once=True,
            ),
        ]
    ),
    Component(
        name="Application model",
        code="appmodel",
        directory="models",
        modules=[
            Module(
                name="Model module",
                code="module",
                template="models/module.py",
                destination_pattern="{modelname}.py",
            ),
            Module(
                name="Model init",
                code="init",
                template="models/__init__.py",
                destination_pattern="__init__.py",
                once=True,
            ),
        ]
    ),
    Component(
        name="Application admins",
        code="appadmins",
        directory="admin",
        modules=[
            Module(
                name="Admin module",
                code="module",
                template="admin/module.py",
                destination_pattern="{modelname}.py",
            ),
            Module(
                name="Admin init",
                code="init",
                template="admin/__init__.py",
                destination_pattern="__init__.py",
                once=True,
            ),
        ]
    ),
    # Component(name="Application views", code="appviews", directory="views", modules=[]),
    # Component(name="Application urls", code="appurls", directory="", modules=[]),
    # Component(name="Application forms", code="appforms", directory="forms", modules=[]),
]


EXTRA_SEARCH = [
    # Component(name="Application search indexes", code="appsearch", directory="", modules=[]),
]
