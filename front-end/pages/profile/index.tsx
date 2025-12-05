import styles from "@/styles/Profile.module.css"
import server from "@/lib/server"
import { useState, useEffect } from "react"
import Head from "next/head"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import { SERVER_URL } from "@/env"
import { GetServerSideProps } from "next"
import ProfilePicturePicker from "@/lib/components/ProfilePicturePicker"
import { BasicUserInfo, PopulatedReview } from "@/lib/server/schema"
import ReviewSummary from "@/lib/components/ReviewSummary"

type Props = {
	allowedProfilePicturePaths: string[]
}

export const getServerSideProps: GetServerSideProps<Props> = async (context) => {
	const allowedProfilePicturePaths = await server.user.availableProfilePictures()

	return {
		props: {
			allowedProfilePicturePaths
		}
	}
}

export default function Profile({ allowedProfilePicturePaths }: Props) {
	const router = useRouter()
	const { user, setUser } = useUser()
	const [ loading, setLoading ] = useState(false)
	const [ editing, setEditing ] = useState(false)
	const [ errorMessage, setErrorMessage ] = useState("")
	const [ reviews, setReviews ] = useState<PopulatedReview[] | null>(null)
	const [ changingProfilePic, setChangingProfilePic ] = useState<boolean>(false)

	useEffect(() => {
		if (user === undefined) {
			return
		}
		
		if (user === null) {
			router.push("/login")
			return
		}

		const userBasicInfo: BasicUserInfo = {
			id: user.id,
			displayName: user.displayName,
			profilePicturePath: user.profilePicturePath
		};

		(async () => {
			let populatedReviews: PopulatedReview[] = []
			for (let review of user.reviews) {
				let book = await server.book.basicDetails(review.bookId)
				if (book !== null) {
					populatedReviews.push({ ...review, book, user: userBasicInfo})
				}
			}
			setReviews(populatedReviews)
		})()
	}, [user, router])

	async function updateProfilePicture(newProfilePicPath: string) {
		setLoading(true)
		const err = await server.user.updateAccount({
			profilePicturePath: newProfilePicPath
		})
		if (user) {
			user.profilePicturePath = newProfilePicPath
		}
		setLoading(false)
	}

	async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
		e.preventDefault()

		const formData = new FormData(e.currentTarget)

		const displayName = formData.get("display_name")!.toString()
		const email = formData.get("email")!.toString()
		const password = formData.get("password")!.toString()
		const confirmPassword = formData.get("confirm_password")!.toString()

		if (password != confirmPassword) {
			setErrorMessage("Ensure that the passwords match.")
			return
		}

		let updateObject: Record<string, string> = {}
		if (email != "") updateObject["email"] = email
		if (displayName != "") updateObject["displayName"] = displayName
		if (password != "") updateObject["password"] = password

		setLoading(true)
		const err = await server.user.updateAccount(updateObject)

		if (err != null) {
			setErrorMessage(err.message)
			setLoading(false)
			return
		}

		setErrorMessage("")
		const userDetails = await server.user.personalInfo()
		setUser(userDetails)
		setLoading(false)
		if (user === null) {
			setErrorMessage("An unexpected error occured. Please try again.")
		} else {
			router.push("/profile")
		}
	}

	if (user === null) {
		return <></>
	}
	if (user === undefined) {
		return <>loading...</>
	}
	return <>
		<Head>
			<title>Reading List | My Account</title>
			<meta name="description" content={`View ${user.displayName}'s profile.`} />
		</Head>
		{changingProfilePic ?
			<ProfilePicturePicker 
				relativeImagePaths={allowedProfilePicturePaths}
				onClose={() => setChangingProfilePic(false)}
				onSelect={newProfilePicPath => {
					updateProfilePicture(newProfilePicPath)
					setChangingProfilePic(false)
				}}
			/>
			:
			<></>}
		<main className={`${styles.page} ${styles.main}`}>
			<div className={`${styles.profileDisplay}`}>
				<img 
					className={`${styles.clickable}`}
					src={SERVER_URL + user.profilePicturePath}
					alt={`${user.displayName}'s profile picture`}
					height={150}
					width={150}
					onClick={() => setChangingProfilePic(true)}
				/>
				<form onSubmit={handleSubmit}>
					<fieldset disabled={loading || !editing} style={{ border: "none", padding: 0 }}>
						<div>
							<label htmlFor="display_name">Display Name</label><br />
							<input type="text" id="display_name" name="display_name" defaultValue={user.displayName} />
						</div>

						<div>
							<label htmlFor="email">Email</label><br />
							<input type="email" id="email" name="email" defaultValue={user.email} />
						</div>

						<div hidden={!editing}>
							<label htmlFor="password">Password</label><br />
							<input type="password" id="password" name="password" minLength={8} />
						</div>

						<div hidden={!editing}>
							<label htmlFor="confirm_password">Confirm Password</label><br />
							<input type="password" id="confirm_password" name="confirm_password" minLength={8} />
						</div>

						<p hidden={errorMessage === "" || !editing}>{errorMessage}</p>

						<button type="submit" hidden={!editing}>Update Account Details</button>
					</fieldset>
				</form>
				<button onClick={() => setEditing(!editing)}>
					{editing ? "Cancel Changes" : "Edit Profile"}
				</button>
				{
					reviews === null ?
						<></>
						:
						<ReviewSummary 
							reviews={reviews} 
							showBook={true} 
							showUser={false} 
							deleteable={true} 
							onDelete={(review) => {
								setReviews(prev => {
									if (prev === null) {
										return null
									}
									return prev.filter(existingReview => existingReview.id != review.id)
								})
								user.reviews = user.reviews.filter(existingReview => existingReview.id != review.id)
							}}	
						/>
				}
			</div>
		</main>
	</>
}
