import styles from "@/styles/Register.module.css"
import server from "@/lib/server"
import { useState } from "react"
import Head from "next/head"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import Link from "next/link"

export default function Register() {
	const [ errorMessage, setErrorMessage ] = useState<string>("")
	const router = useRouter()
	const { user, setUser } = useUser()
	const [ loading, setLoading ] = useState<boolean>(false)

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault()

		const formData = new FormData(e.currentTarget)

		const password = formData.get("password")!.toString()
		const confirmPassword = formData.get("confirm_password")!.toString()
		if (password != confirmPassword) {
			setErrorMessage("Please ensure that the passwords match.")
			return
		}

		setLoading(true)
		const err = await server.user.register(
			formData.get("display_name")!.toString(),
			formData.get("email")!.toString(),
			password
		)

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
			router.push("/login")
		} else {
			router.push("/")
		}
	}

	return (
		<>
			<Head>
				<title>Reading List | Log In</title>
				<meta name="description" content="Log in to your Reading List account." />
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
								<label htmlFor="display_name">Display Name</label><br />
								<input type="text" id="display_name" name="display_name" required />
							</div>

							<div>
								<label htmlFor="password">Password</label><br />
								<input type="password" id="password" name="password" required minLength={8} />
							</div>

							<div>
								<label htmlFor="confirm_password">Confirm Password</label><br />
								<input type="password" id="confirm_password" name="confirm_password" required minLength={8} />
							</div>

							<p hidden={errorMessage === ""}>{errorMessage}</p>

							<button type="submit">Create Account</button>
						</fieldset>
					</form>
					<p>
						Already have an account? 
						Log in <Link href="/login" className={styles.link}>here</Link>.
					</p>
				</main>
			</div>
		</>
	);
}

