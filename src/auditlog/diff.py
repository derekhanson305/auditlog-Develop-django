from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.utils.encoding import smart_text


def model_instance_diff(old, new):
    """
    Calculates the differences between two model instances. One of the instances may be ``None`` (i.e., a newly
    created model or deleted model). This will cause all fields with a value to have changed (from ``None``).

    :param old: The old state of the model instance.
    :type old: Model
    :param new: The new state of the model instance.
    :type new: Model
    :return: A dictionary with the names of the changed fields as keys and a two tuple of the old and new field values
             as value.
    :rtype: dict
    """
    from auditlog.registry import auditlog

    if not(old is None or isinstance(old, Model)):
        raise TypeError("The supplied old instance is not a valid model instance.")
    if not(new is None or isinstance(new, Model)):
        raise TypeError("The supplied new instance is not a valid model instance.")

    diff = {}

    if old is not None and new is not None:
        fields = set(old._meta.fields + new._meta.fields)
        model_fields = auditlog.get_model_fields(new._meta.model)
    elif old is not None:
        fields = set(old._meta.fields)
        model_fields = auditlog.get_model_fields(old._meta.model)
    elif new is not None:
        fields = set(new._meta.fields)
        model_fields = auditlog.get_model_fields(new._meta.model)
    else:
        fields = set()
        model_fields = None

    # Check if fields must be filtered
    if model_fields and (model_fields['include_fields'] or model_fields['exclude_fields']) and fields:
        filtered_fields = []
        if model_fields['include_fields']:
            filtered_fields = [field for field in fields
                               if field.name in model_fields['include_fields']]
        else:
            filtered_fields = fields
        if model_fields['exclude_fields']:
            filtered_fields = [field for field in filtered_fields
                               if field.name not in model_fields['exclude_fields']]
        fields = filtered_fields

    for field in fields:
        try:
            old_value = smart_text(getattr(old, field.name, None))
        except ObjectDoesNotExist:
            old_value = None

        try:
            new_value = smart_text(getattr(new, field.name, None))
        except ObjectDoesNotExist:
            new_value = None

        if old_value != new_value:
            diff[field.name] = (old_value, new_value)

    if len(diff) == 0:
        diff = None

    return diff
