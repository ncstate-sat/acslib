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

* Currently supports Search for `Personnel`, `Clearances`, and `Credentials` in Ccure9k
* Supports search by custom fields.

## Usage

### Find a person by name

```python
import acslib

ccure_api = acslib.CcureAPI()
response = ccure_api.personnel.search("Roddy Piper".split())
```

### Find a person by custom field

```python
import acslib
from acslib.ccure.search import PersonnelFilter, FUZZ

ccure_api = acslib.CcureAPI()
search_filter = PersonnelFilter(lookups={"Text1": FUZZ})
response = ccure_api.personnel.search(["PER0892347"], search_filter=search_filter)
```

### Find a Clearance by name

```python
import acslib

ccure_api = acslib.CcureAPI()
response = ccure_api.clearance.search(["suite", "door"])
```

### Find a Clearance by other field

```python
import acslib
from acslib.ccure.search import ClearanceFilter, NFUZZ

# search by ObjectID
ccure_api = acslib.CcureAPI()
search_filter = ClearanceFilter(lookups={"ObjectID": NFUZZ})
response = ccure_api.clearance.search([8897], search_filter=search_filter)
```

### Find all credentials

```python
import acslib

ccure_api = acs.CcureAPI()
response = ccure_api.credential.search()
```

### Find a credential by name

```python
import acslib

# fuzzy search by name
ccure_api = acslib.CcureAPI()
response = ccure_api.credential.search(["charles", "barkley"])
```

### Find a credential by other field

```python
import acslib
from acslib.ccure.search import CredentialFilter, NFUZZ

# search by ObjectID
ccure_api = acslib.CcureAPI()
search_filter = CredentialFilter(lookups={"ObjectID": NFUZZ})
response = ccure_api.credential.search([5001], search_filter=search_filter)
```

### Update a credential

```python
import acslib

# update CardInt1 for the credential with ObjectID 5001
ccure_api = acslib.CcureAPI()
response = ccure_api.credential.update(5001, {"CardInt1": 12345})
```
