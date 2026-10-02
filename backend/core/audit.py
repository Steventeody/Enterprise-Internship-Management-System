"""
PKL CMS — Audit Logger
Fungsi helper untuk mencatat semua operasi sensitif ke tabel audit_logs.
"""

import json
from django.utils import timezone


def log_audit(actor, action, entity_type=None, entity_id=None,
              old_data=None, new_data=None, request=None):
    """
    Catat satu entri audit log ke database.

    Dipanggil setelah setiap operasi penting:
    - CREATE_INTERN, ASSIGN_TASK, SUBMIT_TASK
    - REVIEW_SUBMISSION, FINALIZE_EVAL, GENERATE_BAST

    Jika tabel AuditLog belum di-migrate (fase awal dev), fungsi ini
    akan gracefully skip tanpa crash.
    """
    try:
        from core.audit_models import AuditLog  # import lazy
        ip = None
        ua = None
        if request:
            ip = _get_client_ip(request)
            ua = request.META.get("HTTP_USER_AGENT", "")[:500]

        AuditLog.objects.create(
            user=actor,
            action=action,
            entity_type=entity_type or "",
            entity_id=entity_id,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip,
            user_agent=ua,
        )
    except Exception:
        # Jangan crash karena audit gagal — log ke console saja
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"[AUDIT] Failed to write log: action={action} "
            f"entity={entity_type}:{entity_id}"
        )


def _get_client_ip(request):
    """Ambil IP client yang asli (handle reverse proxy)."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
