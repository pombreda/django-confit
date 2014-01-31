# -*- coding: utf-8 -*-
"""Utilities to load configuration from various sources:

* from :attr:`os.environ` or similar dictionary:
  :func:`settings_from_string_mapping`;

* from Python module: :func:`settings_from_module`;

* from JSON or YAML file: :func:`settings_from_file`.

"""
import json

import six
import yaml


def settings_from_string_mapping(input, prefix=''):
    """Convert mapping of {key: string} to {key: complex type}.

    Simple key-value stores (flat mappings) are supported:

    >>> flat_mapping = {'DEBUG': 'True', 'SECRET_KEY': 'not a secret'}
    >>> output = settings_from_string_mapping(flat_mapping)
    >>> output == flat_mapping
    True

    Values can be complex types (sequences, mappings) using JSON or YAML.
    Keys using ".json" or ".yaml" suffix are automatically decoded:

    >>> nested_mapping = {
    ...     'DATABASES.yaml': 'ENGINE: sqlite3',
    ... }
    >>> output = settings_from_string_mapping(nested_mapping)
    >>> output['DATABASES'] == {'ENGINE': 'sqlite3'}
    True

    You can use optional ``prefix`` argument to load only a subset of mapping:

    >>> mapping = {'YES_ONE': '1', 'NO_TWO': '2'}
    >>> settings_from_string_mapping(mapping, prefix='YES_')
    {'ONE': '1'}

    """
    output = {}
    for key, value in six.iteritems(input):
        if key.startswith(prefix):
            key = key[len(prefix):]
            if key.endswith('.json'):
                output[key[:-5]] = json.loads(value)
            elif key.endswith('.yaml'):
                output[key[:-5]] = yaml.load(value)
            else:
                output[key] = value
    return output


def settings_from_file(file_obj):
    """Return mapping from filename.

    Supported file formats are JSON and YAML. The lowercase extension is used
    to guess the file type.

    >>> from six.moves import StringIO
    >>> file_obj = StringIO('SOME_LIST: [a, b, c]')
    >>> file_obj.name = 'something.yaml'
    >>> settings_from_file(file_obj) == {
    ...     'SOME_LIST': ['a', 'b', 'c'],
    ... }
    True

    """
    file_name = file_obj.name
    if file_name.endswith('.yaml'):
        return yaml.load(file_obj)
    elif file_name.endswith('.json'):
        return json.load(file_obj)
    else:
        raise ValueError(
            'Cannot guess format of configuration file "{name}". '
            'Expected one of these extensions: "{extensions}".'.format(
                name=file_name,
                extensions='", "'.join('.yaml', '.json')))


def settings_from_module(module_path):
    """Import settings from module's globals and return them as a dict.

    >>> settings = settings_from_module('django.conf.global_settings')
    >>> settings['DATABASES']
    {}
    >>> '__name__' in settings
    False

    """
    module = __import__(module_path, fromlist='*', level=0)
    is_uppercase = lambda x: x.upper() == x
    is_special = lambda x: x.startswith('_')
    return dict([(key, value) for key, value in module.__dict__.items()
                 if is_uppercase(key) and not is_special(key)])