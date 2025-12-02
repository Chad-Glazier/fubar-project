import { SERVER_URL } from "@/env"

async function register(
	displayName: string,
	email: string,
	password: string 
): Promise<Error | null> {
	let res = await fetch(
		SERVER_URL + "user", 
		{
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				display_name: displayName,
				email: email,
				password: password
			}),
		}
	)

	switch (res.status) {
	case 200: // OK
	case 201:
		return null
	case 500: // Errors expected from the server.
	case 409: // These responses will contain messages suitable for end-users.
		let body = await res.json()
		if (body.detail != undefined) {
			return new Error(body.detail)
		}
	default: // Unexpected validation error (from fastapi)
		return new Error("Unknown error occurred. Try again.")
	}
}

const user = {
	register
}

export default user
