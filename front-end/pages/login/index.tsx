import { Inter } from "next/font/google"
import styles from "@/styles/Login.module.css"
import server from "@/lib/server"
import { useState } from "react";

const inter = Inter({
	variable: "--font-inter",
	subsets: ["latin"],
});

export default function Login() {
	const [ errorMessage, setErrorMessage ] = useState<string>("")

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault()

		const formData = new FormData(e.currentTarget)

		const password = formData.get("password")
		const confirmPassword = formData.get("confirmPassword")
		if (password != confirmPassword) {
			setErrorMessage("Please ensure that the passwords match.")
			return
		}

		const err = await server.user.register(
			formData.get("email")!.toString(),
			formData.get("display_name")!.toString(),
			password!.toString()
		)

		if (err == null) {
			setErrorMessage("")
			return
		}

		setErrorMessage(err.message)
	}

	return (
		<>
			<div
				className={`${styles.page} ${inter.variable}`}
			>
				<main className={styles.main}>
					<form onClick={handleSubmit}>
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

					<p hidden={errorMessage != ""}>{errorMessage}</p>

					<button type="submit">Create Account</button>
					</form>
				</main>
			</div>
		</>
	);
}
