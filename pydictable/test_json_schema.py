from unittest import TestCase
from pydictable import DictAble, StrField, ListField, ObjectField, UnionField
from pydictable.json_schema import get_json_schema


class TestJSONSchema(TestCase):
    def test_basic_json_schema(self):
        class Person(DictAble):
            name = StrField()

        schema = get_json_schema(Person)
        self.assertEqual(schema, {
            '$defs': {
                'Person': {
                    'name': {
                        'required': False,
                        'type': 'StrField'
                    }
                }
            },
            '$root': '#/$defs/Person'
        })

    def test_cyclic_ref(self):
        class B(DictAble):
            pass

        class A(DictAble):
            ibs = ListField(ObjectField(B))

        B.ias = UnionField([ObjectField(A), StrField()])
        schema = get_json_schema(A)
        self.assertEqual(
            schema,
            {
                '$defs': {
                    'A': {
                        'ibs': {
                            'type': 'ListField',
                            'required': False,
                            'of': {
                                'type': 'ObjectField',
                                'required': False,
                                'of': {
                                    '$ref': '#/$defs/B'
                                }
                            }
                        }
                    },
                    'B': {
                        'ias': {
                            'type': 'UnionField',
                            'required': False,
                            'of': [
                                {
                                    'type': 'ObjectField',
                                    'required': False,
                                    'of': {
                                        '$ref': '#/$defs/A'
                                    }
                                },
                                {
                                    'type': 'StrField',
                                    'required': False
                                }
                            ]
                        }
                    }
                },
                '$root': '#/$defs/A'
            }
        )
