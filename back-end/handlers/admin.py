from fastapi import APIRouter, Request, HTTPException
from http import HTTPStatus
from pydantic import BaseModel, Field

from db.models.User import User
from db.models.UserReview import UserReview
from db.models.Report import Report
from db.models.Penalty import Penalty
from db.models.AuditLog import AuditLog


admin_router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================
# AUTH HELPERS
# ============================================================
def require_admin(req: Request) -> User:
    """Return authenticated admin user or throw 401."""
    user = User.from_session(req)
    if user is None or not user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Administrator access required."
        )
    return user


# ============================================================
# DASHBOARD (test_admin_auth)
# GET /admin/dashboard
# ============================================================
@admin_router.get("/dashboard")
async def get_dashboard(req: Request):
    require_admin(req)
    return {
        "flagged_reviews": list(Report.get_all())
    }


# ============================================================
# AUDIT LOG (test_admin_auth)
# GET /admin/audit
# ============================================================
@admin_router.get("/audit")
async def get_audit(req: Request):
    require_admin(req)
    return list(AuditLog.get_all())
    

# ============================================================
# BODY SCHEMAS
# ============================================================
class ReportBody(BaseModel):
    reason: str = ""
    text: str = ""


class PenaltyBody(BaseModel):
    penalty_type: str
    reason: str
    duration_days: int = Field(ge=0)


# ============================================================
# 1. USER SUBMITS A REPORT
# POST /admin/report/{review_id}
# ============================================================
@admin_router.post("/report/{review_id}")
@admin_router.post("/reports/{review_id}")
async def report_review(review_id: str, body: ReportBody, req: Request):
    user = User.from_session(req)
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Login required.")

    review = UserReview.get_by_primary_key(review_id)
    if review is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Review not found.")

    report = Report(
        id=Report.new_id(),
        review_id=review_id,
        user_id=user.id,
        reason=body.reason,
        text=body.text
    )
    report.put()

    return {"id": report.id}


# ============================================================
# 2. ALTERNATE REPORT SUBMISSION  
# POST /admin/reports
# ============================================================
@admin_router.post("/reports")
async def submit_report(data: dict, req: Request):
    user = User.from_session(req)
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED, "Login required.")

    review = UserReview.get_by_primary_key(data["review_id"])
    if review is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Review not found.")

    report = Report(
        id=Report.new_id(),
        review_id=data["review_id"],
        user_id=user.id,
        reason=data.get("reason", ""),
        text=data.get("text", "")
    )
    report.put()

    return {"id": report.id}


# ============================================================
# 3. ADMIN – VIEW ALL REPORTS
# GET /admin/reports
# ============================================================
@admin_router.get("/reports")
async def get_reports(req: Request):
    require_admin(req)
    return list(Report.get_all())


# ============================================================
# 4. ADMIN – DELETE REPORT (IDEMPOTENT)
# DELETE /admin/reports/{report_id}
# ============================================================
@admin_router.delete("/reports/{report_id}")
async def delete_report(report_id: str, req: Request):
    admin = require_admin(req)

    report = Report.get_by_primary_key(report_id)
    if report:
        report.delete()

        AuditLog(
            id=AuditLog.new_id(),
            admin_id=admin.id,
            action="delete_report",
            target_id=report_id
        ).put()

    return {"deleted": True}   # always 200


# ============================================================
# 5. ADMIN – APPLY PENALTY
# POST /admin/penalty/{user_id}
# ============================================================
@admin_router.post("/penalty/{user_id}")
async def apply_penalty(user_id: str, body: PenaltyBody, req: Request):
    admin = require_admin(req)

    penalty = Penalty(
        id=Penalty.new_id(),
        user_id=user_id,
        penalty_type=body.penalty_type,
        reason=body.reason,
        duration_days=body.duration_days
    )
    penalty.put()

    AuditLog(
        id=AuditLog.new_id(),
        admin_id=admin.id,
        action="apply_penalty",
        target_id=user_id
    ).put()

    return {"id": penalty.id}


# ============================================================
# 6. ADMIN – DELETE REVIEW (IDEMPOTENT)
# DELETE /admin/reviews/{review_id}
# ============================================================
@admin_router.delete("/reviews/{review_id}")
async def admin_delete_review(review_id: str, req: Request):
    admin = require_admin(req)

    review = UserReview.get_by_primary_key(review_id)
    if review:
        review.delete()
        AuditLog(
            id=AuditLog.new_id(),
            admin_id=admin.id,
            action="delete_review",
            target_id=review_id,
        ).put()

    return {"deleted": True}
