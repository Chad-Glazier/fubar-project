import { SERVER_URL } from "@/env"
import styles from "./ReviewSummary.module.css"
import { PopulatedReview } from "@/lib/server/schema"
import { useState } from "react"
import { FaExclamationTriangle, FaTrash } from "react-icons/fa"
import server from "../server"
import { useRouter } from "next/router"

type Props = {
	reviews: PopulatedReview[]
	showUser?: boolean
	showBook?: boolean
	deleteable?: boolean
	reportable?: boolean
	onDelete?: (review: PopulatedReview) => void
};

export default function ReviewSummary({
	reviews,
	showUser = false,
	showBook = false,
	deleteable = false,
	reportable = false,
	onDelete
}: Props) {
	const [ expanded, setExpanded ] = useState<number>(-1)
	const [ deleted, setDeleted ] = useState<boolean>(false)
	const router = useRouter()
	
	if (reviews.length === 0) {
		return <div className={styles.empty}>No reviews yet.</div>;
	}

	if (deleted) {
		return <></>
	}

	return (
		<div className={styles.container}>
			{reviews.map((review, idx) => (
				<div 
					key={review.id} 
					className={styles.reviewCard} 
					onClick={() => {
						if (expanded === idx) {
							setExpanded(-1)
						} else {
							setExpanded(idx)
						}
					}}
				>
					{showUser && (
						<div className={styles.userSection}>
							<img
								src={SERVER_URL + review.user.profilePicturePath}
								alt={review.user.displayName}
								className={styles.avatar}
								onClick={() => {
									router.push("/profile/" + review.user.id)
								}}
							/>
							<span className={styles.username}>
								{review.user.displayName}
							</span>
						</div>
					)}

					{showBook && (
						<div className={styles.bookSection}>
							<img
								src={review.book.imageLinks?.thumbnail ??
									SERVER_URL + "public/default-book.png"}
								alt={review.book.title}
								className={styles.bookThumb}
							/>
							<div>
								<div className={styles.bookTitle}>
									{review.book.title}
								</div>
								{review.book.authors.length > 0 && (
									<div className={styles.bookAuthors}>
										{review.book.authors.join(", ")}
									</div>
								)}
							</div>
						</div>
					)}

					{deleteable && (expanded === idx) && (
						<button
							className={styles.deleteButton}
							onClick={(e) => {
								e.stopPropagation();

								server.review.remove(review.bookId)
									.then(_ => {
										onDelete && onDelete(review)
									})
							}}
						>
							<FaTrash />
						</button>
					)}

					{reportable && (expanded === idx) && (
						<button
							className={styles.deleteButton}
							onClick={(e) => {
								e.stopPropagation();

								server.review.remove(review.bookId)
									.then(_ => {
										onDelete && onDelete(review)
									})
							}}
						>
							<FaExclamationTriangle />
						</button>
					)}

					<div className={styles.body}>
						<div className={styles.rating}>
							{review.rating}/10
						</div>
						{review.text.length > 0 ? 
							<p className={styles.text}>{
								review.text.length > 60 && expanded !== idx ?
									`"${review.text.substring(0, 54)} [...]"`
									:
									"\"" + review.text + "\""
							}</p>
							:
							<></>
						}
					</div>
				</div>
			))}
		</div>
	);
}
