import json
import logging
import os
import sys
import uuid
from logging.handlers import RotatingFileHandler
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.red_flag import RedFlagResult
from app.models.triage import TriageDecision
from app.models.otc import OTCResult
from app.models.output import TriageOutput
from app.db.models import TriageAuditLog

# Initialize logger once at module level
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "red_flag_audit.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logger
logger = logging.getLogger("red_flag_audit")
logger.setLevel(logging.INFO)
logger.propagate = False # Prevent double logging to parent loggers

# Use RotatingFileHandler for production safety (handles rotation and concurrent-ish append better than raw open)
# Max size 10MB, keep 5 backups
handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

async def log_red_flag_evaluation(session_id: str, result: RedFlagResult) -> None:
    """
    Logs a red flag evaluation to a JSONL file using a production-safe logger.
    Guaranteed never to raise an exception.
    """
    try:
        # Prepare record
        record = {
            "session_id": session_id,
            "evaluated_at": result.evaluated_at.isoformat(),
            # Scrub PHI: capture flag type/severity but exclude verbatim patient text (matched_on)
            "flags_matched": [
                {
                    "severity": m.severity.value if hasattr(m.severity, 'value') else str(m.severity),
                    "rule_id": getattr(m, "rule_id", "unknown"),
                    "requires_immediate_crisis_resource": m.requires_immediate_crisis_resource
                } for m in result.flags_matched
            ],
            "highest_severity": result.highest_severity,
            "evaluation_error": result.evaluation_error
        }

        # Log via the production-safe logger
        logger.info(json.dumps(record))

    except Exception as e:
        # Fail silently to stderr per requirements
        sys.stderr.write(f"CRITICAL ERROR in audit_logger (red_flag): {str(e)}\n")

async def log_triage_classification(session_id: str, decision: TriageDecision, db: AsyncSession) -> None:
    """Logs triage classification decision to DB."""
    try:
        event_data = {
            "triage_level": decision.triage_level.value,
            "confidence": decision.confidence,
            "primary_reason": decision.primary_reason,
            "contributing_factors": decision.contributing_factors,
            "classification_version": decision.classification_version,
            "classified_at": decision.classified_at.isoformat()
        }
        
        audit_entry = TriageAuditLog(
            session_id=uuid.UUID(session_id),
            event_type="triage_classified",
            event_data=event_data,
            classification_version=decision.classification_version
        )
        db.add(audit_entry)
        await db.commit()
    except Exception as e:
        sys.stderr.write(f"CRITICAL ERROR in audit_logger (classification): {str(e)}\n")

async def log_otc_evaluation(session_id: str, otc_result: OTCResult, db: AsyncSession) -> None:
    """Logs OTC evaluation outcome to DB."""
    try:
        suggestions_audit = []
        for sug in otc_result.suggestions:
            suggestions_audit.append({
                "name": sug.medicine.name,
                "approved": sug.approved,
                "rejection_reason": sug.rejection_reason
            })
            
        event_data = {"suggestions": suggestions_audit}
        
        audit_entry = TriageAuditLog(
            session_id=uuid.UUID(session_id),
            event_type="otc_evaluated",
            event_data=event_data
        )
        db.add(audit_entry)
        await db.commit()
    except Exception as e:
        sys.stderr.write(f"CRITICAL ERROR in audit_logger (otc): {str(e)}\n")

async def log_output_assembled(session_id: str, output: TriageOutput, db: AsyncSession) -> None:
    """Logs final output assembly metadata to DB (PHI scrubbed)."""
    try:
        # Never log explanation text or raw symptom strings
        event_data = {
            "triage_level": output.triage_level.value,
            "triage_label": output.triage_label,
            "had_crisis_resource": len(output.crisis_resources) > 0,
            "otc_count": len(output.approved_otc_suggestions),
            "llm_was_used": output.llm_was_used,
            "assembled_at": output.assembled_at.isoformat()
        }
        
        audit_entry = TriageAuditLog(
            session_id=uuid.UUID(session_id),
            event_type="output_built",
            event_data=event_data
        )
        db.add(audit_entry)
        await db.commit()
    except Exception as e:
        sys.stderr.write(f"CRITICAL ERROR in audit_logger (assembly): {str(e)}\n")

async def log_session_error(session_id: str, error_type: str, error_message: str, db: AsyncSession) -> None:
    """Logs pipeline or session errors to DB."""
    try:
        event_data = {
            "error_type": error_type,
            "error_message": error_message
        }
        
        audit_entry = TriageAuditLog(
            session_id=uuid.UUID(session_id),
            event_type="error",
            event_data=event_data
        )
        db.add(audit_entry)
        await db.commit()
    except Exception as e:
        sys.stderr.write(f"CRITICAL ERROR in audit_logger (error): {str(e)}\n")
