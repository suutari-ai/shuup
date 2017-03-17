from __future__ import unicode_literals

import inspect

from django.apps import apps
from django.db import models
from django.utils.html import strip_tags
from django.utils.encoding import force_text


def setup(app):
    # Make sure we have loaded models, otherwise related fields may end up
    # as strings
    models.get_models()

    app.connect('autodoc-process-docstring', process_docstring)


def process_docstring(app, what, name, obj, options, lines):
    # Only look at objects that inherit from Django's base model class
    if inspect.isclass(obj) and issubclass(obj, models.Model):
        latelines = ['']
        _process_model(obj, lines, latelines)
        lines.extend(latelines)

    # Return the extended docstring
    return lines


def _process_model(model, lines, latelines):
    # Grab the field list from the meta class
    fields = model._meta.get_fields()
    for field in fields:
        _process_model_field(field, lines, latelines)


def _process_model_field(field, lines, latelines):
    if not hasattr(field, 'attname') or isinstance(field, models.ForeignKey):
        field.attname = field.name

    _process_field_help_text_and_verbose_name(field, lines)
    _process_field_type(field, lines, latelines)


def _process_field_help_text_and_verbose_name(field, lines):
    # Decode and strip any html out of the field's help text
    try:
        help_text = strip_tags(force_text(field.help_text))
    except:
        help_text = ''

    # Decode and capitalize the verbose name, for use if there isn't
    # any help text
    try:
        verbose_name = force_text(field.verbose_name).capitalize()
    except:
        verbose_name = ''

    if help_text:
        # Add the model field to the end of the docstring as a param
        # using the help text as the description
        lines.append(':param %s: %s' % (field.attname, help_text))
    elif verbose_name:
        # Add the model field to the end of the docstring as a param
        # using the verbose name as the description
        lines.append(':param %s: %s' % (field.attname, verbose_name))


def _process_field_type(field, lines, latelines):
    # Add the field's type to the docstring
    if isinstance(field, models.ForeignKey):
        to = _resolve_field_destination(field, field.rel.to)
        lines.append(':type %s: %s to :class:`%s.%s`' % (
            field.attname,
            type(field).__name__, to.__module__, to.__name__))
    elif isinstance(field, models.ManyToManyField):
        to = _resolve_field_destination(field, field.rel.to)
        lines.append(':type %s: %s to :class:`%s.%s`' % (
            field.attname,
            type(field).__name__, to.__module__, to.__name__))
    elif isinstance(field, models.ManyToOneRel):
        to = _resolve_field_destination(field, field.related_model)
        latelines.append('.. attribute:: %s' % (
            field.related_name or field.name + '_set'))
        latelines.append('')
        latelines.append('   %s to :class:`%s.%s`' % (
            type(field).__name__, to.__module__, to.__name__))
        latelines.append('')
    else:
        lines.append(':type %s: %s' % (
            field.attname, type(field).__name__))


def _resolve_field_destination(field, to):
    if isinstance(to, type):  # Already a model class
        return to
    if to == 'self':
        return field.model
    elif '.' in to:
        return apps.get_model(to)
    return apps.get_model(field.model._meta.app_label, to)
