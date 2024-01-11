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
from acslib.ccure.base import CcureConnection
from acslib.ccure import CCurePersonnel, PersonnelFilter

ccure_connection = CcureConnection()
cc_personnel = CCurePersonnel(ccure_connection)

search = PersonnelFilter()
response = cc_personnel.search(terms="Roddy Piper".split(), search_filter=search)
```

### Find a person by custom field

```python
from acslib.ccure.base import CcureConnection
from acslib.ccure import CCurePersonnel, PersonnelFilter
from acslib.ccure.search import FUZZ

ccure_connection = CcureConnection()
cc_personnel = CCurePersonnel(ccure_connection)

search = PersonnelFilter()
search.filter_fields = {"Text1": FUZZ}
response = cc_personnel.search(terms=["PER0892347"], search_filter=search)
```

### Find a Clearance by name

```python
import acslib

ccure_acs = acslib.CcureACS()
response = ccure_acs.search(search_type="clearance", terms=["suite", "door"])
```

### Find a Clearance by other field

```python
import acslib
from acslib.ccure.search import ClearanceFilter, NFUZZ

# search by ObjectID
ccure_acs = acslib.CcureACS()
response = ccure_acs.search(
    search_type="clearance",
    terms=["8897"],
    search_filter=ClearanceFilter(lookups={"ObjectID": NFUZZ})
)
```