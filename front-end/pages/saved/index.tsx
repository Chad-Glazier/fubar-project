import styles from "@/styles/Saved.module.css"
import server from "@/lib/server"
import { useState, useEffect } from "react"
import Head from "next/head"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import { SERVER_URL } from "@/env"
import ProfilePicturePicker from "@/lib/components/ProfilePicturePicker"
import { Book, PopulatedReview } from "@/lib/server/schema"
import ReviewSummary from "@/lib/components/ReviewSummary"
import BookCard from "@/lib/components/BookCard"

export default function Saved() {
	const router = useRouter()
	const { user, setUser } = useUser()
	const [ savedBooks, setSavedBooks ] = useState<Book[]>([])

	useEffect(() => {
		if (user === undefined) {
			return
		}
		
		if (user === null) {
			router.push("/login")
			return
		}

		setSavedBooks(user.savedBooks)
	}, [user, router])

	if (user === null) {
		return <></>
	}
	if (user === undefined) {
		return <>loading...</>
	}
	return <>
		<Head>
			<title>Reading List | My Saved Books</title>
			<meta name="description" content={`View your saved books.`} />
		</Head>
		<main className={`${styles.main}`}>
			<div className={styles.container}>
				{savedBooks.length === 0 ?
					<em>You have no saved books.</em>
					:
					savedBooks.map(book => 
						<BookCard 
							key={book.id}
							{...book} 
							initiallySaved={true}
							onSave={() => {
								server.user.saveBook(book.id)
							}}
							onUnsave={() => {
								server.user.unsaveBook(book.id)
							}}
						/>
					)
				}
			</div>
		</main>
	</>
}
