from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus

from db.models.User import User
from db.models.Report import Report
from db.models.UserReview import UserReview
from db.models.AuditLog import AuditLog


admin_reports_router = APIRouter(prefix="/admin/reports", tags=["admin"])


# ---------------------------------------------------------
# Helper: require admin login
# ---------------------------------------------------------
def require_admin(req: Request) -> User:
    user = User.from_session(req)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Login required."
        )
    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Admin privileges required."
        )
    return user


# ---------------------------------------------------------
# USER-FACING REPORT SUBMISSION
# POST /admin/reports
# ---------------------------------------------------------
@admin_reports_router.post("")
async def submit_report(data: dict, req: Request):
    """
    Tests expect:
    POST /admin/reports
    {
        "review_id": "...",
        "reason": "...",
        "text": "..."
    }
    """

    user = User.from_session(req)
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Login required.")

    # Validate review exists
    review = UserReview.get_by_primary_key(data["review_id"])
    if review is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Review not found.")

    report = Report(
        id=Report.new_id(),
        review_id=data["review_id"],
        user_id=user.id,
        reason=data.get("reason", ""),
        text=data.get("text", ""),
    )
    report.put()

    return {"id": report.id}
    # 200 OK — test expects this


# ---------------------------------------------------------
# ADMIN VIEW REPORTS
# GET /admin/reports
# ---------------------------------------------------------
@admin_reports_router.get("")
async def list_reports(req: Request):
    admin = require_admin(req)
    reports = list(Report.get_all())
    return reports   # tests expect a LIST


# ---------------------------------------------------------
# ADMIN DELETE REPORT (IDEMPOTENT)
# DELETE /admin/reports/{report_id}
# ---------------------------------------------------------
@admin_reports_router.delete("/{report_id}")
async def delete_report(report_id: str, req: Request):
    admin = require_admin(req)

    report = Report.get_by_primary_key(report_id)

    # DELETE MUST BE IDEMPOTENT
    if report is not None:
        report.delete()
        AuditLog(
            id=AuditLog.new_id(),
            action="delete_report",
            admin_id=admin.id,
            target_id=report_id,
        ).put()

    return {"deleted": True}  # tests expect 200 always
