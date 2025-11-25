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

## Importing the Dataset

To import the dataset to the application database, follow these steps:
1) Download the dataset from [here](https://www.kaggle.com/datasets/ruchi798/bookcrossing-dataset?resource=download).
2) Decompress/extract the files.
3) Finally, ensure that the virtual environment is active and that your current working directory is `back-end`, then run the `import_data.py` script.

## Testing

To run the test suite, just run

```sh
pytest
```

from within the virtual environment. Add the `--cov` flag for a coverage report.

To add more unit tests, just create a new file that starts with `test_`. For 
example, if you're testing the class you defined in `apple.py`, then make a 
test directory (i.e., a subpackage) named `tests`, then make a file 
`tests/test_apple.py`. Inside of such a file, you can create functions that 
start with `test_` and use `assert` statements to test conditions. When you run 
`pytest`, it will search for such test functions and run them. For an example, 
see [this file](back-end/db/tests/test_persisted_model.py).

## Deploying with Docker

To run the backend in a container:

```sh
docker build -t fubar-api .
docker run -p 8000:8000 --env-file back-end/.env fubar-api
```

This builds the backend image and exposes the FastAPI app on port 8000. Provide a `.env` file (see `back-end/.env.example`) if you need API keys or other settings.
