import styles from "@/styles/Register.module.css"
import server from "@/lib/server"
import { useState } from "react"
import Head from "next/head"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"

export default function Register() {
	const [ errorMessage, setErrorMessage ] = useState<string>("")
	const router = useRouter()
	const { user, setUser } = useUser()
	const [ loading, setLoading ] = useState<boolean>(false)

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault()

		const formData = new FormData(e.currentTarget)

		const email = formData.get("email")!.toString()
		const password = formData.get("password")!.toString()

		setLoading(true)
		const err = await server.user.logIn(email, password)

		if (err != null) {
			setErrorMessage(err.message)
			setLoading(false)
			return
		}

		setErrorMessage("")
		const userDetails = await server.user.personalInfo()
		setUser(userDetails)
		setLoading(false)
		if (user === null) {
			setErrorMessage("An unexpected error occured. Please try again.")
		} else {
			router.push("/")
		}
	}

	return (
		<>
			<Head>
				<title>Reading List | Register</title>
				<meta name="description" content="Register an account for Reading List." />
			</Head>
			<div
				className={`${styles.page}`}
			>
				<main className={styles.main}>
					<form onSubmit={handleSubmit}>
						<fieldset disabled={loading} style={{ border: "none", padding: 0 }}>
							<div>
								<label htmlFor="email">Email</label><br />
								<input type="email" id="email" name="email" required />
							</div>

							<div>
								<label htmlFor="password">Password</label><br />
								<input type="password" id="password" name="password" required minLength={8} />
							</div>

							<p hidden={errorMessage === ""}>{errorMessage}</p>

							<button type="submit">Log In</button>
						</fieldset>
					</form>
				</main>
			</div>
		</>
	);
}
