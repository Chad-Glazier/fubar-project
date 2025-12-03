from datetime import date

from fastapi.testclient import TestClient

from db.models.User import User
from server import app


client = TestClient(app)
ORIGINAL_DIR = User.data_dir
TEST_DIR = "./data/testing-data"


def setup_function(_):
	User.data_dir = TEST_DIR
	User._drop_table()


def teardown_function(_):
	User._drop_table()
	User.data_dir = ORIGINAL_DIR


def test_user_streak_endpoint_returns_data():
	user = User.create(
		id="streak-user",
		display_name="Reader",
		email="reader@example.com",
		password="secret",
	)
	user.record_activity(date(2024, 6, 1))
	user.record_activity(date(2024, 6, 2))

	resp = client.get(f"/user/{user.id}/streak")
	assert resp.status_code == 200
	data = resp.json()
	assert data["currentStreak"] == 2
	assert data["longestStreak"] == 2
	assert data["badge"] != ""
	assert data["lastActivityDate"] == date(2024, 6, 2).isoformat()
