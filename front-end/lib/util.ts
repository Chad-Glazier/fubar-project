import server from "./server"
import { Book } from "./server/schema"

const RECOMMENDATIONS_PER_DAY = 100

export function setStoredRecommendations(userId: string, books: Book[]) {
	localStorage.setItem(
		userId + "_recommendations",
		JSON.stringify(books)
	)

	localStorage.setItem(
		userId + "_last_recommendations_update",
		Date.now().toString()
	)
}

export function getStoredRecommendations(userId: string): Book[] {
	let lastUpdateRecord = localStorage.getItem(userId + "_last_recommendations_update")
	let lastUpdate: number = 0
	if (lastUpdateRecord === null || Number.isNaN(parseInt(lastUpdateRecord))) {
		lastUpdate = 0
	} else {
		lastUpdate = parseInt(lastUpdateRecord)
	}

	const oneDayInMilliseconds = 24 * 60 * 60 * 1000

	if ((Date.now() - lastUpdate) > oneDayInMilliseconds) {
		server.user.recommendations(userId, RECOMMENDATIONS_PER_DAY)
			.then(recommendations => {
				const validRecommendations = recommendations
					.filter(recommendation => recommendation.book !== null)
					.map(recommendation => recommendation.book) as Book[]
				setStoredRecommendations(
					userId,
					validRecommendations
				)
			})
	}

	let stored = localStorage.getItem(
		userId + "_recommendations"
	)
	if (stored === null || stored.length === 0) {
		return []
	}

	return JSON.parse(stored) as Book[]
}