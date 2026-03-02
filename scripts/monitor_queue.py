#!/usr/bin/env python3
"""
Queue Monitor
=============

Continuously monitors the PDF extraction queue and prints
a nicely formatted status table every few seconds.

USAGE:
    python scripts/monitor_queue.py
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime

QUEUE_FILE = Path("data/extraction_pipeline/extraction_queue.json")
CLAIMS_FILE = Path("data/extraction_pipeline/work_claims.json")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_stats():
    stats = {}
    total_cost = 0.0
    extraction_times = []
    
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE) as f:
                data = json.load(f)
                stats = data.get("stats", {})
                
                # Parse running cost and time from all items
                items = data.get("items", {})
                for item in items.values():
                    # Accumulate cost (whether accepted or failed)
                    if "total_cost" in item:
                        total_cost += item.get("total_cost", 0.0)
                        
                    # Accumulate time (only on successes to avoid skewed math from instant API failures)
                    result = item.get("extraction_result")
                    if isinstance(result, dict) and "extraction_time" in result:
                        extraction_times.append(result.get("extraction_time", 0.0))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
            
    active_claims = 0
    if CLAIMS_FILE.exists():
        try:
            with open(CLAIMS_FILE) as f:
                data = json.load(f)
                active_claims = len(data.get("claims", {}))
        except Exception as e:
            import logging; logging.getLogger(__name__).debug(f"Non-critical: {e}")
            
    mean_time = sum(extraction_times) / len(extraction_times) if extraction_times else 0.0
    return stats, active_claims, total_cost, mean_time

def print_table():
    stats, active_claims, total_cost, mean_time = get_stats()
    
    total = stats.get("total", 0)
    pending = stats.get("pending", 0)
    accepted = stats.get("accepted", 0)
    requeued = stats.get("requeued", 0)
    failed = stats.get("failed", 0)
    
    # Calculate derived metrics
    completed = accepted + failed
    processing = total - pending - completed
    
    clear_screen()
    print(f"=== PDF EXTRACTION LIVE MONITOR ===")
    print(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'-'*60}")
    print(f"{'Metric':<25} | {'Value':<15} | {'Description'}")
    print(f"{'-'*60}")
    print(f"{'Total In Queue':<25} | {total:<15} | Total PDFs discovered")
    print(f"{'Currently Claimed':<25} | {active_claims:<15} | Locked by active agents")
    print(f"{'Actively Processing':<25} | {processing:<15} | Claimed but not finished")
    print(f"{'Successfully Accepted':<25} | {accepted:<15} | Ready for integration")
    print(f"{'Failed / Needs Review':<25} | {failed:<15} | Unrecoverable errors")
    print(f"{'Requeued (Retrying)':<25} | {requeued:<15} | Hit an error, will retry")
    print(f"{'Remaining Pending':<25} | {pending:<15} | Waiting to be claimed")
    print(f"{'-'*60}")
    print(f"{'Total API Cost':<25} | ${total_cost:<14.2f} | Accumulated Gemini spend")
    print(f"{'Mean Extraction Time':<25} | {mean_time:<11.1f} sec | Avg time per success")
    print(f"{'-'*60}")
    
    if total > 0:
        pct = (completed / total) * 100
        print(f"Overall Progress: {pct:.1f}%")
        
        # Simple progress bar
        bar_len = 40
        filled = int(bar_len * (completed / total))
        bar = '█' * filled + '-' * (bar_len - filled)
        print(f"[{bar}]")

def main():
    print("Starting monitor... (Press Ctrl+C to exit)")
    try:
        while True:
            print_table()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")

if __name__ == "__main__":
    main()
