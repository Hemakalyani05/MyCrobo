import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional
from ..models.schemas import ScanRequest, AuditReport, AgentEvent
from ..ingestion.repo_loader import RepoLoader
from ..ingestion.language_detector import analyze_repository
from ..scanner.engine import ScanEngine
from .llm_client import LLMClient
from .reasoning import ReasoningAgent
from ..db.database import save_report

class AuditOrchestrator:
    def __init__(self, request: ScanRequest):
        self.request = request
        self.scan_id = f"audit-{uuid.uuid4().hex[:10]}"
        self.queue: asyncio.Queue = asyncio.Queue()

    async def emit(self, event_type: str, stage: str, pct: int, message: str, data: Optional[dict] = None):
        evt = AgentEvent(
            type=event_type,
            stage=stage,
            progress_percent=pct,
            message=message,
            data=data
        )
        await self.queue.put(evt)

    async def execute_scan(self) -> AuditReport:
        start_time = time.time()
        await self.emit("log", "Ingestion", 5, f"Initializing repository ingestion for source '{self.request.source_type}'...")

        # 1. Load Repository
        try:
            repo_name, repo_path = RepoLoader.load(
                self.request.source_type,
                self.request.target,
                self.request.language
            )
        except Exception as e:
            await self.emit("error", "Ingestion", 0, f"Failed to ingest target: {str(e)}")
            raise e

        await self.emit("log", "Architecture Detection", 15, f"Analyzing architecture and directory tree at {repo_name}...")

        # 2. Analyze Architecture & Languages
        metadata = analyze_repository(repo_path)
        metadata.repo_name = repo_name

        langs_str = ", ".join(f"{l.language} ({l.percentage}%)" for l in metadata.languages[:3]) or "Generic"
        fws_str = ", ".join(metadata.frameworks) if metadata.frameworks else "Standard"
        await self.emit(
            "log",
            "Architecture Detection",
            25,
            f"Detected: {langs_str} | Frameworks: {fws_str} | Total Files: {metadata.total_files}",
            {"metadata": metadata.model_dump()}
        )

        # 3. Deterministic Scanning
        scanner = ScanEngine(repo_path, metadata)

        # Progress bridge
        def progress_cb(stage: str, pct: int, msg: str):
            asyncio.create_task(self.queue.put(AgentEvent(
                type="progress",
                stage=stage,
                progress_percent=pct,
                message=msg
            )))

        await self.emit("progress", "Deterministic Analysis", 30, "Launching concurrent AST, Security, Slop, and Debt scanners...")
        raw_findings = scanner.run(progress_callback=progress_cb)

        await self.emit("log", "AI Reasoning Agent", 70, f"Deterministic pass found {len(raw_findings)} potential issues. Initializing AI reasoning agent...")

        # 4. AI Reasoning & Verification
        llm = LLMClient(
            provider=self.request.ai_model or "heuristic",
            gemini_api_key=self.request.gemini_api_key,
            openai_api_key=self.request.openai_api_key,
            ollama_url=self.request.ollama_url or "http://localhost:11434"
        )
        reasoner = ReasoningAgent(repo_path, metadata, llm)

        await self.emit("progress", "AI Reasoning Agent", 85, "Filtering false positives and synthesizing unified diff patches...")
        verified_findings, summary, executive_analysis = await reasoner.verify_and_enrich(raw_findings)

        duration = round(time.time() - start_time, 2)
        report = AuditReport(
            scan_id=self.scan_id,
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            source_type=self.request.source_type,
            target=self.request.target,
            metadata=metadata,
            summary=summary,
            findings=verified_findings,
            agent_analysis=executive_analysis,
            duration_seconds=duration
        )

        # 5. Persist to DB
        await save_report(report)

        await self.emit(
            "complete",
            "Audit Complete",
            100,
            f"Audit completed in {duration}s! Security Score: {summary.security_score}/100 (Grade: {summary.grade})",
            {"report": report.model_dump()}
        )

        return report

    async def stream_events(self) -> AsyncGenerator[str, None]:
        scan_task = asyncio.create_task(self.execute_scan())

        while True:
            # Check if there is an event in queue
            try:
                evt = await asyncio.wait_for(self.queue.get(), timeout=0.5)
                yield f"data: {evt.model_dump_json()}\n\n"
                if evt.type in ["complete", "error"]:
                    break
            except asyncio.TimeoutError:
                if scan_task.done():
                    # Consume any remaining events
                    while not self.queue.empty():
                        rem_evt = self.queue.get_nowait()
                        yield f"data: {rem_evt.model_dump_json()}\n\n"
                    break
                continue
