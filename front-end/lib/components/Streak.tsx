import { FaFire } from "react-icons/fa"
import styles from "./Streak.module.css"

type Props = {
	streakCount: number
	badge: string
}

export default function Streak({ streakCount, badge }: Props) {
	return (
		<div className={styles.streakContainer}>
			<div className={styles.iconWrapper}>
				<FaFire className={styles.fireIcon} />
			</div>

			<div className={styles.info}>
				<div className={styles.count}>
					{streakCount}-day streak
				</div>
				<div className={styles.badge}>
					{badge}
				</div>
			</div>
		</div>
	)
}
