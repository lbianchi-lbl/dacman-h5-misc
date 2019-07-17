
# `h5diff` feature analysis

## Features

- Recursive comparison depending on object type
    - Group
        - Compare names of top-level objects (i.e. relative path from group)
        - Using the names, generate report of objs: common to both A and B; only in A; only in B
        - Common objects are compared recursively
    - File
        - Compare names of top-level objects (i.e. relative path from group)
        - Using the names, generate report of objs: common to both A and B; only in A; only in B
        - Common objects are compared recursively
    - Dataset
        - Compares: array rank, dimensions, datatypes, and data values
            - Comparison of array values looks similar to Dac-Man records
    - Symbolic links
        - Compare their targets, i.e. the path to which they point to
- Basic change statistics to filter output
    - Count: show up to N differences
    - Delta: show differences if `(|a-b| > D)`
    - Relative delta: show if `(|(a-b)/b| > R)`
- Optionally exclude/ignore object paths
- Optionally use system epsilon to filter out false positives due to float precision
    - Show difference if `(|a-b| > EPSILON)`
- Select level of info/verbosity
    - `0`: Print difference information + list of objects
    - `1`: Same as `0` + one-line summary for each attribute
    - `2`: Same as `1` + extended summary for each attribute
        - i.e. attributes are treated similar to arrays

## Limitations

- Depends on name to define object identity
    - Objects need to have the same name to be compared, unless otherwise specified at the CLI
    - No heuristics to detect same objects with different name
- No structured output
    - Human- but not machine-readable
- No advanced/semantically relevant comparisons
    - e.g. for change in attribute `owner_of` in example files (`egomez` -> `Russel`):

        ```txt
        attribute: <owner of </>> and <owner of </>>
            size:           H5S_SCALAR           H5S_SCALAR
        position        owner of </>    owner of </>    difference
        ------------------------------------------------------------
        [ 0]            e            R
        [ 1]            g            u
        [ 2]            o            s
        [ 3]            m            s
        [ 5]            z            l
        6 differences found
        ```

## Modes of operation

- `h5diff fileA fileB /foo/data1 /bar/data2`
    - Two files and two object names
    - Assume they refer to the same object
    - Compare them

- `h5diff fileA fileB /foo/data1`
    - Two files, one object name
    - Compare object with that name in both files

- `h5diff fileA fileA /foo/data1 /bar/data2`
    - One file, two object names
    - Compare objects within the same file
    - File must still be specified as CLI arg

- `h5diff fileA fileB`
    - Two files
    - Compare contents (recursively if `-r` flag) as explained above
