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

from within the virtual environment. 

To add more unit tests, just create a new file that starts with `test_`. For 
example, if you're testing the class you defined in `apple.py`, then make a 
test directory (i.e., a subpackage) named `tests`, then make a file 
`tests/test_apple.py`. Inside of such a file, you can create functions that 
start with `test_` and use `assert` statements to test conditions. When you run 
`pytest`, it will search for such test functions and run them. For an example, 
see [this file](back-end/db/tests/test_persisted_model.py).

## API Overview

Once the server is running on `http://localhost:8000`, you can call these endpoints. Each describes what it does, how to use it, and what to expect back.

### Book Details
- **Purpose:** Fetch one book plus its reviews.
- **Request:** `GET /books/{book_id}` (no body)
- **Response:**
  ```json
  {
    "book": { "id": "bd1", "title": "Details Book", "authors": ["Auth"] },
    "average_rating": 9.0,
    "review_count": 2,
    "reviews": [
      { "id": "r1", "rating": 8 },
      { "id": "r2", "rating": 10 }
    ]
  }
  ```
- **Errors:** `404 Book not found` if the ID isn’t stored.

If a requested book ID hasn’t been persisted yet, the server automatically calls the Google Books API to retrieve the metadata/cover, stores it locally, and then returns it to the caller.

### Book Recommendations
- **Purpose:** Suggest books for a specific user.
- **Request:** `GET /recommendations/{user_id}?n=10&k=5`
  - `n` (optional) → how many suggestions (default 10)
  - `k` (optional) → how many neighbors to consider (default 5)
- **Response:**
  ```json
  [
    { "book": { "id": "b1", "title": "Brave New" }, "score": 0.92 },
    { "book": { "id": "b2", "title": "Dune" }, "score": 0.81 }
  ]
  ```
  If the book is missing locally, you may see `{ "book_id": "..." }` instead of the full object.
- **Errors:** `404 No recommendations available` when we can’t compute anything for that user.

### Search
- **Purpose:** Find books whose title or authors match a keyword.
- **Request:** `GET /search?query=term&limit=20`
- **Response:**
  ```json
  [
    { "id": "b1", "title": "Learning FastAPI", "authors": ["Ada"] },
    { "id": "b2", "title": "Fast Recipes", "authors": ["Turing"] }
  ]
  ```
- **Errors:** `404 No books found` when nothing matches or the catalog is empty.

### Saved Books
- **Purpose:** Let users bookmark books.
- **Requests:**
  1. `POST /users/{user_id}/saved/{book_id}` → saves a book. Response `{ "message": "Book saved" }`. Errors: `404 User not found`, `404 Book not found`.
  2. `DELETE /users/{user_id}/saved/{book_id}` → removes a saved book. Response `{ "message": "Book removed" }`. Error: `404 User not found` if the user ID is unknown.
  3. `GET /users/{user_id}/saved` → lists saved books. Response:
     ```json
     [
       { "id": "sb1", "user_id": "u1", "book_id": "b2" }
     ]
     ```
     Error: `404 User not found` if that user doesn’t exist.

Use these descriptions as your quick reference for the API—no background in the codebase required.

## Deploying with Docker

To run the backend in a container:

```sh
docker build -t fubar-api .
docker run -p 8000:8000 --env-file back-end/.env fubar-api
```

This builds the backend image and exposes the FastAPI app on port 8000. Provide a `.env` file (see `back-end/.env.example`) if you need API keys or other settings.
