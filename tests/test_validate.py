import pytest
from dataenforce import Dataset, validate
import pandas as pd
import numpy as np
from datetime import datetime

def test_validate_columns():
    df1 = pd.DataFrame(dict(a=[1,2,3]))
    df2 = pd.DataFrame(dict(a=[1,2,3], b=[4,5,6]))
    df3 = pd.DataFrame(dict(a=[1,2,3], b=[4,5,6], c=[7,8,9]))

    @validate
    def process(data: Dataset["a", "b"]):
        pass

    process(df2)
    with pytest.raises(TypeError):
        process(df1)
    with pytest.raises(TypeError):
        process(df3)

def test_validate_combination():
    df1 = pd.DataFrame(dict(a=[1,2,3]))
    df2 = pd.DataFrame(dict(a=[1,2,3], b=[4,5,6]))

    @validate
    def process(data1: Dataset["a"], data2: Dataset["a", "b"]):
        pass

    process(df1, df2)

def test_validate_ellipsis():
    df1 = pd.DataFrame(dict(a=[1,2,3]))
    df2 = pd.DataFrame(dict(a=[1,2,3], b=[4,5,6]))
    df3 = pd.DataFrame(dict(a=[1,2,3], b=[4,5,6], c=[7,8,9]))

    @validate
    def process(data: Dataset["a", "b", ...]):
        pass

    process(df2)
    process(df3)
    with pytest.raises(TypeError):
        process(df1)

def test_validate_empty():
    df = pd.DataFrame(dict(a=[1,2,3]))

    @validate
    def process(data: Dataset[...]):
        pass

    process(df)

    with pytest.raises(TypeError):
        process(False)

def test_validate_dtypes():
    df = pd.DataFrame(dict(a=[1,2,3], b=[4.1,5.1,6.1], c=["a", "b", "c"], d=[datetime.now().replace(hour=x) for x in [7,8,9]]))

    @validate
    def process1(data: Dataset["a": int, "b": np.float, "c": object, "d": np.datetime64]):
        pass
    @validate
    def process2(data: Dataset["a": float, "b", ...]):
        pass
    @validate
    def process3(data: Dataset["a": np.datetime64, ...]):
        pass

    process1(df)
    with pytest.raises(TypeError):
        process2(df)
    with pytest.raises(TypeError):
        process3(df)

def test_validate_other_types():
    df = pd.DataFrame(dict(a=[1,2,3]))

    @validate
    def process(data: Dataset["a"], other: int):
        pass

    process(df, 3)

def test_return_type():
    df = pd.DataFrame(dict(a=[1,2,3]))

    class Klass:
        pass

    @validate
    def process(data: Dataset["a"]) -> int:
        return 2
    
    @validate
    def process2(data: Dataset["a"]) -> Klass:
        return Klass()

    #@validate
    #def process3(data: Dataset["a"]) -> "Klass":
    #    return Klass()

    process(df)
    process2(df)
    #process3(df) # -> This scenario fails, issue with eval in get_type_hints (read PEP 563)