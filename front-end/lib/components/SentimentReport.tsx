import { FaChartBar, FaInfoCircle } from "react-icons/fa";
import styles from "./SentimentReport.module.css";

type Props = {
	sentiment: string
	score: number
	scores: Record<string, number>
	reviewCount: number
}

export default function SentimentReport({
	sentiment,
	score,
	scores,
	reviewCount,
}: Props) {
	if (reviewCount === 0) {
		return (
			<div className={styles.card}>
				<div className={styles.empty}>
					<FaInfoCircle size={20} />
					<p>No sentiment analysis yet &mdash; this book has no written reviews.</p>
				</div>
			</div>
		);
	}

	return (
		<div className={styles.card}>
			<h2 className={styles.header}>
				<FaChartBar size={18} />
				Sentiment Overview
			</h2>

			<div className={styles.row}>
				<span className={styles.label}>Overall Sentiment</span>
				<span className={styles.value}>
					{sentiment} ({score.toFixed(3)})
				</span>
			</div>

			<div className={styles.subheader}>Score Breakdown</div>
			<div className={styles.scoreList}>
				{Object.entries(scores).map(([key, value]) => (
					<div key={key} className={styles.scoreItem}>
						<span>{key}</span>
						<span>{value.toFixed(3)}</span>
					</div>
				))}
			</div>

			<div className={styles.row}>
				<span className={styles.label}>Reviews Analyzed</span>
				<span className={styles.value}>{reviewCount}</span>
			</div>
		</div>
	);
}
