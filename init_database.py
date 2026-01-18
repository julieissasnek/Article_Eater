#!/usr/bin/env python3
"""
Database Initialization with Sample Data
Populates Article Eater database with realistic sample data
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random
import os

DB_PATH = os.environ.get("DB_PATH", "ae.db")

# Sample data templates
SAMPLE_AUTHORS = [
    ["Boubekri, M.", "Hull, R.B.", "Scott, K."],
    ["Aries, M.", "Veitch, J.", "Newsham, G."],
    ["Kaplan, R.", "Kaplan, S."],
    ["Ulrich, R.S.", "Zimring, C.", "Quan, X."],
    ["Evans, G.W.", "Cohen, S."],
    ["Kellert, S.R.", "Heerwagen, J.", "Mador, M."],
    ["Browning, W.", "Ryan, C.", "Clancy, J."],
    ["Terrapin Bright Green", ""],
    ["Gillis, K.", "Gatersleben, B."],
    ["Li, Q.", "Kobayashi, M.", "Kawada, T."]
]

SAMPLE_VENUES = [
    "Journal of Environmental Psychology",
    "Building and Environment",
    "Architectural Science Review",
    "Environment and Behavior",
    "Health & Place",
    "Indoor Air",
    "Lighting Research & Technology",
    "Applied Ergonomics",
    "Work: A Journal of Prevention, Assessment and Rehabilitation",
    "Frontiers in Psychology"
]

TOPICS = ["lighting", "biophilic", "spatial", "color", "acoustics", "thermal", "air-quality"]

def create_schema(conn):
    """Create database schema"""
    cursor = conn.cursor()
    
    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            article_id TEXT PRIMARY KEY,
            doi TEXT UNIQUE,
            corpus_id TEXT UNIQUE,
            title TEXT NOT NULL,
            authors TEXT,
            year INTEGER,
            venue TEXT,
            abstract TEXT,
            full_text TEXT,
            sections TEXT,
            text_length INTEGER,
            is_open_access BOOLEAN,
            citation_count INTEGER,
            url_pdf TEXT,
            ingested_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Findings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            finding_level TEXT CHECK(finding_level IN ('micro', 'meso', 'macro')),
            consequent TEXT NOT NULL,
            antecedents TEXT,
            operational_measure TEXT,
            measure_type TEXT,
            measure_direction TEXT,
            p_value REAL,
            effect_size REAL,
            effect_size_type TEXT,
            sample_size INTEGER,
            job_id TEXT,
            paper_id TEXT,
            passage TEXT,
            page_number INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (paper_id) REFERENCES articles(article_id) ON DELETE CASCADE
        )
    """)
    
    # Rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            rule_id TEXT PRIMARY KEY,
            rule TEXT NOT NULL,
            confidence REAL,
            triangulation_score REAL,
            contradiction_count INTEGER DEFAULT 0,
            job_id TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Rule evidence table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rule_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_id TEXT NOT NULL,
            article_id TEXT NOT NULL,
            passage TEXT,
            page_number INTEGER,
            stance TEXT CHECK(stance IN ('supporting', 'contradicting', 'neutral')),
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (rule_id) REFERENCES rules(rule_id) ON DELETE CASCADE,
            FOREIGN KEY (article_id) REFERENCES articles(article_id) ON DELETE CASCADE
        )
    """)
    
    # Processing queue table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_queue (
            job_id TEXT PRIMARY KEY,
            job_type TEXT CHECK(job_type IN ('L0_harvest', 'L1_cluster', 'L2_extract', 'L3_synthesize', 'L4_expand')),
            params TEXT,
            status TEXT CHECK(status IN ('pending', 'running', 'complete', 'failed')),
            priority INTEGER DEFAULT 100,
            created_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            error TEXT
        )
    """)
    
    conn.commit()
    print("✓ Database schema created")

