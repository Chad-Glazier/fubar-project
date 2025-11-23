from fastapi import FastAPI

from handlers import ROUTERS

app = FastAPI()

for router in ROUTERS:
	app.include_router(router)
