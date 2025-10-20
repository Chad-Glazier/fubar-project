# FUBAR Project

Under construction

![bob the builder](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwwwimage-us.pplusstatic.com%2Fthumbnails%2Fphotos%2Fw1920-q80%2Fmarquee%2F1035369%2Fbobc_sp_hero_landscape.jpg&f=1&nofb=1&ipt=4a172924ac2ce281793ea635e8adf4787380d5d7f213a60b563dc5feabf36a7b)

## To Do

In the `back-end/models` part:

- The `save` function can be generalized up to the `BaseModelWithCSV` class (which 
should probably also be given a more appropriate name).
- We need a mutex to prevent concurrent writing. However, reading while writing
is fine because the `os.replace` function is atomic; i.e., it's not possible
for the data table CSV file to be part-way through an update when it is read. Since 
each class has its own table, there should be an independent mutex for each class. 
I.e., a static field. However, I'm not sure if python has real static members anyway;
it might instead be necessary to look into existing mutex libraries.
- After those changes, need to write more tests in `test_BaseModelWithCSV.py`
- Then we need to be able to retrieve model instances from the CSV files.

Later:
- After the models are sorted out, we can start implementing request handlers to
interact with the "database."
