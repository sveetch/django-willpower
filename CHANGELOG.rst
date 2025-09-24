
=========
Changelog
=========

Development
***********

Todo.


Version 0.2.1 - 2025/09/23
**************************

Implemented many features, introduced "Willpower object" syntax and fix many issues.

* Introduced basic search with django-haystack and whoosh;
* Added new attribute ``related_model`` to ``DataModel`` to enable listing of relation
  in detail view, currently it is limited to the application models only;
* Added new macro to render detail value instead of using a rendered include using a
  rendered template so the detail directly include the value code;
* Implemented definition of ``limit_choices_to`` for a ForeignKey field;
* Improved the way to define the model object title to display;
* Changed Index view to order queryset on field from
  ``model_inventory.string_representation``;
* Added template tag to correctly use the elided pagination and update base template
  for more flexible blocks;
* Fixed all field template to correctly apply ``blank`` value;
* Leveled up pagination settings to 75 entries;
* Fixed admin module template;
* Fixed macro ``attribute_value_coerced_string`` for correct None value usage;
* Added new extension to implement ``str.format()``, added missing basic modules and
  added some minor tests;
* Enabled additional filters into Jinja environment from builder and update some field
  templates to use them;
* Added a Jinja filter ``wobject_render`` to render a ``WillpowerObjectString``;
* Implemented "Willpower object" in field attributes ``default`` and ``target``. It
  stills  have to be fully supported in templates (string cast and imports);


Version 0.2.0 - 2025/08/22
**************************

This is a large refactoring to improve internal code.

* Dataclasses are now connected each others (From Application to Module, from DataModel
  to Field and a link between Application and DataModel) so it is easier to introspect
  from templates;
* Project builder has evolved and a project registry class has been added;
* Command line has evolved to be allow for multiple commands instead of an unique one;
* Command ``create`` does not involve Cookiecutter anymore for now (it may comes again
  in an additional command ``bake``);
* Command ``create`` has dropped many deprecated options and just expect a destination
  directory and a JSON file for the full project configuration;
* A new command ``version`` has been added to print out programm version;
* Test coverage has been started;
* Added some new components, modules and Model field templates;


Version 0.1.0 - Unreleased
**************************

First commit with basic requirements, templates and some starting code done as a
Proof of concept.
