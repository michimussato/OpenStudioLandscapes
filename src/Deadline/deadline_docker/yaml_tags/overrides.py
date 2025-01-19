from yaml import YAMLObject


__all__ = [
    "OverrideArray",
]


class OverrideArray(YAMLObject):
    """
    - https://pyyaml.org/wiki/PyYAMLDocumentation
    - https://stackoverflow.com/questions/26744956/formatting-custom-class-output-in-pyyaml
    """
    yaml_tag = u'!override'
    yaml_flow_style = False

    def __init__(self, array):
        self.array = array

    @classmethod
    def to_yaml(cls, dumper, data):
        node = dumper.represent_sequence(u'!override', data.array)
        return node

    @classmethod
    def from_yaml(cls, loader, node):
        array = loader.construct_sequence(node)
        return OverrideArray(array)

    def __repr__(self):
        return "%s(ports=%r)" % (
            self.__class__.__name__, self.array)