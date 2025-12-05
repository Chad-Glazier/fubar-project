
import styles from "@/styles/Review.module.css"
import { GetServerSideProps } from "next"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import BookCard from "@/lib/components/BookCard"
import Head from "next/head"
import { Book, BookDetails, PopulatedReview } from "@/lib/server/schema"
import server from "@/lib/server"
import { useEffect, useRef, useState } from "react"
import ReviewSummary from "@/lib/components/ReviewSummary"

type Props = {
	book: Book
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

	return {
		props: {
			book: bookDetails.book,
		}
	}
}

export default function ReviewPage({
	book,
}: Props) {
	const router = useRouter()
	const { user, setUser } = useUser()
	const reviewsAtATime = 10
	const [ reviewsToShow, setReviewsToShow ] = useState<number>(reviewsAtATime)
	const [rating, setRating] = useState<number>(5)
	const [text, setText] = useState<string>("")
	const loadedValues = useRef<boolean>(false)

	useEffect(() => {
		if (user === undefined) {
			return
		}

		if (user === null) {
			router.push("/login")
			return
		}

		if (loadedValues.current === false) {
			const existingReview = user.reviews.find(
				review => review.bookId === book.id
			)
			if (existingReview) {
				setText(existingReview.text)
				setRating(existingReview.rating)
			}
			loadedValues.current = true
		}
	}, [user, router])

	return <>
		<Head>
			<title>Reading List | Reviewing {book.title}</title>
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
			<div className={styles.editor}>
				<label className={styles.label}>Your Rating</label>
				<select
					className={styles.ratingInput}
					value={rating}
					onChange={(e) => setRating(parseInt(e.target.value))}
				>
					{Array.from({ length: 11 }).map((_, i) => (
						<option key={i} value={i}>{i}/10</option>
					))}
				</select>

				<label className={styles.label}>Your Review</label>
				<textarea
					className={styles.textArea}
					value={text}
					onChange={(e) => setText(e.target.value)}
					placeholder="Write your thoughts about this book..."
					rows={6}
				/>

				<button
					className={styles.postButton}
					onClick={async () => {
						if (!user) {
							router.push("/login")
							return
						}

						if (text.trim().length === 0) return

						await server.review.create(
							book.id,
							rating,
							text
						)

						// Refresh user info (updated review count, etc.)
						const updated = await server.user.personalInfo()
						setUser(updated)

						router.push(`/book/${book.id}`)
					}}
				>
					Post Review
				</button>
			</div>
		</main>
	</>
}
