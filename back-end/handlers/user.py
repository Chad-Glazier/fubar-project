from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated
from fastapi import APIRouter, HTTPException, Response, Request
from uuid import uuid4
from http import HTTPStatus
import argon2

from db.models.User import User, UserSession, TOKEN_NAME
from db.models.UserReview import UserReview

password_hasher = argon2.PasswordHasher()

user_router = APIRouter(prefix = "/user", tags = ["users"])

###############################################################################
# 
# The types that will be used by this router are defined below.
#

class RegistrationDetails(BaseModel):
	display_name: Annotated[str, StringConstraints(min_length=1)]
	email: EmailStr
	password: Annotated[str, StringConstraints(min_length=1)]

class UserCredentials(BaseModel):
	email: EmailStr
	password: Annotated[str, StringConstraints(min_length=1)]

class UserDetails(BaseModel):
	display_name: str
	email: str
	reviews: list[UserReview]

###############################################################################
# 
# The request handlers are defined below.
#

#
# Lets users create accounts.
#
@user_router.post("/")
async def register_user(user_details: RegistrationDetails, resp: Response) \
	-> None:
	# Validate the data:
	if User.get_first_where(email = user_details.email) != None:
		raise HTTPException(
			status_code = HTTPStatus.CONFLICT, 
			detail = "That email is already registered."
		)
	if User.get_first_where(display_name = user_details.display_name) != None:
		raise HTTPException(
			status_code = HTTPStatus.CONFLICT,
			detail = "That display name is taken."
		)
	
	# Generate a unique ID.
	unique_id = str(uuid4())
	while User.get_by_primary_key(unique_id) != None:
		unique_id = str(uuid4())
	
	# Hash the password
	hashed_password = password_hasher.hash(user_details.password)

	# Store the user record in the database
	new_user = User(
		id = unique_id,
		display_name = user_details.display_name,
		email = user_details.email,
		password = hashed_password
	)
	success = new_user.post()

	# Check for an unexpected error
	if not success:
		raise HTTPException(
			status_code = HTTPStatus.INTERNAL_SERVER_ERROR,
			detail = "An unexpected server error occurred."
		)
	
	# Create a session for the new user
	new_user.create_session(resp)
	resp.status_code = HTTPStatus.CREATED

#
# Gets the data about the currently logged in user.
#
@user_router.get("/")
async def account_info(req: Request) -> UserDetails:
	user = User.from_session(req)
	if user == None:
		raise HTTPException(
			status_code = HTTPStatus.NOT_FOUND, 
			detail = "Not currently logged in."
		)
	
	user_reviews: list[UserReview] = []
	for review in UserReview.get_where(user_id = user.id):
		user_reviews.append(review)
	
	return UserDetails(
		display_name = user.display_name,
		email = user.email,
		reviews = user_reviews
	)

#
# Lets users log out (i.e., delete their session).
#
@user_router.delete("/session")
async def log_out(req: Request, resp: Response) -> None:
	session = UserSession.from_request(req)
	if session == None:
		return
	session.delete()
	resp.delete_cookie(TOKEN_NAME)

#
# Lets users log in (i.e., create a session).
#
@user_router.post("/session")
async def log_in(credentials: UserCredentials, resp: Response):
	user = User.get_first_where(email = credentials.email)

	if user == None:
		raise HTTPException(
			status_code = HTTPStatus.NOT_FOUND,
			detail = "That email is not recognized."
		)

	try:
		# raises an exception if it doesn't match	
		password_hasher.verify(
			user.password, 
			credentials.password
		)

		user.create_session(resp)

		if password_hasher.check_needs_rehash(user.password):
			user.password = password_hasher.hash(credentials.password)
			user.patch()

	except argon2.exceptions.VerifyMismatchError:
		raise HTTPException(
			status_code = HTTPStatus.UNAUTHORIZED,
			detail = "Password is incorrect."
		)
	
	except:
		raise HTTPException(
			status_code = HTTPStatus.INTERNAL_SERVER_ERROR,
			detail = "Log in failed for an unknown reason."
		)
	
