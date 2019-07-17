#!/usr/bin/env python3.6

from pathlib import Path
import collections
import json

import h5py as h5
import numpy as np


def extra_serializer(o):
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, bytes):
        # HDF5 text is read into Python as `bytes` objects
        # we decode them to strings when serializing to JSON
        # since JSON doesn't support raw bytes,
        # and the default serializer uses base64 encoder which is not human-readable
        return o.decode()
    else:
        # fallback case for complex datatypes?
        return repr(o)
    raise TypeError


def to_json(data):
    return json.dumps(data,
                      default=extra_serializer,
                      indent=4,
                      separators=(',', ': ')
                     )


def to_dict_basic_types(data):
    return json.loads(to_json(data))


def collect_from_obj(d, name=None, obj=None):

    d['name'] = name
    d['id'] = obj.id.id
    d['attributes'] = dict(obj.attrs)
    d['type_h5'] = type(obj).__name__
    d['type_h5py'] = type(obj)


def collect_from_dataset(d, dataset):

    d['name'] = dataset.name
    d['shape'] = dataset.shape
    d['ndim'] = dataset.ndim

    try:
        dtype = dataset.dtype
    except Exception as e:
        dtype = None
        d['dtype_error'] = str(e)

    d['dtype'] = dtype


def collect_from_dataset_value(d, dataset):

    value =  dataset[()]

    d['type_value'] = type(value)
    d['value'] = value


def collect_from_group(d, group):

    counter = collections.Counter(type(obj).__name__ for obj in group.values())

    id_ = group.id

    d['fileno'] = id_.fileno
    d['num_objs'] = dict(counter)
    d['num_objs']['total'] = id_.get_num_objs()

def collect_from_file(d, file):
    d['filename'] = file.filename


class ObjMetadataCollector:
    """
    Collect metadata from a single h5 Object.
    """

    def __init__(self, *, obj=None, name=None):
        
        self.obj = obj
        self.name = name

        self._data = {}

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, val):
        self._data[key] = val

    def keys(self):
        return self._data.keys()

    @property
    def is_dataset(self):
        return isinstance(self.obj, h5.Dataset)

    @property
    def is_group(self):
        return isinstance(self.obj, h5.Group)

    @property
    def is_file(self):
        return isinstance(self.obj, h5.File)

    def collect(self):

        collect_from_obj(self, obj=self.obj, name=self.name)

        if self.is_dataset:
            self['dataset'] = {}
            collect_from_dataset(self['dataset'], self.obj)
            collect_from_dataset_value(self['dataset'], self.obj)

        if self.is_group:
            self['group'] = {}
            collect_from_group(self['group'], self.obj)

        if self.is_file:
            self['file'] = {}
            collect_from_file(self['file'], self.obj)


class RecursiveMetadataCollector:
    """
    Recursively collect metadata for all Objects in a Group or File.
    """

    @classmethod
    def from_file(cls, file, key=None, **kwargs):

        key = key or file.name
        
        self = cls(**kwargs)
        
        self.visit(key, file)
        file.visititems(self.visit)

        # here we could in principle close the file,
        # since at this point we have all the data we need

        return self

    def __init__(self):
        
        self._items = []
        
    def __iter__(self):
        return iter(self._items)

    def add(self, props):
        self._items.append(props)

    def visit(self, name, obj):

        metadata = ObjMetadataCollector(obj=obj, name=name)

        metadata.collect()

        self.add(dict(metadata))


class Record:
    """
    An indexed collection of metadata items.

    `key_getter`: a function that returns the index key when applied to each metadata item.
    """

    @staticmethod
    def default_key_getter(md):
        return md['name']

    def __init__(self, source, key_getter=None, **kwargs):

        metadata_items = RecursiveMetadataCollector.from_file(source)

        self.key_getter = key_getter or self.default_key_getter

        self._map = {self.key_getter(md): md for md in metadata_items}

    def keys(self):
        return self._map.keys()

    def values(self):
        return self._map.values()

    def items(self):
        return self._map.items()

    def __getitem__(self, key):
        return self._map[key]

    def get(self, *args, **kwargs):
        return self._map.get(*args, **kwargs)

    def display(self, mode='json'):
        print(to_json(self._map))

    def _ipython_display_(self):
        from IPython.display import display, JSON

        display(JSON(to_dict_basic_types(self._map)))


def main():
    import sys
    
    path_in = Path(sys.argv[1])
    
    path_out = None

    if len(sys.argv) > 2:
        path_out = Path(sys.argv[2])

    mode_read_only = 'r'
    try:
        file = h5.File(path_in, mode_read_only)
        record = Record(file, key_getter=Record.default_key_getter)
        record.display(mode='json')

    except Exception as e:
        print(f'Error: {repr(e)}', file=sys.stderr)
        sys.exit(1)
    finally:
        file.close()

        
if __name__ == '__main__':
    main()
