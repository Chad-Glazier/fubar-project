type Review = {
	id: string
	userId: string
	bookId: string
	rating: number
	text: string
}

type AccountInfo = {
	displayName: string
	email: string
	reviews: Review[]
}
