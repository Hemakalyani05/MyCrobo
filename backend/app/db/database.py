import json
import aiosqlite
from typing import List, Optional, Dict, Any
from ..core.config import DATABASE_PATH
from ..models.schemas import AuditReport

_db_initialized = False

async def init_db():
    global _db_initialized
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                repo_name TEXT,
                source_type TEXT,
                target TEXT,
                created_at TEXT,
                security_score INTEGER,
                grade TEXT,
                total_findings INTEGER,
                report_json TEXT
            )
        """)
        await db.commit()
    _db_initialized = True

async def save_report(report: AuditReport):
    global _db_initialized
    if not _db_initialized:
        await init_db()

    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO scans 
            (scan_id, repo_name, source_type, target, created_at, security_score, grade, total_findings, report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report.scan_id,
            report.metadata.repo_name,
            report.source_type,
            report.target,
            report.created_at,
            report.summary.security_score,
            report.summary.grade,
            report.summary.total_findings,
            report.model_dump_json()
        ))
        await db.commit()

async def get_report(scan_id: str) -> Optional[AuditReport]:
    global _db_initialized
    if not _db_initialized:
        await init_db()

    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT report_json FROM scans WHERE scan_id = ?", (scan_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return AuditReport.model_validate_json(row[0])
    return None

async def list_scans() -> List[Dict[str, Any]]:
    global _db_initialized
    if not _db_initialized:
        await init_db()

    scans = []
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("""
            SELECT scan_id, repo_name, source_type, target, created_at, security_score, grade, total_findings 
            FROM scans ORDER BY created_at DESC LIMIT 50
        """) as cursor:
            async for row in cursor:
                scans.append({
                    "scan_id": row[0],
                    "repo_name": row[1],
                    "source_type": row[2],
                    "target": row[3],
                    "created_at": row[4],
                    "security_score": row[5],
                    "grade": row[6],
                    "total_findings": row[7]
                })
    return scans
