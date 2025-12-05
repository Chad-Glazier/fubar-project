import { useRouter } from "next/router"
import styles from "./PaginationControls.module.css"
import { FaArrowLeftLong, FaArrowRightLong } from "react-icons/fa6"

type Props = {
    page: number
    next: string | null
    prev: string | null
}

export default function PaginationControls({ page, next, prev }: Props) {
    const router = useRouter()

    return <>
        <div className={styles.pagination}>
            <button
                className={styles.navButton}
                disabled={!prev}
                onClick={() => prev && router.push(prev)}
            >
                <FaArrowLeftLong />
            </button>

            <span className={styles.pageNumber}>Page {page}</span>

            <button
                className={styles.navButton}
                disabled={!next}
                onClick={() => next && router.push(next)}
            >
                <FaArrowRightLong />
            </button>
        </div>
	</>
}
