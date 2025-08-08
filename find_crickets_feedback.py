#!/usr/bin/env python3
"""
Find the record with crickets feedback
"""

from airtable_logger import AirtableLogger

def find_crickets_feedback():
    """Find the record with crickets feedback."""
    al = AirtableLogger()
    records = al.get_all_records()
    
    crickets_record = None
    for r in records:
        if 'Feedback' in r.get('fields', {}) and 'crickets' in r.get('fields', {}).get('Feedback', '').lower():
            crickets_record = r
            break
    
    print(f"Record with crickets feedback:")
    print(f"  ID: {crickets_record.get('id') if crickets_record else 'Not found'}")
    print(f"  Topic: {crickets_record.get('fields', {}).get('Topic', 'N/A') if crickets_record else 'N/A'}")
    print(f"  Feedback: \"{crickets_record.get('fields', {}).get('Feedback', 'N/A') if crickets_record else 'N/A'}\"")
    
    return crickets_record

if __name__ == "__main__":
    find_crickets_feedback() 