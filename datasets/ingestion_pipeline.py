import os
import sys
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path to allow imports from app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.knowledge.datasets.manifest import DatasetManifest, NormalizedRecord
from app.knowledge.datasets.registry import DatasetRegistry
from app.knowledge.datasets.priority import DatasetPriorityManager
from app.knowledge.datasets.health import DatasetHealthManager
from app.knowledge.datasets.verify import DatasetVerifier
from app.knowledge.engines.chunking import ChunkEngine
from app.knowledge.engines.extractors import ExtractorFactory

try:
    import polars as pl
except ImportError:
    pl = None
import pandas as pd

BASE_DIR = Path("datasets")
CORE_DIRS = ["incoming", "raw", "processed", "normalized", "embeddings", "indexes", "metadata", "logs", "relationships"]

def setup_logging():
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "processing_v2.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("IngestionPipelineV2")

def determine_publisher(name: str) -> str:
    name_lower = name.lower()
    if "who" in name_lower: return "WHO"
    if "cdc" in name_lower: return "CDC"
    if "nih" in name_lower or "pubmed" in name_lower: return "NIH"
    if "clin_trials" in name_lower: return "Clinical Trials"
    if "guideline" in name_lower: return "Peer-reviewed Guidelines"
    if "41586" in name_lower: return "Research Papers" # Nature paper heuristic
    return "Unknown"

