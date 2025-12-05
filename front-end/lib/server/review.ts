import { SERVER_URL } from "@/env"

/**
 * Create a new review, or overwrite an existing one. Must be logged in.
 */
async function create(bookId: string, rating: number, text: string): Promise<Error | null> {
	let res = await fetch(
		SERVER_URL 
		+ "review/"
		+ encodeURIComponent(bookId), 
		{
			method: "PUT",
			credentials: "include",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				rating,
				text,
			}),
		}
	)

	switch (res.status) {
	case 200: // OK
	case 201:
		return null
	case 500:
	case 401:
	case 409: // These responses will contain messages suitable for end-users.
		let body = await res.json()
		if (body && body.detail != undefined) {
			return new Error(body.detail)
		}
	default: // Unexpected validation error (from fastapi)
		return new Error("Unknown error occurred. Please try again.")
	}
}

/**
 * Delete an existing review. Must be logged in.
 */
async function remove(bookId: string): Promise<Error | null> {
	let res = await fetch(
		SERVER_URL
		+ "review/"
		+ encodeURIComponent(bookId), 
		{
			method: "DELETE",
			credentials: "include",
		}
	)

	switch (res.status) {
	case 200: // OK
	case 201:
		return null
	case 500:
	case 401:
	case 409: // These responses will contain messages suitable for end-users.
		let body = await res.json()
		if (body && body.detail != undefined) {
			return new Error(body.detail)
		}
	default: // Unexpected validation error (from fastapi)
		return new Error("Unknown error occurred. Please try again.")
	}
}

const review = {
	create,
	remove
}

export default review