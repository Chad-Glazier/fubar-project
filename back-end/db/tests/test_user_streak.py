from datetime import date, timedelta

from db.models.User import User


ORIGINAL_DATA_DIR = User.data_dir
TEST_DATA_DIR = "./data/testing-data"


def setup_function(_):
	User.data_dir = TEST_DATA_DIR
	User._drop_table()


def teardown_function(_):
	User._drop_table()
	User.data_dir = ORIGINAL_DATA_DIR


def _user() -> User:
	return User.create(
		id="streak-user",
		display_name="Streak User",
		email="streak@example.com",
		password="secret",
	)


def test_record_activity_initializes_and_updates_streak():
	user = _user()
	day_one = date(2024, 1, 1)
	user.record_activity(day_one)

	reloaded = User.get_by_primary_key(user.id)
	assert reloaded is not None
	assert reloaded.current_streak == 1
	assert reloaded.longest_streak == 1
	assert reloaded.last_activity_date == day_one.isoformat()

	reloaded.record_activity(day_one + timedelta(days=1))
	reloaded = User.get_by_primary_key(user.id)
	assert reloaded.current_streak == 2
	assert reloaded.longest_streak == 2


def test_record_activity_ignores_same_day_and_resets_after_gap():
	user = _user()
	today = date(2024, 2, 1)
	user.record_activity(today)
	user.record_activity(today)  # same day
	reloaded = User.get_by_primary_key(user.id)
	assert reloaded.current_streak == 1

	reloaded.record_activity(today + timedelta(days=2))
	reloaded = User.get_by_primary_key(user.id)
	assert reloaded.current_streak == 1
	assert reloaded.longest_streak == 1


def test_record_activity_handles_out_of_order_dates():
	user = _user()
	day_one = date(2024, 3, 1)
	user.record_activity(day_one)
	user.record_activity(day_one + timedelta(days=1))
	reloaded = User.get_by_primary_key(user.id)
	assert reloaded.current_streak == 2

	# Backdated activity should not change streak
	reloaded.record_activity(day_one)
	reloaded = User.get_by_primary_key(user.id)
	assert reloaded.current_streak == 2
