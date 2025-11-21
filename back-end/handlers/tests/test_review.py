from fastapi.testclient import TestClient
from handlers.user import RegistrationDetails

from db.models.User import User, UserSession, TOKEN_NAME
from db.models.UserReview import UserReview
from server import app

def setup():
	client = TestClient(app)

	client.post(
		"/user",
		content = RegistrationDetails(
			display_name = "eric_johnson",
			email = "ejohnson54@gmail.com",
			password = "stratocaster123"
		).model_dump_json()
	)

	test_user = User.get_first_where(email = "ejohnson54@gmail.com")
	assert test_user != None

	return client, test_user

def cleanup(client: TestClient, test_user: User):
	for session in UserSession.get_where(user_id = test_user.id):
		session.delete()

	for review in UserReview.get_where(user_id = test_user.id):
		review.delete()

	test_user.delete()
	
	client.cookies.delete(TOKEN_NAME)

def test_create_review():
	pass

def test_update_review():
	pass

def test_delete_review():
	pass
