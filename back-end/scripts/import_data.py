import os
from pathlib import Path

from db.models.Book import Book
from db.models.UserReview import UserReview

print(f"Currently in {os.getcwd()}\n")

print("Enter the name of the directory that contains the original, \n" + \
	  "uncompressed Book Crossing data (relative to the working\ndirectory):")
relative_path = input("-> ")

raw_data_dir = Path(os.getcwd(), relative_path)

raw_user_review_file = Path(raw_data_dir, "./BX-Book-Ratings.csv")
raw_book_file = Path(raw_data_dir, "./BX_Books.csv")

if raw_user_review_file.exists() and raw_book_file.exists():
	print("\nRaw data files found.\n")
	
else:
	print(f"\nRaw data files could not be found at {raw_data_dir}.\n")
	exit(1)


r = raw_book_file.open("r")
total_records = -1
while r.readline() != "":
	total_records += 1
r.close()

print(f"Importing books...", end = "")

recorded_books = 0
r = raw_book_file.open("r")
w = Book._append_csv_file() # pyright: ignore[reportPrivateUsage]
line = r.readline() # skip the first line, the headers
line = r.readline()
while line != "":
	values = line[1:-2].split("\";\"")

	new_book = Book(
		id = values[0],
		title = values[1],
		authors = values[2].split(",")
	)
	w.write(new_book._to_csv_row() + "\n") # pyright: ignore[reportPrivateUsage]

	recorded_books += 1

	print(f"\rImporting books... {round(recorded_books / total_records * 100, 1)}%", end = "")

	line = r.readline()

r.close()
w.close()

print()

r = raw_user_review_file.open("r")
total_records = -1
while r.readline() != "":
	total_records += 1
r.close()

print(f"Importing user reviews...", end = "")

recorded_reviews = 0
r = raw_user_review_file.open("r")
w = UserReview._append_csv_file() # pyright: ignore[reportPrivateUsage]
line = r.readline() # skip the first line, the headers
line = r.readline()
while line != "":
	values = line[1:-2].split("\";\"")

	new_user_review = UserReview(
		id = values[0] + values[1],
		user_id = values[0],
		book_id = values[1],
		rating = int(values[2])
	)
	w.write(new_user_review._to_csv_row() + "\n") # pyright: ignore[reportPrivateUsage]

	recorded_reviews += 1

	print(f"\rImporting user reviews... {round(recorded_reviews / total_records * 100, 1)}%", end = "")

	line = r.readline()

r.close()
w.close()

print("\n\nData imported.")
