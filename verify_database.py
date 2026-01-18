#!/usr/bin/env python3
"""
Visual Database Verification
Shows what's in the database in a nice format
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "ae.db"

# Colors
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(title):
    """Print section header"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{title}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_article(row):
    """Pretty print an article"""
    authors = json.loads(row['authors']) if row['authors'] else []
    author_str = ', '.join(authors[:2])
    if len(authors) > 2:
        author_str += f" et al. ({len(authors)} authors)"
    
    print(f"{CYAN}ID:{RESET} {row['article_id']}")
    print(f"{CYAN}Title:{RESET} {row['title'][:80]}...")
    print(f"{CYAN}Authors:{RESET} {author_str}")
    print(f"{CYAN}Year:{RESET} {row['year']} | {CYAN}Venue:{RESET} {row['venue']}")
    print(f"{CYAN}Citations:{RESET} {row['citation_count']} | {CYAN}Open Access:{RESET} {'Yes' if row['is_open_access'] else 'No'}")
    print(f"{CYAN}DOI:{RESET} {row['doi']}")
    print()

def print_finding(row):
    """Pretty print a finding"""
    antecedents = json.loads(row['antecedents']) if row['antecedents'] else []
    
    print(f"{CYAN}Consequent:{RESET} {row['consequent']}")
    print(f"{CYAN}Antecedents:{RESET} {', '.join(antecedents)}")
    print(f"{CYAN}Statistics:{RESET} p={row['p_value']}, d={row['effect_size']}, n={row['sample_size']}")
    print(f"{CYAN}Paper:{RESET} {row['paper_id']} (page {row['page_number']})")
    print(f"{CYAN}Measure:{RESET} {row['measure_type']} ({row['measure_direction']} effect)")
    print()

def print_rule(row):
    """Pretty print a rule"""
    print(f"{CYAN}Rule ID:{RESET} {row['rule_id']}")
    print(f"{CYAN}Rule:{RESET} {row['rule']}")
    print(f"{CYAN}Confidence:{RESET} {row['confidence']:.1%} | {CYAN}Triangulation:{RESET} {row['triangulation_score']:.1%}")
    print(f"{CYAN}Contradictions:{RESET} {row['contradiction_count']}")
    print()

def print_job(row):
    """Pretty print a job"""
    status_colors = {
        'pending': YELLOW,
        'running': CYAN,
        'complete': GREEN,
        'failed': '\033[91m'  # RED
    }
    
    color = status_colors.get(row['status'], RESET)
    
    print(f"{CYAN}Job ID:{RESET} {row['job_id'][:30]}...")
    print(f"{CYAN}Type:{RESET} {row['job_type']}")
    print(f"{CYAN}Status:{RESET} {color}{row['status'].upper()}{RESET}")
    print(f"{CYAN}Priority:{RESET} {row['priority']}")
    
    if row['error']:
        print(f"{CYAN}Error:{RESET} {row['error']}")
    
    print()

def main():
    """Show database contents"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Header
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}{BOLD}Article Eater Database Contents{RESET}")
    print(f"{GREEN}{'='*70}{RESET}")
    print(f"{CYAN}Database:{RESET} {DB_PATH}")
    print(f"{CYAN}Time:{RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary
    print_header("Summary Statistics")
    
    cursor.execute("SELECT COUNT(*) FROM articles")
    article_count = cursor.fetchone()[0]
    print(f"{GREEN}✓{RESET} Articles: {BOLD}{article_count}{RESET}")
    
    cursor.execute("SELECT COUNT(*) FROM findings")
    finding_count = cursor.fetchone()[0]
    print(f"{GREEN}✓{RESET} Findings: {BOLD}{finding_count}{RESET}")
    
    cursor.execute("SELECT COUNT(*) FROM rules")
    rule_count = cursor.fetchone()[0]
    print(f"{GREEN}✓{RESET} Rules: {BOLD}{rule_count}{RESET}")
    
    cursor.execute("SELECT COUNT(*) FROM processing_queue")
    job_count = cursor.fetchone()[0]
    print(f"{GREEN}✓{RESET} Jobs: {BOLD}{job_count}{RESET}")
    
    cursor.execute("SELECT COUNT(*) FROM rule_evidence")
    evidence_count = cursor.fetchone()[0]
    print(f"{GREEN}✓{RESET} Rule Evidence: {BOLD}{evidence_count}{RESET}")
    
    # Jobs by status
    print(f"\n{CYAN}Jobs by Status:{RESET}")
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM processing_queue 
        GROUP BY status
    """)
    for row in cursor.fetchall():
        print(f"  - {row['status']}: {row['count']}")
    
    # Sample Articles
    print_header("Sample Articles (5 of " + str(article_count) + ")")
    
    cursor.execute("""
        SELECT * FROM articles 
        ORDER BY citation_count DESC 
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{YELLOW}[{i}]{RESET}")
        print_article(row)
    
    # Sample Findings
    print_header("Sample Findings (5 of " + str(finding_count) + ")")
    
    cursor.execute("""
        SELECT * FROM findings 
        ORDER BY effect_size DESC 
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{YELLOW}[{i}]{RESET}")
        print_finding(row)
    
    # Sample Rules
    print_header("Sample Rules (5 of " + str(rule_count) + ")")
    
    cursor.execute("""
        SELECT * FROM rules 
        ORDER BY confidence DESC 
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{YELLOW}[{i}]{RESET}")
        print_rule(row)
        
        # Show evidence count for this rule
        cursor.execute("""
            SELECT COUNT(*) FROM rule_evidence WHERE rule_id = ?
        """, (row['rule_id'],))
        evidence_count = cursor.fetchone()[0]
        print(f"  {CYAN}→ Supported by {evidence_count} papers{RESET}\n")
    
    # Queue Status
    print_header("Processing Queue (All " + str(job_count) + " Jobs)")
    
    cursor.execute("""
        SELECT * FROM processing_queue 
        ORDER BY 
            CASE status
                WHEN 'running' THEN 1
                WHEN 'pending' THEN 2
                WHEN 'failed' THEN 3
                WHEN 'complete' THEN 4
            END,
            created_at DESC
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{YELLOW}[{i}]{RESET}")
        print_job(row)
    
    # Year distribution
    print_header("Publication Year Distribution")
    
    cursor.execute("""
        SELECT year, COUNT(*) as count 
        FROM articles 
        GROUP BY year 
        ORDER BY year DESC
    """)
    
    for row in cursor.fetchall():
        bar = '█' * (row['count'] // 2)
        print(f"{row['year']}: {bar} {row['count']}")
    
    # Top venues
    print_header("Top Publication Venues")
    
    cursor.execute("""
        SELECT venue, COUNT(*) as count 
        FROM articles 
        GROUP BY venue 
        ORDER BY count DESC 
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {row['venue']}: {row['count']} papers")
    
    # Measurement types
    print_header("Finding Measurement Types")
    
    cursor.execute("""
        SELECT measure_type, COUNT(*) as count 
        FROM findings 
        GROUP BY measure_type 
        ORDER BY count DESC
    """)
    
    for row in cursor.fetchall():
        bar = '█' * (row['count'] // 5)
        print(f"{row['measure_type']}: {bar} {row['count']}")
    
    # Footer
    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"{GREEN}✓ Database verification complete!{RESET}")
    print(f"{GREEN}{'='*70}{RESET}\n")
    
    conn.close()

if __name__ == "__main__":
    main()