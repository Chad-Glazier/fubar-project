import { useState } from "react";
import { useRouter } from "next/router";
import styles from "./BookCard.module.css";
import { FaBookmark, FaRegBookmark, FaPen } from "react-icons/fa";
import { Book } from "../server/schema"
import { SERVER_URL } from "@/env"
import useUser from "@/lib/hooks/useUser";

type Props = Book & {
	initiallySaved: boolean
	onSave?: () => void
	onUnsave?: () => void
	initiallyExpanded?: boolean
};

export default function BookCard({
	id,
	title,
	authors,
	description,
	imageLinks,
	averageRating,
	initiallySaved,
	onSave,
	onUnsave,
	initiallyExpanded
}: Props) {
	const router = useRouter()
	const [ expanded, setExpanded ] = useState(!!initiallyExpanded)
	const [ saved, setSaved ] = useState(initiallySaved)
	const { user } = useUser()

	const toggleExpand = () => {
		setExpanded((expanded) => !expanded)
	}

	const shortDescription =
		description && description.length > 100
			? description.substring(0, 95) + "[...]"
			: description

	return (
		<div
			className={`${styles.card} ${expanded ? styles.expanded : ""}`}
			onClick={toggleExpand}
		>
			<img
				src={
					imageLinks && imageLinks["thumbnail"] ?
						imageLinks["thumbnail"]
						:
						SERVER_URL + "public/default-book.png"}
				alt={title}
				className={styles.thumb}
			/>

			<div className={styles.content}>
				<div className={styles.header}>
					<h2
						className={`${styles.title} ${
							expanded ? styles.titleLink : ""
						}`}
						onClick={(e) => {
							if (expanded) {
								e.stopPropagation()
								router.push(`/book/${encodeURIComponent(id)}`)
							}
						}}
					>
						{title}
					</h2>

					{averageRating !== undefined && averageRating !== null && (
						<span className={styles.rating}>
							{averageRating.toFixed(1)}/10
						</span>
					)}
				</div>

				<div className={styles.authors}>
					{authors.join(", ")}
				</div>

				<p className={styles.description}>
					{expanded ? description : shortDescription}
				</p>

				{expanded && (
					<div
						className={styles.actions}
						onClick={(e) => e.stopPropagation()}
					>
						<button
							className={styles.actionBtn}
							onClick={() => {
								if (saved) {
									setSaved(false)
									onUnsave && onUnsave()
								} else {
									setSaved(true)
									onSave && onSave()
								}
							}}
						>
							{saved ? <FaBookmark /> : <FaRegBookmark />}
							<span>{saved ? "Saved" : "Save"}</span>
                        </button>
						<button
							className={styles.actionBtn}
							onClick={() => {
								if (user) {
									router.push(`/review/${id}`)
								} else {
									router.push("/login")
								}
							}}
						>
							<FaPen />
							<span>Write Review</span>
						</button>
					</div>
				)}
			</div>
		</div>
	);
}
