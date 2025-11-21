Google Books setup

This folder contains the backend code. To enable Google Books API access locally:

1. Copy `.env.example` to `.env` inside `back-end/`:

   cp back-end/.env.example back-end/.env

2. Fill in your API key in `back-end/.env`:

   GOOGLE_BOOKS_API_KEY=AIza....

3. Make sure `back-end/.env` is in `.gitignore` (it already is) so you don't commit secrets.

Code uses `os.getenv('GOOGLE_BOOKS_API_KEY')` to read the key.
