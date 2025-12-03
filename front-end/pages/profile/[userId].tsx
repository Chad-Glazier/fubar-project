import styles from "@/styles/Profile.module.css"
import server from "@/lib/server"
import { useState, useEffect } from "react"
import Head from "next/head"
import { useRouter } from "next/router"
import useUser from "@/lib/hooks/useUser"
import { GetServerSideProps } from "next"

export const getServerSideProps: GetServerSideProps = async (context) => {
	

	return {
		props: {
			
		}
	}
} 