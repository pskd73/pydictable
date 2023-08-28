from typing import Type, Tuple, List

from pydictable import DictAble, Field, ListField, UnionField, DictField, ObjectField


def _update_spec(schema: Type[DictAble], spec: dict):
    if schema.__name__ in spec.get('$defs', {}):
        return

    spec['$defs'][schema.__name__] = {}
    _spec = spec['$defs'][schema.__name__]
    for attr, field in schema.get_fields().items():
        field_key = schema.get_field_key(attr)
        field_schema, refs = get_field_schema(field)
        _spec[field_key] = field_schema
        for ref in refs:
            _update_spec(ref, spec)


def get_field_schema(field: Field) -> Tuple[dict, List[Type[DictAble]]]:
    schema = {
        'type': field.__class__.__name__,
        'required': field.required
    }
    refs = []
    if isinstance(field, ListField):
        schema['of'], refs = get_field_schema(field.obj_type)
    if isinstance(field, UnionField):
        of = []
        for child_field in field.fields:
            child_schema, child_refs = get_field_schema(child_field)
            of.append(child_schema)
            refs += child_refs
        schema['of'] = of
    if isinstance(field, DictField):
        key_schema, key_refs = get_field_schema(field.key_type)
        value_schema, value_refs = get_field_schema(field.value_type)
        schema['of'] = {
            'key': key_schema,
            'value': value_schema
        }
        refs += key_refs
        refs += value_refs
    if isinstance(field, ObjectField):
        schema['of'] = {
            '$ref': f'#/$defs/{field.obj_type.__name__}'
        }
        refs += [field.obj_type]
    return schema, refs


def get_json_schema(schema: Type[DictAble], new_schema: bool = False) -> dict:
    try:
        if not new_schema:
            return schema.get_input_spec()
    except RecursionError:
        pass
    spec = {
        '$defs': {},
        '$root': f'#/$defs/{schema.__name__}'
    }
    _update_spec(schema, spec)
    return spec
