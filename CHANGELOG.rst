
=========
Changelog
=========

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