def generate_sample_articles(conn, count=50):
    """Generate sample articles"""
    cursor = conn.cursor()
    
    article_ids = []
    
    for i in range(count):
        article_id = f"paper-{i+1}"
        doi = f"10.{1000+i}/example.2015.{i+1}"
        corpus_id = f"corpus-{i+1}"
        
        authors = random.choice(SAMPLE_AUTHORS)
        year = random.randint(2015, 2024)
        venue = random.choice(SAMPLE_VENUES)
        topic = random.choice(TOPICS)
        
        title = f"Effects of {topic} design on occupant wellbeing and performance in built environments: Study {i+1}"
        
        abstract = f"""This study investigates the impact of {topic} on occupant wellbeing and performance in office environments. 
We conducted a field study with n={50 + i*5} participants across {2 + i%5} different buildings. 
Results showed significant positive effects on stress reduction (p<0.05, d=0.{30 + i%40}) and cognitive performance (p<0.01, d=0.{25 + i%35}). 
Physiological measurements confirmed these findings, with cortisol levels reduced by {15 + i%20}% in optimal conditions. 
The study provides evidence-based guidelines for {topic} design in office settings. 
Implications for architectural practice and workplace design are discussed."""
        
        citation_count = random.randint(10, 300)
        is_open_access = random.choice([True, False])
        
        cursor.execute("""
            INSERT INTO articles (
                article_id, doi, corpus_id, title, authors, year, venue, 
                abstract, is_open_access, citation_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_id, doi, corpus_id, title, json.dumps(authors), 
            year, venue, abstract, is_open_access, citation_count,
            (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
        ))
        
        article_ids.append(article_id)
    
    conn.commit()
    print(f"✓ Generated {count} sample articles")
    return article_ids

def generate_sample_findings(conn, article_ids):
    """Generate sample findings from articles"""
    cursor = conn.cursor()
    
    consequents = [
        "stress levels", "cortisol levels", "cognitive performance", 
        "attention restoration", "productivity", "job satisfaction",
        "sleep quality", "heart rate variability", "blood pressure",
        "creative problem solving", "task completion time", "error rate"
    ]
    
    antecedents = [
        ["natural light exposure", "window access"],
        ["presence of plants", "biophilic elements"],
        ["ceiling height", "spatial openness"],
        ["color temperature", "lighting quality"],
        ["acoustic comfort", "noise levels"],
        ["thermal comfort", "temperature control"],
        ["air quality", "ventilation"]
    ]
    
    findings_count = 0
    
    for article_id in article_ids:
        # Generate 2-5 findings per paper
        num_findings = random.randint(2, 5)
        
        for j in range(num_findings):
            consequent = random.choice(consequents)
            antecedent_list = random.choice(antecedents)
            
            cursor.execute("""
                INSERT INTO findings (
                    finding_level, consequent, antecedents, 
                    operational_measure, measure_type, measure_direction,
                    p_value, effect_size, effect_size_type, sample_size,
                    paper_id, passage, page_number
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'micro',
                consequent,
                json.dumps(antecedent_list),
                f"{consequent} measured via standardized assessment",
                random.choice(['self-report', 'behavioral', 'physiological']),
                random.choice(['positive', 'negative']),
                round(random.uniform(0.001, 0.049), 3),
                round(random.uniform(0.2, 0.8), 2),
                'd',
                random.randint(30, 200),
                article_id,
                f"Participants showed significant improvement in {consequent} compared to control condition.",
                random.randint(5, 15)
            ))
            
            findings_count += 1
    
    conn.commit()
    print(f"✓ Generated {findings_count} sample findings")

