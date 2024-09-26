.. _quickstart:

Quickstart
==========

Installation
------------

* Install django-superform4::

    pip install django-superform4

* Add ``'django_superform'`` to your ``INSTALLED_APPS`` settings::

    INSTALLED_APPS = [
        # other apps
        "django_superform",
    ]

* Use like you would any other Form or Field. Subclass ``SuperModelForm`` to make ModelForms that can have InlineFormSetFields as fields
