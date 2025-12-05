from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from handlers import ROUTERS

app = FastAPI()

for router in ROUTERS:
	app.include_router(router)

app.add_middleware(
	CORSMiddleware,
	allow_origins = [
		"http://localhost:3000",
		"http://localhost:8000",
		"http://localhost"
	],
	allow_methods = ["*"],
	allow_credentials = True,
	allow_headers = ["*"]
)

app.mount("/public", StaticFiles(directory="public"), name="public")
