from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction, AuditLog


def create_audit_log(
    db: Session,
    admin_id: int,
    action: AuditAction,
    target_user_id: int | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        admin_id=admin_id,
        action=action.value,
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
    action: AuditAction | None = None,
    admin_id: int | None = None,
    target_user_id: int | None = None,
) -> list[AuditLog]:
    query = db.query(AuditLog)

    if action is not None:
        query = query.filter(AuditLog.action == action.value)

    if admin_id is not None:
        query = query.filter(AuditLog.admin_id == admin_id)

    if target_user_id is not None:
        query = query.filter(AuditLog.target_user_id == target_user_id)

    return (
        query
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
