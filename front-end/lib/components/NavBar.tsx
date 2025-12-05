import { useRouter } from "next/router"
import { useState } from "react"
import useUser from "@/lib/hooks/useUser"
import styles from "./NavBar.module.css"
import Link from "next/link"
import { FaCompass, FaUser, FaBookmark, FaSearch } from "react-icons/fa"

export default function NavBar() {
	const router = useRouter()
	const { user } = useUser()
	const [ query, setQuery ] = useState("")

	function handleSearch(e: React.FormEvent) {
		e.preventDefault()
		if (!query.trim()) return
		router.push(`/search/${encodeURIComponent(query.trim())}`)
	}

	return (
		<nav className={styles.nav}>
			<div className={styles.left}>
				<Link href="/" className={styles.iconButton} title="Home">
					<FaCompass />
				</Link>

				{user && (
					<Link href="/saved" className={styles.iconButton} title="Saved Posts">
						<FaBookmark />
					</Link>
				)}
			</div>
			
			<form className={styles.searchForm} onSubmit={handleSearch}>
				<input
					className={styles.searchInput}
					type="text"
					placeholder="Search books..."
					value={query}
					onChange={(e) => setQuery(e.target.value)}
				/>	
			</form>

			<div className={styles.right}>
				{user ? (
					<Link href="/profile" className={styles.iconButton} title="My Profile">
						<FaUser />
					</Link>
				) : (
					<Link href="/login" className={styles.loginButton}>
						Log In
					</Link>
				)}
			</div>
		</nav>
	)
}
