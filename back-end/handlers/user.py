from fastapi import APIRouter, HTTPException

from db.models import User

user_router = APIRouter(prefix = "/user", tags = ["users"])

@user_router.get("/{user_id}")
async def _get_user_root(user_id: str) -> :
	found_user = User.get_by_primary_key(user_id)
	if found_user == None:
		raise HTTPException(status_code = 404)
	else:
		return found_user
