# Access Control Systems Library


<p align="left">
<a href="https://pypi.org/project/acslib/">
    <img src="https://img.shields.io/pypi/v/acslib.svg"
        alt = "Release Status">
</a>


A library for interacting with Access Control Systems like Genetec or Ccure9k. This is a work in progress and is not ready for production use.

Currently development is heavily influenced by Ccure9k, but the goal is to abstract the differences between the two systems and provide a common
interface for interacting with them.


</p>



* Free software: MIT
* Documentation: <https://github.com/ncstate-sat/acslib>


## Features

* Currently supports Search for `Personnel` and `Clearances` in Ccure9k
* Supports search by custom fields.

## Usage

### Find a person by name

```python
import acslib

ccure_api = acslib.CcureAPI()
response = ccure_api.personnel.search(terms="Roddy Piper".split())
```

### Find a person by custom field

```python
import acslib
from acslib.ccure.search import PersonnelFilter, FUZZ

ccure_api = acslib.CcureAPI()
response = ccure_api.personnel.search(
    terms=["PER0892347"],
    search_filter=PersonnelFilter(lookups={"Text1": FUZZ})
)
```

### Find a Clearance by name

```python
import acslib

ccure_api = acslib.CcureAPI()
response = ccure_api.clearance.search(terms=["suite", "door"])
```

### Find a Clearance by other field

```python
import acslib
from acslib.ccure.search import ClearanceFilter, NFUZZ

# search by ObjectID
ccure_api = acslib.CcureAPI()
response = ccure_api.clearance.search(
    terms=["8897"],
    search_filter=ClearanceFilter(lookups={"ObjectID": NFUZZ})
)
```

### Find all credentials

```python
import acslib

ccure_api = acs.CcureAPI()
response = ccure_api.credential.search()
```

### Find a credential by personnel ID

```python
import acslib

# find all credentials associated with either of two people:
ccure_api = acslib.CcureAPI()
response = ccure_api.credential.search(terms=[5001, 5003])
```
