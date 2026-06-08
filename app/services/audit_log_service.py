from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    admin_id: int,
    action: str,
    target_user_id: int | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        admin_id=admin_id,
        action=action,
        target_user_id=target_user_id,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[AuditLog]:
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
