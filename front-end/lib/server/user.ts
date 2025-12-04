import { SERVER_URL } from "@/env"
import { AccountInfo, AccountInfoSchema, PersonalInfo, PersonalInfoSchema, ProfilePicturesSchema } from "./schema"
import z from "zod"
import { logWrongServerResponseBody } from "./util"

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
		if (body && body.detail != undefined) {
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
		if (body && body.detail != undefined) {
			return new Error(body.detail)
		}
	default: // Unexpected validation error (from fastapi)
		return new Error("Unknown error occurred. Please try again.")
	}
}

/**
 * Get the public info about a specific user.
 */
async function accountInfo(userId: string): Promise<AccountInfo | null> {
	let res = await fetch(
		SERVER_URL + "user/" + encodeURIComponent(userId), 
		{
			method: "GET"
		}
	)

	if (!res.ok) {
		return null
	}
	
	let responseBody = await res.json()
	let accountInfo = AccountInfoSchema.safeParse(responseBody)
	if (!accountInfo.success) {
		logWrongServerResponseBody(responseBody, AccountInfoSchema)
		return null
	}

	return accountInfo.data
}

/**
 * Update the details for the currently logged-in user.
 */
async function updateAccount(updates: Partial<{
	profilePicturePath: string
	email: string
	password: string
	displayName: string
}>): Promise<Error | null> {
	let res = await fetch(
		SERVER_URL + "user",
		{
			method: "PATCH",
			credentials: "include",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify(updates),
		}
	)

	switch (res.status) {
	case 200:
	case 201:
		return null
	case 409:
	case 401:
		let body = await res.json()
		if (body && body.detail != undefined) {
			return new Error(body.detail)
		}
	default:
		return new Error("Unknown error occurred. Please try again.")
	}
}

/**
 * Get the allowed profile pictures as an array of strings that represent
 * paths relative to `SERVER_URL` that will serve the images.
 */
async function availableProfilePictures(): Promise<string[]> {
	let res = await fetch(
		SERVER_URL + "profile_pictures/all"
	)

	if (!res.ok) {
		return []
	}

	let responseBody = await res.json()
	let profilePictures = ProfilePicturesSchema.safeParse(responseBody)
	if (!profilePictures.success) {
		logWrongServerResponseBody(responseBody, ProfilePicturesSchema)
		return []
	}
	return profilePictures.data.map(profilePicture => profilePicture.relativeUrl)
}

const user = {
	register,
	personalInfo,
	logIn,
	accountInfo,
	updateAccount,
	availableProfilePictures
}

export default user
