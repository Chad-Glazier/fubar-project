import { createContext, useContext } from "react"
import { PersonalInfo } from "../server/schema"

type UserContextType = {
	user: PersonalInfo | null
	setUser: React.Dispatch<React.SetStateAction<PersonalInfo | null>>
}

export const UserContext = createContext<UserContextType | null>(null)

export default function useUser(): UserContextType {
	const context = useContext(UserContext)
	if (!context) {
		let msg = "You can only use `useUser` inside of a `UserContext.Provider` component."
		console.error(msg)
		throw new Error(msg)
	}
	return context
}