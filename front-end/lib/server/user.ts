import { SERVER_URL } from "@/env"
import { PersonalInfo, PersonalInfoSchema, UserStreak, UserStreakSchema } from "./schema"

/**
 * Register a new user. If something is wrong with the registration, like
 * attempting to register an existing email or display name, then a user-
 * appropriate error message will be returned. If the account was registered
 * correctly, then the user should now be logged in and this function returns
 * `null`.
 * 
 * @param displayName 
 * @param email 
 * @param password 
 * @returns an `Error` if something went wrong, otherwise returns `null`.
 */
async function register(
	displayName: string,
	email: string,
	password: string 
): Promise<Error | null> {
	let res = await fetch(
		SERVER_URL + "user", 
		{
			method: "POST",
			credentials: "include",
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
		return new Error("Unknown error occurred. Please try again.")
	}
}

/**
 * Get the personal information about whichever user is currently logged in.
 * 
 * @returns `PersonalInfo` about the current user; if no one is logged in,
 * returns `null`.
 */
async function personalInfo(): Promise<PersonalInfo | null> {
	let res = await fetch(
		SERVER_URL + "user/me", 
		{
			method: "GET",
			credentials: "include"
		}
	)

	if (!res.ok) {
		return null
	}

	let parsed = PersonalInfoSchema.safeParse(await res.json())
	if (!parsed.success) {
		return null
	}

	return parsed.data
}

/**
 * Log in to an account.
 * 
 * @returns an `Error` with a message appropriate for the end-user if something
 * went wrong, otherwise returns `null`.
 */
async function logIn(
	email: string,
	password: string 
): Promise<Error | null> {
	let res = await fetch(
		SERVER_URL + "user/session", 
		{
			method: "POST",
			credentials: "include",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({
				email: email,
				password: password
			}),
		}
	)

	switch (res.status) {
	case 200: // OK
	case 201:
		return null
	case 401: // wrong password
	case 404: // wrong email
	case 500: // server error
		let body = await res.json()
		if (body.detail != undefined) {
			return new Error(body.detail)
		}
	default: // Unexpected validation error (from fastapi)
		return new Error("Unknown error occurred. Please try again.")
	}
}

/**
 * Fetch a user's reading streak summary.
 */
async function streak(userId: string): Promise<UserStreak | null> {
	if (!userId) {
		return null
	}

	let res = await fetch(
		SERVER_URL + `user/${userId}/streak`,
		{
			method: "GET",
			credentials: "include",
		}
	)

	if (!res.ok) {
		return null
	}

	let parsed = UserStreakSchema.safeParse(await res.json())
	if (!parsed.success) {
		return null
	}

	return parsed.data
}

async function getProfile() {
	throw new Error("Not implemented")
}

const user = {
	register,
	personalInfo,
	logIn,
	streak,
	getProfile
}

export default user
