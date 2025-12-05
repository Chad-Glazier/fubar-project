import { SERVER_URL } from "@/env"
import { BookDetails, Book, BookSchema, BookDetailsSchema } from "./schema"
import { logWrongServerResponseBody } from "./util"
import z from "zod"

const SEARCH_RESULTS_PER_PAGE = 12

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

/**
 * Returns the search results for a given book title.
 */
async function search(
	bookTitle: string, 
	pageNumber: number
): Promise<{
	prev: string | null
	books: Book[]
	next: string | null
}> {
	let res = await fetch(
		SERVER_URL 
		+ "search/book/" 
		+ encodeURIComponent(bookTitle) 
		+ `?limit=${SEARCH_RESULTS_PER_PAGE + 1}&skip=${(pageNumber - 1) * SEARCH_RESULTS_PER_PAGE}`
	)

	if (!res.ok) {
		console.error(
			`Search results unexpectedly failed. Response body:\n${JSON.stringify(await res.json())}`)
		return { books: [], prev: null, next: null }
	}

	const responseBody = await res.json()
	let parsed = z.array(BookSchema).safeParse(responseBody)
	
	if (!parsed.success) {
		logWrongServerResponseBody(
			responseBody,
			z.array(BookSchema)
		)
		return { books: [], prev: null, next: null }
	}

	let prev: string | null = null
	if (pageNumber > 1) {
		prev = `/search/${encodeURIComponent(bookTitle)}?page=${pageNumber - 1}`
	}

	let next: string | null = null
	if (parsed.data.length > SEARCH_RESULTS_PER_PAGE) {
		next = `/search/${encodeURIComponent(bookTitle)}?page=${pageNumber + 1}`
	}

	return {
		prev,
		books: parsed.data.slice(0, SEARCH_RESULTS_PER_PAGE),
		next
	}
}

const book = {
	details,
	basicDetails,
	search
}

export default book
