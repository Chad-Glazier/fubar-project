const DEFAULT_SERVER_URL = process.env.NEXT_PUBLIC_SERVER_URL ?? "http://localhost:8000/"

export const SERVER_URL = DEFAULT_SERVER_URL.endsWith("/")
	? DEFAULT_SERVER_URL
	: `${DEFAULT_SERVER_URL}/`
