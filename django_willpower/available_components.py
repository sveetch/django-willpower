from .models import Component, Module


DEFAULTS = [
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
    # Component(name="Application forms", code="appforms", directory="forms", modules=[]),
    # Component(name="Application views", code="appviews", directory="views", modules=[]),
    # Component(name="Application urls", code="appurls", directory="", modules=[]),
    # Component(name="Application search indexes", code="appsearch", directory="", modules=[]),
]