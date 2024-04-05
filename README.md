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

* Currently supports Search for `Personnel`, `Clearances`, `Credentials`, and `ClearanceItem` in Ccure9k
* Supports search by custom fields.

## Usage

### Personnel

#### Find a person by name

```python
from acslib import CcureAPI

ccure_api = CcureAPI()
response = ccure_api.personnel.search("Roddy Piper".split())
```

#### Find a person by custom field

```python
from acslib import CcureAPI
from acslib.ccure.filters import PersonnelFilter, FUZZ

ccure_api = CcureAPI()
search_filter = PersonnelFilter(lookups={"Text1": FUZZ})
response = ccure_api.personnel.search(["PER0892347"], search_filter=search_filter)
```

### Clearance

#### Find a Clearance by name

```python
from acslib import CcureAPI

ccure_api = CcureAPI()
response = ccure_api.clearance.search(["suite", "door"])
```

#### Find a Clearance by other field

```python
from acslib import CcureAPI
from acslib.ccure.filters import ClearanceFilter, NFUZZ

# search by ObjectID
ccure_api = CcureAPI()
search_filter = ClearanceFilter(lookups={"ObjectID": NFUZZ})
response = ccure_api.clearance.search([8897], search_filter=search_filter)
```

### Credential

#### Find all credentials

```python
from acslib import CcureAPI

ccure_api = CcureAPI()
response = ccure_api.credential.search()
```

#### Find a credential by name

```python
from acslib import CcureAPI

# fuzzy search by name
ccure_api = CcureAPI()
response = ccure_api.credential.search(["charles", "barkley"])
```

#### Find a credential by other field

```python
from acslib import CcureAPI
from acslib.ccure.filters import CredentialFilter, NFUZZ

# search by ObjectID
ccure_api = CcureAPI()
search_filter = CredentialFilter(lookups={"ObjectID": NFUZZ})
response = ccure_api.credential.search([5001], search_filter=search_filter)
```

#### Update a credential

```python
from acslib import CcureAPI

# update CardInt1 for the credential with ObjectID 5001
ccure_api = CcureAPI()
response = ccure_api.credential.update(5001, {"CardInt1": 12345})
```

### ClearanceItem

Clearance items include "door" and "elevator."

#### Find ClearanceItem by name

```python
from acslib import CcureAPI
from acslib.ccure.types import ClearanceItemType as cit

# fuzzy search for doors by name
ccure_api = CcureAPI()
response = ccure_api.clearance_item.search(cit.DOOR, ["hall", "interior"])
```

#### Find ClearanceItem by other field

```python
from acslib import CcureAPI
from acslib.ccure.filters import ClearanceItemFilter, NFUZZ
from acslib.ccure.types import ClearanceItemType as cit

# search elevators by ObjectID
ccure_api = CcureAPI()
search_filter = ClearanceItemFilter(lookups={"ObjectID": NFUZZ})
response = ccure_api.clearance_item.search(cit.ELEVATOR, [5000], search_filter=search_filter)
```

#### Update ClearanceItem

```python
from acslib import CcureAPI
from acslib.ccure.types import ClearanceItemType as cit
# change a door's name
ccure_api = CcureAPI()
response = ccure_api.clearance_item.update(cit.DOOR, 5000, update_data={"Name": "new door name 123"})
```

#### Create ClearanceItem

```python
from acslib import CcureAPI
from acslib.ccure.types import ClearanceItemCreateData, ClearanceItemType as cit

# create a new elevator
ccure_api = CcureAPI()
new_elevator_data = ClearanceItemCreateData(
    Name="New elevator 1",
    Description="newest elevator in town",
    ParentID=5000,
    ParentType="SoftwareHouse.NextGen.Common.SecurityObjects.iStarController",
    ControllerID=5000,
    ControllerClassType="SoftwareHouse.NextGen.Common.SecurityObjects.iStarController"
)
response = ccure_api.clearance_item.create(cit.ELEVATOR, create_data=new_elevator_data)
```

#### Delete ClearanceItem

```python
from acslib import CcureAPI
from acslib.ccure.types import ClearanceItemType as cit
# delete a door
ccure_api = CcureAPI()
response = ccure_api.clearance_item.delete(cit.DOOR, 5000)
```
