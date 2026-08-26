from fastapi import APIRouter

router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("/")
def get_audit_logs():
    return {
        "message": "Audit logs endpoint is working"
    }
