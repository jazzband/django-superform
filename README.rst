django-superform
================

**Less sucking formsets.**

|build| |docs| |package| |gitter|

A ``SuperForm`` is absolutely super if you want to nest a lot of forms in each
other. Use formsets and nested forms inside the ``SuperForm``. The
``SuperForm`` will take care of its children!

.. note::
    This package is still in rapid development. Some APIs might change in the
    future and it's not yet feature complete. The documentation is not yet
    complete either, but everything that is documented, is up to date and
    should work as stated. If not, then please file a bug.
    Every non-backwards compatible change and new features will be documented
    in the changelog_.

.. _changelog: https://github.com/gregmuellegger/django-superform/tree/master/CHANGES.rst

Imagine you want to have a view that shows and validates a form and a formset.
Let's say you have a signup form where users can enter multiple email
addresses. Django provides formsets_ for this usecase, but handling those in a
view is usually quite troublesome. You need to validate both the form and the
formset manually and you cannot use django's generic FormView_. So here comes
**django-superform** into play.

.. _formsets: https://docs.djangoproject.com/en/1.6/topics/forms/formsets/
.. _FormView: https://docs.djangoproject.com/en/1.6/ref/class-based-views/generic-editing/#formview

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

Documentation
-------------

Full documentation is available on Read The Docs: https://django-superform.readthedocs.org/

----

Developed by Gregor Müllegger in cooperation with Team23_.

.. _Team23: http://www.team23.de/

.. |build| image:: https://travis-ci.org/gregmuellegger/django-superform.svg?branch=master
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/gregmuellegger/django-superform
.. |docs| image:: https://readthedocs.org/projects/django-superform/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://django-superform.readthedocs.org/
.. |package| image:: https://badge.fury.io/py/django-superform.svg
    :alt: Package Version
    :scale: 100%
    :target: http://badge.fury.io/py/django-superform
.. |gitter| image:: https://badges.gitter.im/JoinChat.svg
    :alt: Gitter Chat, discuss django-superform with others
    :scale: 100%
    :target: https://gitter.im/gregmuellegger/django-superform
