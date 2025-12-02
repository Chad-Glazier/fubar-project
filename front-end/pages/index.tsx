import { Inter } from "next/font/google";
import styles from "@/styles/Home.module.css";

const inter = Inter({
	variable: "--font-inter",
	subsets: ["latin"],
});

export default function Home() {
	return (
		<>
			<div
				className={`${styles.page} ${inter.variable}`}
			>
				<main className={styles.main}>
					bazinga
				</main>
			</div>
		</>
	);
}
