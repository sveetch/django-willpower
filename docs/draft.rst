=======================
Development draft notes
=======================

Concept draft
*************

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

.. NOTE::

    * We use a cookiecutter replay to not have to fill any prompt question;
    * To quickly start we will ignore API, CMS plugin and all extras;

Experimentation
***************

Jinja has proven to be painful for building Python code at a certain point of details
because it does not allow to easily manage whitespace, indentation and linebreak
characters. You can certainly manage them but it result to templates very difficult to
maintain for all possible options.

We experimentated building code with builtin Python module 'ast' that is promising in a
certain way because it allow to code programatically without to concern about
whitespace, indentation and linebreak characters.

'ast' module take care itself of all these characters which you don't have to bother
(well it may not fully pass a Flake8 check but this can be fixed easily).

However the problem is that with 'ast' you need to be very declarative to define code
and it leads to a lot of work for complex modules, the maintenance should be better
that with Jinja, but evolution may be less easy.

We need to continue experimentation a little bit on a single component module to dig
on this problem but for now we are thinking about an hybrid solution with Jinja filters
that may build some module parts with ast. Jinja will still be used to templatize the
module structure and use 'ast' to build the complex part that would involve many
conditions and Python syntax structure blocks.

Actually there is a sample in progress of the 'ast' experimentation in the script
``model_prototyper.py`` at the root of this repository. It is not involved in Willpower
code in any ways.

Todo
****

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

- [~] Base component building:

  - [x] Models;
  - [~] Admins;
  - [ ] URLs;
  - [ ] Views;
  - [ ] Templates;
  - [ ] Forms;
  - [ ] Settings;
  - [ ] Extra components:

    - [ ] Haystack index;
    - [ ] DRF serializer;
    - [ ] DRF viewset;
    - [ ] CMS plugin;
    - [ ] django-configuration helper;

- [ ] We seriously start lacking of test coverage, especially about components modules
  render;
- [~] Look to build Python modules with 'ast' instead of Jinja templates because it is
  more efficient for code quality (indentation, space and condition is painful to
  manage well with Jinja, this could lead to problems to maintain or evolve templates);

  - [x] Check 'ast' is usable to build code;
  - [x] Start code prototyping with models;
  - [~] Finish the Model prototyping;
  - [ ] Continue with other models;
  - [ ] Alternatively we could use ast prototyping only for some parts like model
    fields and keep using Jinja as the base. The ast prototyping would be specialized
    to some specific part and have a Jinja filter for it (like a
    ``build_model_fields``) but the filter would still need an argument to manage
    indentation from the built code;

    - [ ] Dataclasses may include method to prototype some parts ?

  - [ ] We could also change the build to be hybrid, each module could be built either
    from a Jinja template or an ast prototyper;

- [ ] Rename 'django-willpower' to just 'willpower';
- [ ] We probably should use Pydantic to validate model dataclasses;
- [ ] Flake can be helpful to quickly see failures in generated modules from templates;
- [ ] Optional pluralize option in model declaration would be nice;
- [ ] Command is missing option '--version';
- [ ] Command option validation is currently very basic, in beta stage it would need to
  validate the structure of JSON payloads for required items;
- [ ] YAML for declaration could be nice ?
- [ ] We will have to introspect declarations to check for some things, actually nothing
  is checked and it will probably lead to some invalid code when user makes a mistakes;
