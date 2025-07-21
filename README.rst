.. _Python: https://www.python.org/
.. _Click: https://click.palletsprojects.com
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _sveetch-djangoapp-sample: https://github.com/sveetch/cookiecutter-sveetch-python

================
Django Willpower
================

Draft
*****

An attempt to reboot `sveetch-djangoapp-sample`_
to implement building of a detailled app where the multiple models and their fields can
be declared and **BAM** the magic makes a detailled app opposed to
`sveetch-djangoapp-sample`_ that always build the same dummy Blog app.

Cookiecutter is not able to produce a detailled structure, the module file needs to
exists in template so we could not declare models like Profile and Stats to create their
own modules, it will always be a Blog thing.

But Cookiecutter may still be used to scaffold the app structure but then an additional
tool will build model, forms, factories, DRF serializers, forms, admins, tests, etc.. in
detail from the declaration.

The built application will be mostly CRUD, basic and very standardized. It probably
won't never fit to all Django possibilities since this would need a better builder,
currently we use Jinja templates to avoid build Python code programatically.

.. WARNING::
    This is a proof of concept.

.. NOTE::

    * Currently we are working with ``make bar`` to start development;
    * We use a cookiecutter replay to not have to fill any prompt question;
    * To quickly start we will ignore API, CMS plugin and all extras;

- [x] Try to build model from declaration fields, for now we may start in the same
  unique module to quickly see how it would be feasible, we could also doing the same
  for views or forms;
- [x] Find how to create on the fly module for each model inside the generated app
  from cookiecutter;
- [x] Finally this will be a package on its own, not a simple cookiecutter template
  because builder needs more information and flexibility to create modules on the
  fly. Cookiecutter is still used to build the app structure and everything else. But
  we now need some tests to help growing and have a stable tool, and stop to have all
  the builder code in a single file (that is necessary for cookiecutter hooks);
- [x] A real process logs:

  - [x] Implement in commandline;
  - [x] Update builder code to use logs instead of print;

- [ ] Correctly manage model fields (actually they all rendered as dummy varchar);
- [ ] Base component building:

  - [x] Model;
  - [ ] Form;
  - [ ] Admin;
  - [ ] View;
  - [ ] URL;
  - [ ] Settings;
  - [ ] Model;

- [ ] Model fields (in their component specificities):
- [ ] Extra component building:

  - [ ] Haystack index;
  - [ ] DRF serializer;
  - [ ] DRF viewset;
  - [ ] CMS plugin;
  - [ ] django-configuration helper;

- [ ] We probably should use Pydantic to validate model dataclasses;
- [ ] Flake can be helpful to quickly see failures in generated modules from templates;
- [ ] Start test coverage to catch failures and improve development without to launch
  various commands each time;
- [ ] Optional pluralize option in model declaration would be nice;
- [ ] Command is missing option '--version';
- [ ] Command option validation is currently very basic, in beta stage it would need to
  validate the structure of JSON payloads for required items;
- [ ] YAML for declaration could be nice ?
- [ ] We will have to introspect declarations to check for some things, actually nothing
  is checked and it will probably lead to some invalid code when user makes a mistakes;

Dependencies
************

* `Cookiecutter`_>=2.4.0;
* `Python`_>=3.10;
* `Click`_>=8.0;

Links
*****

* Read the documentation on `Read the docs <https://django-willpower.readthedocs.io/>`_;
* Download its `PyPi package <https://pypi.python.org/pypi/django-willpower>`_;
* Clone it on its `Github repository <https://github.com/sveetch/django-willpower>`_;
