from fastapi import APIRouter
from db.camelized_model import CamelizedModel

profile_pictures_router = APIRouter(prefix = "/profile_pictures", tags = ["profile pictures"])

###############################################################################
# 
# The types that will be used by this router are defined below.
#

class ProfilePicture(CamelizedModel):
	id: str
	relative_url: str

###############################################################################
# 
# The handlers are defined below.
#

# The profile pictures are hard-coded in right now, stored in the `/public` 
# folder.
profile_pictures: list[ProfilePicture] = \
	[ProfilePicture(id = str(i), relative_url = f"public/profile_pictures/bot_{i}.png") for i in range(1, 14)]

@profile_pictures_router.get("/all")
async def get_all_profile_pictures() -> list[ProfilePicture]:
	"""
	Get a list of objects that represent different profile pictures.
	"""
	return profile_pictures
