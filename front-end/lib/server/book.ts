import { SERVER_URL } from "@/env"
import { BookDetails, Book, BookSchema, BookDetailsSchema } from "./schema"
import { logWrongServerResponseBody } from "./util"

/**
 * Get some basic information about a book, like its title.
 * 
 * @returns a `Book` object if one could be found, otherwise returning
 * `null`.
 */
async function basicDetails(bookId: string): Promise<Book | null> {
	let res = await fetch(
		SERVER_URL + "books/" + encodeURIComponent(bookId) + "?basic=true",
		{
			method: "GET",
		}
	)

	if (!res.ok) {
		return null
	}

	let responseBody = await res.json()
	let parsed = BookSchema.safeParse(responseBody)
	if (!parsed.success) {
		logWrongServerResponseBody(responseBody, BookSchema)
		return null
	}

	return parsed.data
}

/**
 * Get the details about a book including a list of its reviews.
 * 
 * @param bookId the ID of the book to retrieve.
 * 
 * @returns a `BookDetails` object, which includes some basic information
 * about the book, such as its title, as well as a list of its reviews. If
 * no book with the matching ID was found, then this function returns `null`.
 */
async function details(bookId: string): Promise<BookDetails | null> {
	let res = await fetch(
		SERVER_URL + "books/" + encodeURIComponent(bookId),
		{
			method: "GET",
		}
	)

	if (!res.ok) {
		return null
	}

	let responseBody = await res.json()
	let parsed = BookDetailsSchema.safeParse(responseBody)
	if (!parsed.success) {
		logWrongServerResponseBody(responseBody, BookDetailsSchema)
		return null
	}

	return parsed.data
}

const book = {
	details,
	basicDetails
}

export default book