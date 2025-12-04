import styles from "@/styles/Home.module.css";
import Head from "next/head"

export default function Home() {
	return <>
		<Head>
			<title>Reading List | Home</title>
			<meta name="description" content="Find book recommendations, read reviews, and create your own." />
		</Head>
		<main className={`${styles.page} ${styles.main}`}>
			bazinga
		</main>
	</>
}
