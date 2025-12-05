from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus

from db.camelized_model import CamelizedModel
from db.models.User import User
from db.models.AdminUser import AdminUser
from db.models.Report import Report
from db.models.UserReview import UserReview
from db.models.AuditLog import AuditLog


admin_reports_router = APIRouter(prefix="/admin/reports", tags=["admin"])

# ============================================================
# BODY SCHEMAS
# ============================================================


# ---------------------------------------------------------
# Helper: require admin login
# ---------------------------------------------------------
def require_admin(req: Request) -> AdminUser:
    admin = AdminUser.from_session(req)
    if admin is None:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Admin privileges required."
        )
    return admin


# ---------------------------------------------------------
# USER-FACING REPORT SUBMISSION
# POST /admin/reports
# ---------------------------------------------------------
class ReportDetails(CamelizedModel):
    review_id: str
    reason: str
    text: str
    
@admin_reports_router.post("")
async def submit_report(data: ReportDetails, req: Request) -> Report:
    user = User.from_session(req)
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Login required.")

    # Validate review exists
    review = UserReview.get_by_primary_key(data.review_id)
    if review is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Review not found.")

    report = Report(
        id=Report.new_id(),
        review_id=data.review_id,
        user_id=user.id,
        reason=data.reason,
        text=data.reason,
    )
    report.put()

    return report
    # 200 OK — test expects this


# ---------------------------------------------------------
# ADMIN VIEW REPORTS
# GET /admin/reports
# ---------------------------------------------------------
@admin_reports_router.get("")
async def list_reports(req: Request):
    require_admin(req)
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
