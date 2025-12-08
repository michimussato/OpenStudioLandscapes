from OpenStudioLandscapes.engine.features import (
    FeatureBase,
)


def test_feature():
    feature1_dict = {
        "feature_name": "feature1",
        "compose_scope": "default",
        "key_prefixes": ["prefix1", "prefix2"],
        "group_name": "Group 1-1",
        "definitions": "Namespace.feature1.definitions",
    }

    feature2_dict = {
        "feature_name": "feature2",
        "compose_scope": "default",
        "key_prefixes": ["prefix3", "prefix4"],
        "group_name": "Group 5.4",
        "definitions": "Namespace.feature2.definitions",
    }

    # Subclass FeatureBase
    class MyFeature1(FeatureBase):
        pass

    class MyFeature2(FeatureBase):
        pass

    # Create objects based on model using dicts
    feature1 = MyFeature1(**feature1_dict)
    feature2 = MyFeature2(**feature2_dict)

    # Verify that group_name
    # - is lower case
    # - does not contain special chars
    assert feature1.group_name == "group_1_1"
    assert feature2.group_name == "group_5_4"

    # Verify the contents of __dict__
    assert feature1.__dict__ == {
        'enabled': True,
        'compose_scope': 'default',
        'feature_name': 'feature1',
        'group_name': 'group_1_1',
        'key_prefixes': ['prefix1', 'prefix2'],
        'docker_compose': '{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml',
        'definitions': 'Namespace.feature1.definitions'
    }
    assert feature2.__dict__ == {
        'compose_scope': 'default',
        'definitions': 'Namespace.feature2.definitions',
        'docker_compose': '{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml',
        'enabled': True,
        'feature_name': 'feature2',
        'group_name': 'group_5_4',
        'key_prefixes': ['prefix3', 'prefix4']
    }

    # Verify that __str__() is something meaningful
    assert feature1.__str__() == "feature1"
    assert feature2.__str__() == "feature2"

    # Verify that __repr__() is something meaningful
    assert feature1.__repr__() == (
        "Feature(['enabled=True', 'compose_scope=default', 'feature_name=feature1', "
        '\'group_name=group_1_1\', "key_prefixes=[\'prefix1\', \'prefix2\']", '
        "'docker_compose={DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml', "
        "'definitions=Namespace.feature1.definitions'])"
    )
    assert feature2.__repr__() == (
        "Feature(['enabled=True', 'compose_scope=default', 'feature_name=feature2', "
        '\'group_name=group_5_4\', "key_prefixes=[\'prefix3\', \'prefix4\']", '
        "'docker_compose={DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml', "
        "'definitions=Namespace.feature2.definitions'])"
    )

    # Verify that the subclasses actually are in the FeatureBase.subclass dict
    # {
    #     'MyFeature1': <class 'test_feature.test_feature.<locals>.MyFeature1'>,
    #     'MyFeature2': <class 'test_feature.test_feature.<locals>.MyFeature2'>,
    # }
    assert FeatureBase.subclasses == {
        MyFeature1.__name__: MyFeature1,
        MyFeature2.__name__: MyFeature2,
    }
