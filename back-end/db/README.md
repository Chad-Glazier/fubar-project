## Database Interface

The database is made up of tables, similar to those of an SQL database. The tables
are defined in [models.py](models.py). To create a new table, just create a new 
class and have it inherit the `PersistedModel` class. E.g.,

```py
class NewTable(PersistedModel):
	field_1: str
	field_2: int
	# ...
```

### Primary Keys

When you create a table like so:

```py
class NewTable(PersistedModel):
	field_1: str
	field_2: int
	# ...
```

the first field (in this case, `field_1`) will be treated as a *primary key*, which
means that it will be used to uniquely identify each record in the table.

This means that you must ensure that the first field is unique. E.g.,

```py
class User(PersistedModel):
	password: str
	username: str
```

This example would be bad practice because it uses the `password` as a primary key
even though two users *might* have the same password. If that were to happen, then the 
database would behave in unexpected ways. Instead, you should ensure that the table's
primary key is something that should always be unique. E.g.,

```py
# this table works because no two users should have the same username.
class User(PersistedModel):
	username: str
	password: str

# or, if you want to be even more safe, you could just create an ID field.
class User(PersistedModel):
	user_id: int
	username: str
	password: str
```

### Creating and Updating Records

Once you've defined a database table (as a class), then you can create, read, update,
and delete records in it. These are done with methods that follow the naming conventions
of HTTP methods: `put`, `post`, `delete`, `get`, and `patch`.

The `put` method is used to create a new record. For example,

```py
class User(PersistedModel):
	username: str
	password: str

# first, we create a user object.
new_user = User(
	username = "j_hendrix",
	password = "ASDKF3I12MK1M3"
)

# then we save it as a record in the database.
new_user.put()

# we can modify the object just like any other python dict,
new_user.password = "@)#$@M#LMK@#KJN$"
# and then update the stored record by using `put` again.
new_user.put()

# This will not create another record in the database, because 
# it has the same primary key (username) as an existing record.
```

The `put` method will work whether or not the record already exists (identity is
based on the primary key; `username` in this case). If the user already exists, 
then it will be updated to match the fields in the object. If the user doesn't already
exist, then it will be created.

The `patch` and `post` methods work the same as `put`, except that `patch` can
only be used to update an existing field and `post` can only be used to create
a new one.

These methods will not raise exceptions, instead they return Boolean values that
indicate their success:
- `patch` will return `True` if an existing record was found
and updated, and `False` if an existing record was not found. 
- `post` will return `True` if a new record was created, and
`False` if there was already a record with the same primary key.
- `put` cannot "fail" in any meaningful sense, so it does not
return anything.

### Retrieving Records

To get a record from a table, you can use the static methods of the table
class. E.g.,

```py
# to get an iteratable of all records:
for user in User.get_all():
	# ...

# to retrieve a specific record:
User.get_by_primary_key("j_hendrix")

# to retrieve a record by some fields (other than the primary key):
for user in User.get_where(password = "ASLFAMSDFKIM@#"):
	# ...

# or,
user = User.get_first_where(password = "ASLKM$@I#$@")
```
