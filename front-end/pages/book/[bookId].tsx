
import styles from "@/styles/Book.module.css"
import { GetServerSideProps } from "next"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import BookCard from "@/lib/components/BookCard"
import Head from "next/head"
import { Book, BookDetails, PopulatedReview } from "@/lib/server/schema"
import server from "@/lib/server"
import PaginationControls from "@/lib/components/PaginationControls"
import { useState } from "react"
import ReviewSummary from "@/lib/components/ReviewSummary"

type Props = {
	book: Book
	reviews: PopulatedReview[]
}

export const getServerSideProps: GetServerSideProps<Props> = async (context) => {
	const bookId = context.params!.bookId as string | undefined
	if (bookId === "" || bookId === undefined) {
		return { notFound: true }
	}

	const bookDetails = await server.book.details(bookId)
	if (bookDetails === null) {
		return { notFound: true }
	}

	let reviews: PopulatedReview[] = []
	for (let review of bookDetails.reviews) {
		let userDetails = await server.user.basicAccountInfo(review.userId)
		if (userDetails === null) {
			userDetails = {
				id: review.userId,
				displayName: `Anonymous User (#${review.userId})`,
				profilePicturePath: "public/profile_pictures/default.jpg"
			}
		}
		reviews.push({
			...review,
			book: bookDetails.book,
			user: userDetails
		})
	}

	return {
		props: {
			book: bookDetails.book,
			reviews: reviews
		}
	}
}

export default function SearchResults({
	book,
	reviews,
}: Props) {
	const router = useRouter()
	const { user, setUser } = useUser()
	const reviewsAtATime = 10
	const [ reviewsToShow, setReviewsToShow ] = useState<number>(reviewsAtATime)  

	return <>
		<Head>
			<title>Reading List | {book.title}</title>
			<meta name="description" content={`View ${book.title} by ${book.authors.join(", ")}.`} />
		</Head>
		<main className={`${styles.main}`}>
			<BookCard
				{...book}
				initiallyExpanded={true}
				initiallySaved={
					user ?
						user.savedBooks.some(
							savedBook => savedBook.id === book.id
						)
						:
						false
				}
				onSave={() => {
					if (user) {
						server.user.saveBook(book.id)
					} else {
						router.push("/login")
					}
				}}
				onUnsave={() => {
					if (user) {
						server.user.unsaveBook(book.id)
					} else {
						router.push("/login")
					}
				}}
			/>
			<ReviewSummary
				reviews={reviews}
				showUser={true}
				showBook={false}
			/>
			{reviewsToShow < reviews.length ? 
				<button 
					className={styles.showMore}
					onClick={() => setReviewsToShow(prev => prev + reviewsAtATime)}
				>Show More Reviews</button>
				:
				<></>
			}
		</main>
	</>
}
