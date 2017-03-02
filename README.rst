django-superform
================

**Less sucking formsets.**

|build| |package| |gitter|

Documentation_ | Changelog_ | Requirements_ | Installation_

A ``SuperForm`` is absolutely super if you want to nest a lot of forms in each
other. Use formsets and nested forms inside the ``SuperForm``. The
``SuperForm`` will take care of its children!

Imagine you want to have a view that shows and validates a form and a formset.
Let's say you have a signup form where users can enter multiple email
addresses. Django provides formsets_ for this usecase, but handling those in a
view is usually quite troublesome. You need to validate both the form and the
formset manually and you cannot use django's generic FormView_. So here comes
**django-superform** into play.

.. _formsets: https://docs.djangoproject.com/en/1.10/topics/forms/formsets/
.. _FormView: https://docs.djangoproject.com/en/1.10/ref/class-based-views/generic-editing/#formview

Here we have an example for the usecase. Let's have a look at the
``forms.py``:

.. code-block:: python

    from django import forms
    from django_superform import SuperModelForm, InlineFormSetField
    from myapp.models import Account, Email


    class EmailForm(forms.ModelForm):
        class Meta:
            model = Email
            fields = ('account', 'email',)


    EmailFormSet = modelformset_factory(EmailForm)


    class SignupForm(SuperModelForm):
        username = forms.CharField()
        # The model `Email` has a ForeignKey called `user` to `Account`.
        emails = InlineFormSetField(formset_class=EmailFormSet)

        class Meta:
            model = Account
            fields = ('username',)


So we assign the ``EmailFormSet`` as a field directly to the ``SignupForm``.
That's where it belongs! Ok and how do I handle this composite form in the
view? Have a look:

.. code-block:: python

    def post_form(request):
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                account = form.save()
                return HttpResponseRedirect('/success/')
        else:
            form = PostForm()
        return render_to_response('post_form.html', {
            'form',
        }, context_instance=RequestContext(request))


No, we don't do anything different as we would do without having the
``FormSet`` on the ``SignupForm``. That way you are free to implement all the
logic in the form it self where it belongs and use generic views like
``CreateView`` you would use them with simple forms. Want an example for this?

.. code-block:: python

    from django.views.generic import CreateView
    from myapp.models import Account
    from myapp.forms import SignupForm


    class SignupView(CreateView):
        model = Account
        form_class = SignupForm


    urlpatterns = patterns('',
        url('^signup/$', SignupView.as_view()),
    )

And it just works.

.. _Requirements:

Requirements
------------

- Python 2.7 or Python 3.3+ or PyPy
- Django 1.4+

.. _Installation:

Installation
------------

Install the desired version with pip_::

    pip install django-superform

.. _pip: https://pip.pypa.io/en/stable/

Then add ``django-superform`` to ``INSTALLED_APPS`` in your settings file:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'django_superform',
        # ...
    )

Development
-----------

- Clone django-superform::

    git clone git@github.com:gregmuellegger/django-superform.git

- ``cd`` into the repository::

    cd django-superform

- Create a new virtualenv_.
- Install the project requirements::

    pip install -e .
    pip install -r requirements.txt

- Run the test suite::

    tox
    # Or if you want to iterate quickly and not test against all supported
    # Python and Django versions:
    py.test

.. _virtualenv: https://virtualenv.pypa.io/en/latest/

Documentation
-------------

Full documentation is available on Read the Docs: https://django-superform.readthedocs.org/

.. _Changelog: https://django-superform.readthedocs.org/en/latest/changelog.html
.. _Documentation: https://django-superform.readthedocs.org/

.. |build| image:: https://travis-ci.org/gregmuellegger/django-superform.svg?branch=master
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/gregmuellegger/django-superform
.. |package| image:: https://badge.fury.io/py/django-superform.svg
    :alt: Package Version
    :scale: 100%
    :target: http://badge.fury.io/py/django-superform
.. |gitter| image:: https://badges.gitter.im/JoinChat.svg
    :alt: Gitter Chat, discuss django-superform with others
    :scale: 100%
    :target: https://gitter.im/gregmuellegger/django-superform
