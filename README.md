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

* Currently supports CRUD operations for `Personnel`, `Clearances`, `Credentials`, and `ClearanceItem` in Ccure9k, and all other Ccure object types.
* Supports search by custom fields.

## Usage

### Personnel

#### Find a person by name

```python
from acslib import CcureAPI

ccure = CcureAPI()
response = ccure.personnel.search("Roddy Piper".split())
```

#### Find a person by custom field

```python
from acslib import CcureAPI
from acslib.ccure.filters import PersonnelFilter, FUZZ

ccure = CcureAPI()
search_filter = PersonnelFilter(lookups={"Text1": FUZZ})
response = ccure.personnel.search(["PER0892347"], search_filter=search_filter)
```

#### Update a personnel record

```python
from acslib import CcureAPI

# change MiddleName and Text14 for the person with CCure ID 5001
ccure = CcureAPI()
ccure.personnel.update(5001, {"Text14": "new text here", "MiddleName": "Shaquille"})
```

#### Add new personnel record

```python
from acslib import CcureAPI
from acslib.ccure.data_models import PersonnelCreateData as pcd

ccure = CcureAPI()
new_person_data = pcd(FirstName="Kenny", LastName="Smith", Text1="001132808")
ccure.personnel.create(new_person_data)
```

#### Delete a personnel record

```python
from acslib import CcureAPI

# delete the personnel record with the CCure ID 6008
ccure = CcureAPI()
ccure.personnel.delete(6008)
```

### Clearance

#### Find a Clearance by name

```python
from acslib import CcureAPI

ccure = CcureAPI()
response = ccure.clearance.search(["suite", "door"])
```

#### Find a Clearance by other field

```python
from acslib import CcureAPI
from acslib.ccure.filters import ClearanceFilter, NFUZZ

# search by ObjectID
ccure = CcureAPI()
search_filter = ClearanceFilter(lookups={"ObjectID": NFUZZ})
response = ccure.clearance.search([8897], search_filter=search_filter)
```

### Credential

#### Find all credentials

```python
from acslib import CcureAPI

ccure = CcureAPI()
response = ccure.credential.search()
```

#### Find a credential by name

```python
from acslib import CcureAPI

# fuzzy search by name
ccure = CcureAPI()
response = ccure.credential.search(["charles", "barkley"])
```

#### Find a credential by other field

```python
from acslib import CcureAPI
from acslib.ccure.filters import CredentialFilter, NFUZZ

# search by ObjectID
ccure = CcureAPI()
search_filter = CredentialFilter(lookups={"ObjectID": NFUZZ})
response = ccure.credential.search([5001], search_filter=search_filter)
```

#### Update a credential

```python
from acslib import CcureAPI

# update CardInt1 for the credential with ObjectID 5001
ccure = CcureAPI()
response = ccure.credential.update(5001, {"CardInt1": 12345})
```

### ClearanceItem

Clearance items include "door" and "elevator."

#### Find ClearanceItem by name

```python
from acslib import CcureAPI
from acslib.ccure.types import ObjectType

# fuzzy search for doors by name
ccure = CcureAPI()
response = ccure.clearance_item.search(ObjectType.DOOR.complete, ["hall", "interior"])
```

#### Find ClearanceItem by other field

```python
from acslib import CcureAPI
from acslib.ccure.filters import ClearanceItemFilter, NFUZZ
from acslib.ccure.types import ObjectType

# search elevators by ObjectID
ccure = CcureAPI()
search_filter = ClearanceItemFilter(lookups={"ObjectID": NFUZZ})
response = ccure.clearance_item.search(ObjectType.ELEVATOR.complete, [5000], search_filter=search_filter)
```

#### Get a door's lock state

```python
from acslib import CcureAPI

# get lock state for door 5001. eg. "Unlocked", "Locked", etc
ccure = CcureAPI()
response = ccure.clearance_item.get_lock_state(5001)
```

#### Update ClearanceItem

```python
from acslib import CcureAPI
from acslib.ccure.types import ObjectType

# change a door's name
ccure = CcureAPI()
response = ccure.clearance_item.update(ObjectType.DOOR.complete, 5000, update_data={"Name": "new door name 123"})
```

#### Create ClearanceItem

```python
from acslib import CcureAPI
from acslib.ccure.data_models import ClearanceItemCreateData
from acslib.ccure.types import ObjectType

# create a new elevator
ccure = CcureAPI()
new_elevator_data = ClearanceItemCreateData(
    Name="New elevator 1",
    Description="newest elevator in town",
    ParentID=5000,
    ParentType="SoftwareHouse.NextGen.Common.SecurityObjects.iStarController",
    ControllerID=5000,
    ControllerClassType="SoftwareHouse.NextGen.Common.SecurityObjects.iStarController"
)
response = ccure.clearance_item.create(ObjectType.ELEVATOR.complete, create_data=new_elevator_data)
```

#### Delete ClearanceItem

```python
from acslib import CcureAPI
from acslib.ccure.types import ObjectType

# delete a door
ccure = CcureAPI()
response = ccure.clearance_item.delete(ObjectType.DOOR.complete, 5000)
```

### Other item types

#### Search for CCure item

```python
from acslib import CcureAPI
from acslib.ccure.filters import CcureFilter, NFUZZ

# search for schedule objects by ObjectID
ccure = CcureAPI()
schedule_type_full = "SoftwareHouse.CrossFire.Common.Objects.TimeSpec"
search_filter = CcureFilter()
response = ccure.ccure_object.search(
    object_type=schedule_type_full,
    search_filter=search_filter,
    terms=[5001]
)
```

### Other common actions

Use `ccure.action` to perform some common tasks like assigning or revoking clearances or getting personnel images.

#### Assign a clearance

```python
from acslib import CcureAPI

# assign clearances 5002 and 5003 to person 5005
ccure = CcureAPI()
response = ccure.action.personnel.assign_clearances(
    personnel_id=5005,
    clearance_ids=[5002, 5003],
)
```

#### Lock a door

```python
from datetime import datetime, timedelta
from acslib import CcureAPI

# lock door 5050 for ten minutes
ccure = CcureAPI()
response = ccure.action.door.lock(
    door_id=5050,
    lock_time=datetime.now(),
    unlock_time=datetime.now() + timedelta(minutes=10),
)
```