def generate_sample_rules(conn, article_ids):
    """Generate sample synthesized rules"""
    cursor = conn.cursor()
    
    rules_data = [
        {
            "rule": "Natural light exposure (>500 lux) in office spaces correlates with 18-31% reduction in self-reported stress",
            "confidence": 0.82,
            "triangulation": 0.86,
            "studies": 7
        },
        {
            "rule": "Presence of living plants in indoor environments reduces cortisol levels by 15-28%",
            "confidence": 0.78,
            "triangulation": 0.80,
            "studies": 6
        },
        {
            "rule": "Ceiling heights above 3.0m enhance creative problem-solving performance by 12-23%",
            "confidence": 0.71,
            "triangulation": 0.75,
            "studies": 5
        },
        {
            "rule": "Views of natural landscapes from workspace increase attention restoration by 20-35%",
            "confidence": 0.85,
            "triangulation": 0.88,
            "studies": 8
        },
        {
            "rule": "Acoustic comfort (noise <45 dB) improves concentration task performance by 14-27%",
            "confidence": 0.74,
            "triangulation": 0.77,
            "studies": 6
        },
        {
            "rule": "Warm color temperatures (2700-3000K) in evening environments improve sleep onset by 12-25 minutes",
            "confidence": 0.79,
            "triangulation": 0.82,
            "studies": 6
        },
        {
            "rule": "Access to outdoor spaces increases physical activity by 800-1500 steps per day",
            "confidence": 0.76,
            "triangulation": 0.80,
            "studies": 5
        },
        {
            "rule": "Natural ventilation (vs. mechanical) correlates with 22-38% reduction in sick building syndrome symptoms",
            "confidence": 0.81,
            "triangulation": 0.84,
            "studies": 7
        },
        {
            "rule": "Desk proximity to windows (<3m) associated with 15-20% improvement in self-reported wellbeing",
            "confidence": 0.73,
            "triangulation": 0.76,
            "studies": 5
        },
        {
            "rule": "Biophilic design elements (plants, water, natural materials) reduce physiological stress markers by 10-18%",
            "confidence": 0.77,
            "triangulation": 0.81,
            "studies": 6
        }
    ]
    
    for i, rule_data in enumerate(rules_data):
        rule_id = f"rule-{i+1}"
        
        cursor.execute("""
            INSERT INTO rules (
                rule_id, rule, confidence, triangulation_score, 
                contradiction_count, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rule_id,
            rule_data["rule"],
            rule_data["confidence"],
            rule_data["triangulation"],
            0,
            (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
        ))
        
        # Add evidence links (link to random supporting articles)
        num_evidence = rule_data["studies"]
        evidence_articles = random.sample(article_ids[:30], min(num_evidence, len(article_ids[:30])))
        
        for article_id in evidence_articles:
            cursor.execute("""
                INSERT INTO rule_evidence (
                    rule_id, article_id, passage, page_number, stance
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                rule_id,
                article_id,
                f"Supporting evidence for {rule_data['rule'][:50]}...",
                random.randint(5, 15),
                'supporting'
            ))
    
    conn.commit()
    print(f"✓ Generated {len(rules_data)} sample rules with evidence")

