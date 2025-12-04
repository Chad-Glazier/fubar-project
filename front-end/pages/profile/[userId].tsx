import styles from "@/styles/Profile.module.css"
import server from "@/lib/server"
import Head from "next/head"
import { GetServerSideProps } from "next"
import { AccountInfo, PopulatedReview } from "@/lib/server/schema"
import { SERVER_URL } from "@/env"
import ReviewSummary from "@/lib/components/ReviewSummary"

type Props = {
	accountInfo: Omit<AccountInfo, "reviews"> & {
		reviews: PopulatedReview[]
	}
}

export const getServerSideProps: GetServerSideProps<Props> = async (context) => {
	const { userId } = context.params as { userId: string }

	const accountInfo = await server.user.accountInfo(userId)

	if (accountInfo === null) {
		return { notFound: true }
	}

	let populatedReviews: PopulatedReview[] = []
	for (let review of accountInfo.reviews) {
		let bookDetails = await server.book.basicDetails(review.bookId)
		if (bookDetails === null) {
			continue
		}
		populatedReviews.push({
			...review,
			book: bookDetails,
			user: {
				id: accountInfo.id,
				displayName: accountInfo.displayName,
				profilePicturePath: accountInfo.profilePicturePath 
			}
		})
	}

	return {
		props: {
			accountInfo: {
				...accountInfo,
				reviews: populatedReviews
			}
		}
	}
}

export default function UserProfile({ accountInfo }: Props) {
	return <>
		<Head>
			<title>Reading List | {accountInfo.displayName}</title>
			<meta name="description" content={`View ${accountInfo.displayName}'s profile.`} />
		</Head>
		<main className={`${styles.page} ${styles.main}`}>
			<div className={`${styles.profileDisplay}`}>
				<img 
					src={SERVER_URL + accountInfo.profilePicturePath}
					alt={`${accountInfo.displayName}'s profile picture`}
					height={150}
					width={150}
				/>
				<h1>
					{`${accountInfo.displayName}'s Reviews`}
				</h1>
				<ReviewSummary reviews={accountInfo.reviews} showUser={false} showBook={true} />
			</div>
		</main>
	</>
}
