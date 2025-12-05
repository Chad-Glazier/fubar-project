import { useEffect } from "react"
import ReactDOM from "react-dom"
import styles from "./ProfilePicturePicker.module.css"
import { SERVER_URL } from "@/env"

type Props = {
	/** Paths relative to the server domain. E.g., "public/img.png" */
	relativeImagePaths: string[]
	onSelect?: (relativeImagePath: string) => void
	onClose?: () => void
}

export default function ProfilePicturePicker({ 
	relativeImagePaths, onSelect, onClose 
}: Props) {
	useEffect(() => {
		function handleKey(e: KeyboardEvent) {
			if (e.key === "Escape") {
				onClose && onClose()
			}
		}
		document.addEventListener("keydown", handleKey)
		return () => document.removeEventListener("keydown", handleKey)
	}, [onClose])

	const modalRoot = document.getElementById("modal-root")
	if (!modalRoot) {
		console.error("The profile picture selector needs an element with `#modal-root`.")
		return null
	}

	const modal = (
		<div className={styles.backdrop} onClick={onClose}>
			<div
				className={styles.modal}
				onClick={(e) => e.stopPropagation()} 
			>
				<h2 className={styles.title}>Choose a New Profile Picture</h2>
				<div className={styles.grid}>
					{relativeImagePaths.map((relativeImagePath, idx) => (
						<img
							key={relativeImagePath}
							src={SERVER_URL + relativeImagePath}
							className={styles.image}
							onClick={() => onSelect && onSelect(relativeImagePath)}
							alt={`Profile picture option ${idx + 1}`}
						/>
					))}
				</div>
			</div>
		</div>
	)

	return ReactDOM.createPortal(modal, modalRoot)
}
