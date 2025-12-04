import { SERVER_URL } from "@/env"
import styles from "./ReviewSummary.module.css"
import { PopulatedReview } from "@/lib/server/schema"
import { useState } from "react"

type Props = {
	reviews: PopulatedReview[];
	showUser?: boolean;
	showBook?: boolean;
};

export default function ReviewSummary({
	reviews,
	showUser = false,
	showBook = false,
}: Props) {
	const [ expanded, setExpanded ] = useState<number>(-1)
	
	if (reviews.length === 0) {
		return <div className={styles.empty}>No reviews yet.</div>;
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

					<div className={styles.body}>
						<div className={styles.rating}>
							{review.rating}/10
						</div>
						<p className={styles.text}>{
							review.text.length > 60 && expanded !== idx ?
								`"${review.text.substring(0, 54)} [...]"`
								:
								"\"" + review.text + "\""
						}</p>
					</div>
				</div>
			))}
		</div>
	);
}
