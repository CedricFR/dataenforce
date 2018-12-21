import inspect
from functools import wraps
import pandas as pd
from typing import GenericMeta, _TypingEmpty, _tp_cache, Generic,get_type_hints
import numpy as np

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
                    raise TypeError("%s is not a pandas Dataframe" % argument_value)
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

    @_tp_cache
    def __getitem__(self, parameters):
        if self.__origin__ is not None or self._gorg is not Dataset:
            # Normal generic rules apply if this is not the first subscription
            # or a subscription of a subclass.
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
        if cls._gorg is Dataset:
            raise TypeError("Type Dataset cannot be instantiated; "
                            "use pandas.DataFrame() instead")
        return _generic_new(pd.DataFrame, cls, *args, **kwds)
