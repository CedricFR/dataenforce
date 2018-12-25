# Overview

`dataenforce` is a Python package used to enforce column names & types of pandas DataFrames using Python 3 type hinting.

It is a common issue in Data Analysis to pass dataframes into functions without a clear idea of which columns are included or not, and as columns are added to or removed from input data, code can break in unexpected ways. With `dataenforce`, you can provide a clear interface to your functions and ensure that the input dataframes will have the right format when your code is used.

# How to install

Install with pip:
```
pip install dataenforce
```

You can also pip install it from the sources, or just import the `dataenforce` folder.

# How to use

There are two parts in `dataenforce`: the type-hinting part, and the validation. You can use type-hinting with the provided class to indicate what shape the input dataframes should have, and the validation decorator to additionally ensure the format is respected in every function call.

## Type-hinting: `Dataset`

The `Dataset` type indicates that we expect a `pandas.DataFrame`

### Column name checking

```py
from dataenforce import Dataset

def process_data(data: Dataset["id", "name", "location"])
  pass
```

The code above specifies that `data` must be a DataFrame with exactly the 3 mentioned columns. If you want to only specify a subset of columns which is required, you can use an ellipsis:
```py
def process_data(data: Dataset["id", "name", "location", ...])
  pass
```

### dtype checking

```py
def process_data(data: Dataset["id": int, "name": object, "latitude": float, "longitude": float])
  pass
```

The code above specifies the column names which must be there, with associated types. A combination of only names & with types is possible: `Dataset["id": int, "name"]`.

### Reusing dataframe formats

As you're likely to use the same column subsets several times in your code, you can define them to reuse & combine them later:
```py
DName = Dataset["id", "name"]
DLocation = Dataset["id", "latitude", "longitude"]

# Expects columns id, name
def process1(data: DName):
  pass

# Expects columns id, name, latitude, longitude, timestamp
def process2(data: Dataset[DName, DLocation, "timestamp"])
  pass
```

## Enforcing: `@validate`

The `@validate` decorator ensures that input `Dataset`s have the right format when the function is called, otherwise raises `TypeError`.

```py
from dataenforce import Dataset, validate
import pandas as pd

@validate
def process_data(data: Dataset["id", "name"]):
  pass

process_data(pd.DataFrame(dict(id=[1,2], name=["Alice", "Bob"]))) # Works
process_data(pd.DataFrame(dict(id=[1,2]))) # Raises a TypeError, column name missing
```

# How to test

`dataenforce` uses `pytest` as a testing library. If you have `pytest` installed, just run `pytest` in the command line while being in the root folder.

# Notes

* You can use `dataenforce` to type-hint the return value of a function, but it is not currently possible to `validate` it (it is not included in the checks)
* `dataenforce` is released under the Apache License 2.0, meaning you can freely use the library and redistribute it, provided Copyright is kept
* Dependencies: Pandas & Numpy