def generate_sample_jobs(conn):
    """Generate sample processing queue jobs"""
    cursor = conn.cursor()
    
    jobs = [
        # Completed jobs
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 86400000}",
            "job_type": "L0_harvest",
            "params": json.dumps({"query": "biophilic design in hospitals"}),
            "status": "complete",
            "priority": 100,
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "started_at": (datetime.now() - timedelta(days=1, hours=-0.1)).isoformat(),
            "completed_at": (datetime.now() - timedelta(days=1, hours=-0.05)).isoformat(),
            "error": None
        },
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 82800000}",
            "job_type": "L1_cluster",
            "params": json.dumps({"article_ids": list(range(1, 21))}),
            "status": "complete",
            "priority": 100,
            "created_at": (datetime.now() - timedelta(hours=23)).isoformat(),
            "started_at": (datetime.now() - timedelta(hours=22)).isoformat(),
            "completed_at": (datetime.now() - timedelta(hours=21)).isoformat(),
            "error": None
        },
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 79200000}",
            "job_type": "L2_extract",
            "params": json.dumps({"article_ids": list(range(1, 11))}),
            "status": "complete",
            "priority": 100,
            "created_at": (datetime.now() - timedelta(hours=22)).isoformat(),
            "started_at": (datetime.now() - timedelta(hours=21)).isoformat(),
            "completed_at": (datetime.now() - timedelta(hours=20)).isoformat(),
            "error": None
        },
        # Running job
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 600000}",
            "job_type": "L3_synthesize",
            "params": json.dumps({"finding_ids": list(range(1, 31))}),
            "status": "running",
            "priority": 100,
            "created_at": (datetime.now() - timedelta(minutes=10)).isoformat(),
            "started_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "completed_at": None,
            "error": None
        },
        # Pending jobs
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 300000}",
            "job_type": "L0_harvest",
            "params": json.dumps({"query": "natural light and productivity"}),
            "status": "pending",
            "priority": 90,
            "created_at": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None
        },
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 120000}",
            "job_type": "L0_harvest",
            "params": json.dumps({"query": "ceiling height and creativity"}),
            "status": "pending",
            "priority": 85,
            "created_at": (datetime.now() - timedelta(minutes=2)).isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None
        },
        # Failed job
        {
            "job_id": f"job-{int(datetime.now().timestamp() * 1000) - 43200000}",
            "job_type": "L2_extract",
            "params": json.dumps({"article_ids": [99]}),
            "status": "failed",
            "priority": 100,
            "created_at": (datetime.now() - timedelta(hours=12)).isoformat(),
            "started_at": (datetime.now() - timedelta(hours=11)).isoformat(),
            "completed_at": (datetime.now() - timedelta(hours=11, minutes=-5)).isoformat(),
            "error": "PDF extraction failed: File not found"
        }
    ]
    
    for job in jobs:
        cursor.execute("""
            INSERT INTO processing_queue (
                job_id, job_type, params, status, priority,
                created_at, started_at, completed_at, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job["job_id"], job["job_type"], job["params"], 
            job["status"], job["priority"],
            job["created_at"], job["started_at"], 
            job["completed_at"], job["error"]
        ))
    
    conn.commit()
    print(f"✓ Generated {len(jobs)} sample jobs")

def create_indexes(conn):
    """Create database indexes for performance"""
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_articles_doi ON articles(doi)",
        "CREATE INDEX IF NOT EXISTS idx_articles_year ON articles(year)",
        "CREATE INDEX IF NOT EXISTS idx_findings_paper ON findings(paper_id)",
        "CREATE INDEX IF NOT EXISTS idx_findings_consequent ON findings(consequent)",
        "CREATE INDEX IF NOT EXISTS idx_rule_evidence_rule ON rule_evidence(rule_id)",
        "CREATE INDEX IF NOT EXISTS idx_rule_evidence_article ON rule_evidence(article_id)",
        "CREATE INDEX IF NOT EXISTS idx_queue_status ON processing_queue(status)",
        "CREATE INDEX IF NOT EXISTS idx_queue_created ON processing_queue(created_at)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    conn.commit()
    print(f"✓ Created {len(indexes)} database indexes")

def main():
    """Initialize database with sample data"""
    print("\n" + "="*60)
    print("Article Eater - Database Initialization")
    print("="*60 + "\n")
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    print(f"Database: {DB_PATH}\n")
    
    # Create schema
    create_schema(conn)
    
    # Generate sample data
    article_ids = generate_sample_articles(conn, count=50)
    generate_sample_findings(conn, article_ids)
    generate_sample_rules(conn, article_ids)
    generate_sample_jobs(conn)
    
    # Create indexes
    create_indexes(conn)
    
    # Summary
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM articles")
    articles_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM findings")
    findings_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rules")
    rules_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM processing_queue")
    jobs_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "="*60)
    print("✓ Database Initialization Complete!")
    print("="*60)
    print(f"\nStatistics:")
    print(f"  Articles:  {articles_count}")
    print(f"  Findings:  {findings_count}")
    print(f"  Rules:     {rules_count}")
    print(f"  Jobs:      {jobs_count}")
    print(f"\nDatabase ready at: {DB_PATH}")
    print("\n")

if __name__ == "__main__":
    main()