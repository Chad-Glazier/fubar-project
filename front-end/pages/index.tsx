import BookCard from "@/lib/components/BookCard"
import useUser from "@/lib/hooks/useUser"
import server from "@/lib/server"
import { Book } from "@/lib/server/schema"
import { getStoredRecommendations } from "@/lib/util"
import styles from "@/styles/Home.module.css";
import Head from "next/head"
import router from "next/router"
import { useEffect, useState } from "react"

const RECOMMENDATIONS_AT_A_TIME = 8

export default function Home() {
	const { user } = useUser()
	const [ message, setMessage ] = useState("Loading...")
	const [ recommendations, setRecommendations ] = useState<Book[]>([]) 
	const [ recommendationsToShow, setRecommendationsToShow ] = useState<number>(RECOMMENDATIONS_AT_A_TIME)

	useEffect(() => {
		if (user === undefined) {
			return
		}
		
		if (user === null) {
			router.push("/login")
			return
		}

		if (user.reviews.length === 0) {
			setMessage("You need to create some reviews before we can find recommendations for you.")
		}

		const storedRecommendations = getStoredRecommendations(user.id)

		setRecommendations(storedRecommendations)
		
		if (storedRecommendations.length > 0) {
			setMessage("")
		}
	}, [user, setRecommendations])

	if (message !== "") return <p className={styles.message}><em>{message}</em></p>
	else return <>
		<Head>
			<title>Reading List | Home</title>
			<meta name="description" content="Find book recommendations, read reviews, and create your own." />
		</Head>
		<main className={`${styles.page} ${styles.main}`}>
			<h1 className={styles.header}>Your Recommended Books</h1>
			<p className={styles.subtitle}> 
				<em>Recommendations refresh daily. Check back again tomorrow for more.</em>
			</p>
			<div className={styles.recommendationsContainer}>
			{
				recommendations.slice(0, recommendationsToShow).map(book => 
					<BookCard 
						key={book.id}
						{...book} 
						initiallySaved={
							user?.savedBooks.some(savedBook => savedBook.id === book.id) ?? false
						}
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
			<button 
				className={styles.refreshButton} 
				onClick={() => 
					setRecommendationsToShow(prev => 
						Math.min(prev + RECOMMENDATIONS_AT_A_TIME, recommendations.length)
					)}
			>
				See More
			</button>
		</main>
	</>
}