class IngestionPipelineV2:
    def __init__(self):
        for d in CORE_DIRS:
            (BASE_DIR / d).mkdir(parents=True, exist_ok=True)
            
        self.logger = setup_logging()
        self.registry = DatasetRegistry()
        self.health = DatasetHealthManager()
        self.priority = DatasetPriorityManager()
        self.verifier = DatasetVerifier()
        self.chunker = ChunkEngine(strategy="sentence")
        
        self.statistics = {
            "total_records": 0,
            "total_chunks": 0,
            "total_relationships": 0
        }

    def process_all(self):
        incoming_dir = BASE_DIR / "incoming"
        for item in incoming_dir.iterdir():
            if item.is_file() and item.suffix in [".csv", ".xlsx", ".json"]:
                self.process_dataset(item)
            elif item.is_dir():
                self.logger.info(f"Skipping directory {item.name}")
        self._save_statistics()
        self.generate_html_report()

    def process_dataset(self, file_path: Path):
        self.logger.info(f"Processing V2: {file_path.name}")
        dataset_id = file_path.stem.replace(".", "_")
        publisher = determine_publisher(file_path.stem)
        priority_score = self.priority.get_priority(publisher)
        evidence_level = self.priority.get_evidence_level(priority_score)
        
        # 1. Verification
        checksum = self.verifier.verify_checksum(str(file_path), "") # Dummy check for now, in reality we'd have it
        # Compute real checksum
        import hashlib
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha256.update(block)
        real_checksum = sha256.hexdigest()

        # 2. Manifest Creation
        manifest = DatasetManifest(
            dataset_id=dataset_id,
            name=file_path.name,
            publisher=publisher,
            license="Unknown",
            version="1.0",
            release_date=datetime.utcnow().date().isoformat(),
            checksum_sha256=real_checksum,
            processing_version="2.0",
            embedding_version="0.0",
            knowledge_version="1.0",
            language="en",
            country="Global",
            medical_domain="General",
            dataset_type="tabular",
            priority=priority_score,
            evidence_level=evidence_level,
            quality_score=0.0,
            processing_status="processing"
        )
        
        self.health.update_status(dataset_id, "processing_status", "processing")
        
        # 3. Read Data
        df = None
        try:
            if file_path.suffix == ".csv":
                if pl is not None:
                    try:
                        pl_df = pl.read_csv(str(file_path), ignore_errors=True)
                        df = pl_df.to_pandas()
                    except Exception:
                        df = pd.read_csv(file_path, low_memory=False, on_bad_lines='skip')
                else:
                    df = pd.read_csv(file_path, low_memory=False, on_bad_lines='skip')
            elif file_path.suffix == ".xlsx":
                df = pd.read_excel(file_path)
        except Exception as e:
            self.logger.error(f"Failed to read {file_path.name}: {e}")
            self.health.update_status(dataset_id, "processing_status", "failed")
            return

        if df is None or df.empty:
            self.logger.warning(f"Empty dataset {file_path.name}")
            return

        total_rows = len(df)
        nulls = int(df.isnull().sum().sum())
        missing_pct = (nulls / (total_rows * len(df.columns))) * 100
        quality_score = max(0.0, 100.0 - missing_pct)
        manifest.quality_score = quality_score
        
        self.health.update_metrics(dataset_id, {
            "coverage": 100.0,
            "missing_percentage": missing_pct,
            "null_percentage": missing_pct,
            "duplicate_percentage": 0.0,
            "quality_score": quality_score
        })

        # 4. Normalization, Chunking, Extraction
        norm_path = BASE_DIR / "normalized" / f"{dataset_id}_v2.jsonl"
        chunk_path = BASE_DIR / "embeddings" / f"{dataset_id}_chunks_v2.jsonl"
        rel_path = BASE_DIR / "relationships" / f"{dataset_id}_rels.jsonl"
        
        extractor = ExtractorFactory.get_extractor("diseases") # Using generic for now
        
        records_count = 0
        chunks_count = 0
        rels_count = 0

        with open(norm_path, "w", encoding="utf-8") as fnorm, \
             open(chunk_path, "w", encoding="utf-8") as fchunk, \
             open(rel_path, "w", encoding="utf-8") as frel:
            
            for _, row in df.iterrows():
                row_dict = row.dropna().to_dict()
                text_repr = " ".join([f"{k}: {v}" for k, v in row_dict.items()])
                
                # Normalized Record
                record = NormalizedRecord(
                    aura_id=str(uuid.uuid4()),
                    title=str(row_dict.get("name", row_dict.get("title", f"Row {records_count}"))),
                    text=text_repr,
                    category="unknown",
                    dataset=dataset_id,
                    dataset_version="1.0",
                    publisher=publisher,
                    evidence_level=evidence_level,
                    priority=priority_score,
                    confidence=quality_score,
                    language="en",
                    metadata=row_dict
                )
                fnorm.write(record.model_dump_json() + "\n")
                records_count += 1
                
                # Chunking
                chunks = self.chunker.process_record(record.model_dump())
                for chunk in chunks:
                    fchunk.write(chunk.model_dump_json() + "\n")
                    chunks_count += 1
                    
                # Relationships
                rels = extractor.extract_relationships(record.model_dump())
                for rel in rels:
                    frel.write(json.dumps(rel) + "\n")
                    rels_count += 1

        manifest.record_count = records_count
        manifest.chunk_count = chunks_count
        manifest.relationship_count = rels_count
        manifest.processing_status = "completed"
        
        self.statistics["total_records"] += records_count
        self.statistics["total_chunks"] += chunks_count
        self.statistics["total_relationships"] += rels_count

        self.registry.register(manifest)
        self.health.update_status(dataset_id, "processing_status", "completed")
        self.health.update_status(dataset_id, "embedding_status", "ready")
        self.health.update_status(dataset_id, "knowledge_graph_status", "ready")
        
        # Save manifest
        with open(BASE_DIR / "metadata" / f"{dataset_id}_manifest_v2.json", "w") as f:
            f.write(manifest.model_dump_json(indent=2))

    def _save_statistics(self):
        with open(BASE_DIR / "statistics_registry.json", "w") as f:
            json.dump(self.statistics, f, indent=2)

    def generate_html_report(self):
        html = ["<html><head><title>AURA V2 Ingestion Report</title><style>body{font-family:sans-serif;} table{border-collapse:collapse;width:100%;} th,td{border:1px solid #ddd;padding:8px;} th{background-color:#f2f2f2;}</style></head><body>"]
        html.append("<h2>Dataset Ingestion Health Report V2</h2><table>")
        html.append("<tr><th>Dataset ID</th><th>Publisher</th><th>Priority</th><th>Rows</th><th>Chunks</th><th>Relationships</th><th>Quality Score</th></tr>")
        
        for ds in self.registry.list_datasets():
            html.append(f"<tr><td>{ds.dataset_id}</td><td>{ds.publisher}</td><td>{ds.priority}</td><td>{ds.record_count}</td><td>{ds.chunk_count}</td><td>{ds.relationship_count}</td><td>{ds.quality_score:.2f}%</td></tr>")
            
        html.append("</table></body></html>")
        
        with open(BASE_DIR / "ingestion_report.html", "w") as f:
            f.write("\n".join(html))


if __name__ == "__main__":
    pipeline = IngestionPipelineV2()
    pipeline.process_all()
