import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dataenforce",
    version="0.1.1",
    author="Cedric Canovas",
    author_email="dev@canovas.me",
    description="Enforce column names & data types of pandas DataFrames",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CedricFR/dataenforce",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License"
    ],
)
