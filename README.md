# FUBAR Project

Under construction

![bob the builder](https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwwwimage-us.pplusstatic.com%2Fthumbnails%2Fphotos%2Fw1920-q80%2Fmarquee%2F1035369%2Fbobc_sp_hero_landscape.jpg&f=1&nofb=1&ipt=4a172924ac2ce281793ea635e8adf4787380d5d7f213a60b563dc5feabf36a7b)

## Setup

Once you have a clone of the repository, open it in your terminal. Then, run the following to
create the virtual environment:

```sh
cd back-end
python -m venv venv
```

Now, if you're on Mac or Linux, run:

```sh
source ./venv/Scripts/activate
```

If you're on Windows (i.e. Powershell), instead run:

```sh
./Scripts/Activate.ps1
```

Once the virtual environment is active, install the project dependencies:

```sh
pip install -r requirements.txt
```

Now you can run the server:

```sh
fastapi dev server.py
```

## Testing

To run the test suite, just run

```sh
pytest
```

from within the virtual environment. 

To add more tests, just create a new file that starts with `test_`. For example,
if you're testing the class you defined in `Apple.py`, then make a test file named
`test_Apple.py` in the same directory. Inside of such a file, you can create 
functions that similarly start with `test_` and use `assert` statements to test 
conditions. When you run `pytest`, it will search for such test functions and run
them. For an example, see [this file](back-end/models/util/test_BaseModelWithCSV.py).

## To Do

In the `back-end/models` part:

- implement search functionality for models; i.e., implement `get_by` and 
`get_first`.

Later:
- After the models are sorted out, we can start implementing request handlers to
interact with the "database."
