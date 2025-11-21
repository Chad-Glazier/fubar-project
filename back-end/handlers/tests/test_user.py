from fastapi.testclient import TestClient
from fastapi import FastAPI
from handlers.user import RegistrationDetails, UserCredentials
from http import HTTPStatus

from handlers.user import user_router
from db.models.User import User, UserSession, TOKEN_NAME

app = FastAPI()
app.include_router(user_router)

def test_user_register_login_logout():
	
	new_client = TestClient(app)

	new_details = RegistrationDetails(
		display_name = "jimi_hendrix",
		email = "jhendrix42@gmail.com",
		password = "stratocaster123"
	)

	resp = new_client.post(
		"/user",
		content = new_details.model_dump_json()
	)

	assert resp.status_code == HTTPStatus.CREATED

	# Confirm that the user exists in the database

	new_user = User.get_first_where(
		display_name = "jimi_hendrix",
		email = "jhendrix42@gmail.com"
	)

	assert new_user != None

	# Confirm that there is now a session created (i.e., we are logged in)

	new_session = UserSession.get_first_where(
		user_id = new_user.id
	)

	assert new_session != None

	# Confirm that the cookie is set on the client

	assert new_client.cookies.get(TOKEN_NAME) == new_session.session_id

	# Check that redundant requests respond with conflict errors

	resp = new_client.post(
		"/user",
		content = new_details.model_dump_json()
	)

	assert resp.status_code == HTTPStatus.CONFLICT

	# Check that we can log out
	
	resp = new_client.delete("/user/session")

	assert resp.status_code == HTTPStatus.OK
	assert UserSession.get_first_where(user_id = new_user.id) == None

	# Check that we can log back in

	credentials = UserCredentials(
		email = "jhendrix42@gmail.com",
		password = "stratocaster123"
	)
	resp = new_client.post(
		"/user/session",
		content = credentials.model_dump_json()	
	)
	new_session = UserSession.get_first_where(user_id = new_user.id)

	assert new_session != None
	assert resp.status_code == HTTPStatus.OK
	assert new_client.cookies.get(TOKEN_NAME) == new_session.session_id

	# Cleanup

	new_user.delete()
	new_session.delete()
