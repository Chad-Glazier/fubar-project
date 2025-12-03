import styles from "@/styles/Profile.module.css"
import server from "@/lib/server"
import { useState, useEffect } from "react"
import Head from "next/head"
import useUser from "@/lib/hooks/useUser"
import Link from "next/link"
import { UserStreak } from "@/lib/server/schema"

export default function Profile() {
	const { user } = useUser()
	const [ streak, setStreak ] = useState<UserStreak | null>(null)
	const [ loadingStreak, setLoadingStreak ] = useState(false)

	useEffect(() => {
		let ignore = false
		if (!user?.id) {
			setStreak(null)
			return
		}

		setLoadingStreak(true)
		server.user.streak(user.id)
			.then((stats) => {
				if (!ignore) {
					setStreak(stats)
				}
			})
			.finally(() => {
				if (!ignore) {
					setLoadingStreak(false)
				}
			})

		return () => {
			ignore = true
		}
	}, [user?.id])

	return (
		<>
			<Head>
				<title>Profile | FUBAR</title>
			</Head>
			<main className={styles.page}>
				<div className={styles.container}>
					{user ? (
						<>
							<section className={styles.header}>
								<div>
									<p className={styles.greeting}>Welcome back</p>
									<h1>{user.displayName}</h1>
									<p className={styles.email}>{user.email}</p>
								</div>
							</section>

							<section className={styles.cards}>
								<div className={styles.card}>
									<h2>Reading Streak</h2>
									{loadingStreak && <p className={styles.muted}>Checking your streak…</p>}
									{!loadingStreak && streak && (
										<div className={styles.streakGrid}>
											<div>
												<p className={styles.metricLabel}>Current streak</p>
												<p className={styles.metricValue}>{streak.currentStreak} days</p>
											</div>
											<div>
												<p className={styles.metricLabel}>Longest streak</p>
												<p className={styles.metricValue}>{streak.longestStreak} days</p>
											</div>
											<div className={styles.badge}>
												<span>Badge</span>
												<strong>{streak.badge}</strong>
											</div>
											<div>
												<p className={styles.metricLabel}>Last activity</p>
												<p className={styles.metricValue}>
													{streak.lastActivityDate ?? "—"}
												</p>
											</div>
										</div>
									)}
									{!loadingStreak && !streak && (
										<p className={styles.muted}>
											Start rating or saving books to build your streak.
										</p>
									)}
								</div>

								<div className={styles.card}>
									<h2>Saved Books</h2>
									{user.savedBooks.length === 0 ? (
										<p className={styles.muted}>No saved books yet.</p>
									) : (
										<ul className={styles.list}>
											{user.savedBooks.map((book) => (
												<li key={book.id}>
													<strong>{book.title}</strong>
													<span>{book.authors.join(", ")}</span>
												</li>
											))}
										</ul>
									)}
								</div>
							</section>
						</>
					) : (
						<section className={styles.card}>
							<h2>Sign in required</h2>
							<p className={styles.muted}>
								Log in to manage your saved books and see your reading streak.
							</p>
							<Link href="/login" className={styles.button}>
								Go to login
							</Link>
						</section>
					)}
				</div>
			</main>
		</>
	)
}
