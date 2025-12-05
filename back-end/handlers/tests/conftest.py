import pytest

from db.models.AuditLog import AuditLog
from db.models.Penalty import Penalty
from db.models.Report import Report
from db.models.User import User, UserSession
from db.models.UserReview import UserReview
from db.models.AdminUser import AdminUser, AdminSession


@pytest.fixture(autouse=True)
def reset_persistent_tables():
    # Keep test state isolated by clearing mutable tables before each test.
    tables = (AuditLog, Penalty, Report, AdminSession, AdminUser, UserSession, User, UserReview)
    original_data_dir = tables[0].data_dir
    for model in tables:
        model.data_dir = "data/testing-data"
        model._drop_table()
    yield
    for model in tables:
        model._drop_table()
        model.data_dir = original_data_dir
