import { Html, Main } from "next/document";

export default function Document() {
	return (
		<Html lang="en">
			<head>
				<title>Reading List</title>
				<meta name="description" content="A website to share book reviews and find recommendations" />
				<link rel="apple-touch-icon" sizes="180x180" href="/favicon_io/apple-touch-icon.png" />
				<link rel="icon" type="image/png" sizes="32x32" href="/favicon_io/favicon-32x32.png" />
				<link rel="icon" type="image/png" sizes="16x16" href="/favicon_io/favicon-16x16.png" />
				<link rel="manifest" href="/favicon_io/site.webmanifest" />
			</head>
			<body>
				<Main />
			</body>
		</Html>
	);
}
