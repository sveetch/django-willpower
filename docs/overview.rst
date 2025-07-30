.. _overview_intro:

========
Overview
========

.. Note::
    This document is currently a draft until Willpower makes it to a stable version.


Concept
*******

The concept of Willpower is that we often restart the same kind of module, classes,
functions, etc.. Sure we evolve, we progress but at some point of experiences there are
many patterns that does not change much and if you are starting an application every
month there are many chances that you will use again previous similar code.

So we have something almost standardized that could be used as templates alike to build
another applications.

Willpower won't never be able to produce a final stage application because there are
too many feature, cases and options to gather to produce a such thing. However there
is a large area of things that won't change much in a short to middle time, this is
what Willpower try to gather and use to produce an application.

Finally Willpower is to be considered as a builder of a working prototype application
with many basic features.


Technically
***********

Project builder like (Paster, Cookiecutter, etc..) are limited to the fact that
components modules must exists in the project template structure before to use it. A
developer must include some kind of a basic application, like a blog, and then create
its components for data models, views, tests, etc..

But if you are planning to build a Product catalog application you may use this project
template structure but you will have to adapt many things at least to get a working
prototype.

Willpower still use Cookiecutter as a base to generate an empty structure, since it
eases structure management and evolution. However Willpower also have a builder that is
able to build components modules from a description of data models. So instead of always
creating a basic Blog application, you will create an application specifically to
the data models you defined.

This so you will be able to create a Blog, a Product catalog or whatever else but only
in a prototype stage.

Internally Willpower will compile informations from your data models definitions and
distribute them to components that will use informations to know what to define in
module for each data model.


What you could expect
*********************

Actually Willpower is focused on creation of a Django application and you could expect
to creation an application with the following components:

* Data models that define their fields with the proper Model field options;
* An admin class for each data model with some possible options;
* An index list view and a detail view for each data model;
* All URLs for created views;
* A form for each model admin and a frontend form for each model. The latter one is not
  used yet in views because you may not want to expose them, this is at your
  responsability;

Many component options would be available to define or not for each model and we plan
to allow for other extra components like default settings, factories, tests, search
indexes, etc..

The application will be well structured with a component module for each model.
