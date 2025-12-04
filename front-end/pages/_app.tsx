import "@/styles/globals.css";
import type { AppProps } from "next/app"
import { Inter } from "next/font/google"
import { UserContext } from "@/lib/hooks/useUser"
import server from "@/lib/server"
import { useEffect, useState } from "react"
import { PersonalInfo } from "@/lib/server/schema"
import NavBar from "@/lib/components/NavBar";

const inter = Inter({
	variable: "--font-inter",
	subsets: ["latin"],
});

export default function App({ Component, pageProps }: AppProps) {
	const [ user, setUser ] = useState<PersonalInfo | null | undefined>(undefined)

	useEffect(() => {
		server.user.personalInfo()
			.then(userInfo => setUser(userInfo))
	}, [])

	return (
		<div className={`${inter.className}`}>
			<UserContext.Provider value={{ user, setUser }}>
				<NavBar />
				<Component {...pageProps} />
			</UserContext.Provider>
		</div>
	);
}
