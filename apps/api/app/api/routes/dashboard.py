from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db import get_db
from ...dependencies import get_current_user
from ...models import User
from ...schemas import DashboardResponse, ReportResponse
from ...services.dashboard import generate_weekly_report, get_dashboard_snapshot, list_reports


router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return get_dashboard_snapshot(db, current_user)


@router.get("/reports", response_model=list[ReportResponse])
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReportResponse]:
    return list_reports(db, current_user)


@router.post("/reports/weekly", response_model=ReportResponse)
def post_weekly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReportResponse:
    return generate_weekly_report(db, current_user)
