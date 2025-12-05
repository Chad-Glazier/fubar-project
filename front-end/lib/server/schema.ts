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
