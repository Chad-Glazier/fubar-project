import styles from "@/styles/Search.module.css"
import { GetServerSideProps } from "next"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import BookCard from "@/lib/components/BookCard"
import Head from "next/head"
import { Book } from "@/lib/server/schema"
import server from "@/lib/server"
import PaginationControls from "@/lib/components/PaginationControls"

type Props = {
	searchResults: Book[]
	pageNumber: number
	nextPagePath: string | null
	prevPagePath: string | null
}

export const getServerSideProps: GetServerSideProps<Props> = async (context) => {
	const searchTerm = context.params!.bookTitle as string
	let pageQuery = context.query?.page as string | undefined

	if (searchTerm === "") {
		return { notFound: true }
	}

	let page = 1
	if (pageQuery !== undefined) {
		page = parseInt(pageQuery, 10)
		if (Number.isNaN(page) || page < 1) {
			return { notFound: true }
		}
	}

	const searchResults = await server.book.search(searchTerm, page)

	return {
		props: {
			pageNumber: page,
			nextPagePath: searchResults.next,
			prevPagePath: searchResults.prev,
			searchResults: searchResults.books,
		}
	}
}

export default function SearchResults({ 
	pageNumber,
	searchResults,
	nextPagePath,
	prevPagePath,
}: Props) {
	const router = useRouter()
	const { user, setUser } = useUser()

	return <>
		<Head>
			<title>Reading List | Results for {}</title>
			<meta name="description" content={`View your saved books.`} />
		</Head>
		<main className={`${styles.main}`}>
			<div className={styles.container}>
				{searchResults.length === 0 ?
					<em>No results were found.</em>
					:
					searchResults.map(book => 
						<BookCard 
							key={book.id}
							{...book} 
							initiallySaved={
								user ?
									user.savedBooks.some(
										savedBook => savedBook.id === book.id
									)
									:
									false
							}
							onSave={() => {
								if (user) {
									server.user.saveBook(book.id)
								} else {
									router.push("/login")
								}
							}}
							onUnsave={() => {
								if (user) {
									server.user.unsaveBook(book.id)
								} else {
									router.push("/login")
								}
							}}
							/>
					)
				}
			</div>
			<PaginationControls 
				page={pageNumber} 
				next={nextPagePath} 
				prev={prevPagePath} 
			/>
		</main>
	</>
}
