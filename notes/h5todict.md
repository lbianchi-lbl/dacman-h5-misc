# `h5todict`

- Reads an HDF5 file and returns a dict-like representation of its contents, similarly to `h5ls -r`
- The output (i.e. `HDF5PropertiesGatherer.data`) is:
    - Python dictionary if used within a Python program
    - JSON string if used from the CLI (print to STDOUT or to file if a second CLI argument is given)

## Testing with other files

The source is mostly the official HDF5 example files at <https://support.hdfgroup.org/ftp/HDF5/examples/files/exbyapi/>.

To run the test suite:

1. Install `pytest`
1. Add any number of HDF5 (with the `.h5` extension in the `example-data` directory
1. Run `pytest tests.py`

- Some dtypes are not supported by the h5py backend, and cause errors when trying to access certain properties
    - Apparently related to known issues, e.g. https://github.com/astropy/astropy/issues/6473, https://stackoverflow.com/questions/55480704
    - Since this does not affect our intended use case very much (at least for now), I opted for a quick fix using try/except and storing any errors along with the data in a separate property
