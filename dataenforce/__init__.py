# Copyright 2018 Cedric Canovas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
from functools import wraps
import pandas as pd
from typing import _TypingEmpty, _tp_cache, Generic, get_type_hints
import numpy as np
try:
    from typing import GenericMeta # Python 3.6
except ImportError: # Python 3.7 
    class GenericMeta(type): pass

def validate(f):
    signature = inspect.signature(f)
    hints = get_type_hints(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)

        for argument_name, value in bound.arguments.items():
            if argument_name in hints and isinstance(hints[argument_name], DatasetMeta):
                hint = hints[argument_name]

                if not isinstance(value, pd.DataFrame):
                    raise TypeError("%s is not a pandas Dataframe" % value)
                columns = set(value.columns)
                if hint.only_specified and not columns == hint.columns:
                    raise TypeError("%s columns do not match required column set %s" % (argument_name, hint.columns))
                if not hint.only_specified and not hint.columns.issubset(columns):
                    raise TypeError("%s is missing some columns from %s" % (argument_name, hint.columns))
                if hint.dtypes:
                    dtypes = dict(value.dtypes)
                    for colname, dt in hint.dtypes.items():
                        if not np.issubdtype(dtypes[colname], np.dtype(dt)):
                            raise TypeError("%s is not a subtype of %s for column %s" % (dtypes[colname], dt, colname))
        return f(*args, **kwargs)

    return wrapper

def _get_columns_dtypes(p):
    columns = set()
    dtypes = {}

    if isinstance(p, str):
        columns.add(p)
    elif isinstance(p, slice):
        columns.add(p.start)
        if not inspect.isclass(p.stop):
            raise TypeError("Column type hints must be classes, error with %s" % repr(p.stop))
        dtypes[p.start] = p.stop
    elif isinstance(p, (list, set)):
        for el in p:
            subcolumns, subdtypes = _get_columns_dtypes(el)
            columns |= subcolumns
            dtypes.update(subdtypes)
    elif isinstance(p, DatasetMeta):
        columns |= p.columns
        dtypes.update(p.dtypes)
    else:
        raise TypeError("Dataset[col1, col2, ...]: each col must be a string, list or set.")

    return columns, dtypes

class DatasetMeta(GenericMeta):
    """Metaclass for Dataset (internal)."""

    def __new__(metacls, name, bases, namespace, **kargs):
        return super().__new__(metacls, name, bases, namespace)

    @_tp_cache
    def __getitem__(self, parameters):
        if hasattr(self, '__origin__') and (self.__origin__ is not None or self._gorg is not Dataset):
            return super().__getitem__(parameters)
        if parameters == ():
            return super().__getitem__((_TypingEmpty,))
        if not isinstance(parameters, tuple):
            parameters = (parameters,)
        parameters = list(parameters)

        only_specified = True
        if parameters[-1] is ...:
            only_specified = False
            parameters.pop()

        columns, dtypes = _get_columns_dtypes(parameters)

        meta = DatasetMeta(self.__name__, self.__bases__, {})
        meta.only_specified = only_specified
        meta.columns = columns
        meta.dtypes = dtypes

        return meta

class Dataset(pd.DataFrame, extra=Generic, metaclass=DatasetMeta):
    """Defines type Dataset to serve as column name & type enforcement for pandas DataFrames"""
    __slots__ = ()

    def __new__(cls, *args, **kwds):
        if not hasattr(cls, '_gorg') or cls._gorg is Dataset:
            raise TypeError("Type Dataset cannot be instantiated; "
                            "use pandas.DataFrame() instead")
        return _generic_new(pd.DataFrame, cls, *args, **kwds)
