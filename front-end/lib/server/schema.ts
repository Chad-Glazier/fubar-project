import Profile from "@/pages/profile"
import { z } from "zod"

export const ImageLinksSchema = z.record(z.string(), z.string())
export type ImageLinks = z.infer<typeof ImageLinksSchema>

export const BookSchema = z.object({
	id: z.string(),
	title: z.string(),
	authors: z.array(z.string()),
	categories: z.array(z.string()).nullable(),
	description: z.string().nullable(),
	imageLinks: ImageLinksSchema.nullable(),
	averageRating: z.number().nullable(),
})
export type Book = z.infer<typeof BookSchema>

export const ReviewSchema = z.object({
	id: z.string(),
	userId: z.string(),
	bookId: z.string(),
	rating: z.number(),
	text: z.string(),
})
export type Review = z.infer<typeof ReviewSchema>

/**
 *  as returned from `GET /books/{book_id}`
 */ 
export const BookDetailsSchema = z.object({
	book: BookSchema,
	averageRating: z.number(),
	reviewCount: z.number(),
	reviews: z.array(ReviewSchema)
})
/**
 *  as returned from `GET /books/{book_id}`
 */ 
export type BookDetails = z.infer<typeof BookDetailsSchema>

export const BasicUserInfoSchema = z.object({
	id: z.string(),
	displayName: z.string(),
	profilePicturePath: z.string(),
})
export type BasicUserInfo = z.infer<typeof BasicUserInfoSchema>

export const AccountInfoSchema = z.object({
	id: z.string(),
	displayName: z.string(),
	profilePicturePath: z.string(),
	reviews: z.array(ReviewSchema),
})
export type AccountInfo = z.infer<typeof AccountInfoSchema>

export const PersonalInfoSchema = z.intersection(
	z.object({
		email: z.email(),
		savedBooks: z.array(BookSchema),
	}),
	AccountInfoSchema,
)
export type PersonalInfo = z.infer<typeof PersonalInfoSchema>

export const UserStreakSchema = z.object({
	currentStreak: z.number(),
	longestStreak: z.number(),
	lastActivityDate: z.string().nullable(),
	badge: z.string(),
})
export type UserStreak = z.infer<typeof UserStreakSchema>

export const ServerErrorSchema = z.object({
	detail: z.string(),
})
export type ServerError = z.infer<typeof ServerErrorSchema>

export const ProfilePicturesSchema = z.array(z.object({
	id: z.string(),
	relativeUrl: z.string()
}))
export type ProfilePictures = z.infer<typeof ProfilePicturesSchema>

export type PopulatedReview = Review & {
	book: Book,
	user: BasicUserInfo
}

export const RecommendationsSchema = z.array(z.object({
	book: BookSchema.nullable(),
	bookId: z.string().nullable(),
	score: z.number()
}))
export type Recommendations = z.infer<typeof RecommendationsSchema>

export const SentimentSchema = z.object({
	bookId: z.string(),
	sentiment: z.string(),
	score: z.number(),
	scores: z.record(z.string(), z.number()), 
	reviewCount: z.number(),
	cachedAt: z.number(),           // epoch seconds
})
export type Sentiment = z.infer<typeof SentimentSchema>