# -*- coding: utf-8 -*-
"""
     ____   _                 _____                 _____
    |    \ |_|___ ___ ___ ___|   __|_ _ ___ ___ ___|   __|___ ___ _____
    |  |  || | .'|   | . | . |__   | | | . | -_|  _|   __| . |  _|     |
    |____/_| |__,|_|_|_  |___|_____|___|  _|___|_| |__|  |___|_| |_|_|_|
         |___|       |___|             |_|


Author: Gregor Müllegger <gregor@muellegger.de>
Project home: https://github.com/gregmuellegger/django-superform
See http://django-superform.readthedocs.org/en/latest/ for complete docs.
"""
from .fields import (
    FormField, ModelFormField, ForeignKeyFormField, FormSetField,
    ModelFormSetField, InlineFormSetField)
from .forms import SuperForm, SuperModelForm
from .widgets import FormWidget, FormSetWidget


__version__ = '0.2.0'


__all__ = (
    'FormField', 'ModelFormField', 'ForeignKeyFormField', 'FormSetField',
    'ModelFormSetField', 'InlineFormSetField', 'SuperForm', 'SuperModelForm',
    'FormWidget', 'FormSetWidget')
