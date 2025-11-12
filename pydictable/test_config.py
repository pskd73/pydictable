from unittest import TestCase

from pydictable import ConfigDict
from pydictable.config import merge_configs


class TestConfig(TestCase):

    def test_merge_configs(self):
        conf1 = ConfigDict()
        conf2 = ConfigDict()
        merged_config = merge_configs(conf1, conf2)
        self.assertEqual(merged_config.str_strip_whitespace, None)

        conf1 = ConfigDict()
        conf2 = ConfigDict(str_strip_whitespace=True)
        merged_config = merge_configs(conf1, conf2)
        self.assertEqual(merged_config.str_strip_whitespace, True)

        conf1 = ConfigDict(str_strip_whitespace=True)
        conf2 = ConfigDict()
        merged_config = merge_configs(conf1, conf2)
        self.assertEqual(merged_config.str_strip_whitespace, True)

        conf1 = ConfigDict(str_strip_whitespace=False)
        conf2 = ConfigDict(str_strip_whitespace=True)
        merged_config = merge_configs(conf1, conf2)
        self.assertEqual(merged_config.str_strip_whitespace, True)

        conf1 = ConfigDict(str_strip_whitespace=True)
        conf2 = ConfigDict(str_strip_whitespace=False)
        merged_config = merge_configs(conf1, conf2)
        self.assertEqual(merged_config.str_strip_whitespace, False)
