#!/usr/bin/env python3
"""
CSV to RAG Importer
Import posts from CSV file into RAG store
"""

import sys
import os
import csv
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_memory import RAGMemory
from config.email_config import EmailSettings

def detect_csv_columns(csv_file: str) -> Dict[str, str]:
    """Detect and map CSV columns to RAG fields."""
    try:
        # Read first few rows to detect columns
        df = pd.read_csv(csv_file, nrows=5)
        columns = df.columns.tolist()
        
        print("📋 Detected CSV columns:")
        for i, col in enumerate(columns, 1):
            print(f"   {i}. {col}")
        
        # Auto-detect common column names
        column_mapping = {}
        
        # Topic mapping
        topic_candidates = ['topic', 'title', 'subject', 'theme', 'category']
        for candidate in topic_candidates:
            if candidate in columns:
                column_mapping['topic'] = candidate
                break
        
        # Post content mapping
        content_candidates = ['post', 'content', 'text', 'body', 'message', 'description']
        for candidate in content_candidates:
            if candidate in columns:
                column_mapping['post'] = candidate
                break
        
        # Quality scores mapping
        voice_candidates = ['voice_quality', 'voice', 'tone_quality', 'voice_score']
        for candidate in voice_candidates:
            if candidate in columns:
                column_mapping['voice_quality'] = candidate
                break
        
        post_quality_candidates = ['post_quality', 'quality', 'post_score', 'content_quality']
        for candidate in post_quality_candidates:
            if candidate in columns:
                column_mapping['post_quality'] = candidate
                break
        
        # Feedback mapping
        feedback_candidates = ['feedback', 'status', 'approved', 'response']
        for candidate in feedback_candidates:
            if candidate in columns:
                column_mapping['feedback'] = candidate
                break
        
        print("\n🎯 Auto-detected column mapping:")
        for rag_field, csv_column in column_mapping.items():
            print(f"   {rag_field} → {csv_column}")
        
        # Ask user to confirm or modify mapping
        print("\n❓ Do you want to modify the column mapping? (y/n): ", end="")
        modify = input().strip().lower()
        
        if modify == 'y':
            column_mapping = manual_column_mapping(columns)
        
        return column_mapping
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return {}

def manual_column_mapping(columns: List[str]) -> Dict[str, str]:
    """Manual column mapping."""
    print("\n📝 Manual Column Mapping")
    print("Enter the column number for each RAG field (or press Enter to skip):")
    
    mapping = {}
    
    # Topic
    print(f"\nTopic column (required):")
    for i, col in enumerate(columns, 1):
        print(f"   {i}. {col}")
    topic_choice = input("Enter number: ").strip()
    if topic_choice.isdigit() and 1 <= int(topic_choice) <= len(columns):
        mapping['topic'] = columns[int(topic_choice) - 1]
    
    # Post content
    print(f"\nPost content column (required):")
    for i, col in enumerate(columns, 1):
        print(f"   {i}. {col}")
    content_choice = input("Enter number: ").strip()
    if content_choice.isdigit() and 1 <= int(content_choice) <= len(columns):
        mapping['post'] = columns[int(content_choice) - 1]
    
    # Voice quality
    print(f"\nVoice quality column (optional):")
    for i, col in enumerate(columns, 1):
        print(f"   {i}. {col}")
    voice_choice = input("Enter number (or press Enter to skip): ").strip()
    if voice_choice.isdigit() and 1 <= int(voice_choice) <= len(columns):
        mapping['voice_quality'] = columns[int(voice_choice) - 1]
    
    # Post quality
    print(f"\nPost quality column (optional):")
    for i, col in enumerate(columns, 1):
        print(f"   {i}. {col}")
    quality_choice = input("Enter number (or press Enter to skip): ").strip()
    if quality_choice.isdigit() and 1 <= int(quality_choice) <= len(columns):
        mapping['post_quality'] = columns[int(quality_choice) - 1]
    
    # Feedback
    print(f"\nFeedback column (optional):")
    for i, col in enumerate(columns, 1):
        print(f"   {i}. {col}")
    feedback_choice = input("Enter number (or press Enter to skip): ").strip()
    if feedback_choice.isdigit() and 1 <= int(feedback_choice) <= len(columns):
        mapping['feedback'] = columns[int(feedback_choice) - 1]
    
    return mapping

def import_csv_to_rag(csv_file: str, column_mapping: Dict[str, str], filter_approved: bool = True):
    """Import posts from CSV to RAG store."""
    try:
        print(f"\n📚 Importing posts from: {csv_file}")
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        print(f"📋 Found {len(df)} rows in CSV")
        
        # Validate required columns
        if 'topic' not in column_mapping or 'post' not in column_mapping:
            print("❌ Error: topic and post columns are required")
            return False
        
        # Filter approved posts if requested
        if filter_approved and 'feedback' in column_mapping:
            approval_keywords = ['yes', 'approved', 'like', 'love', 'great', 'perfect']
            df_filtered = df[df[column_mapping['feedback']].str.lower().isin(approval_keywords)]
            print(f"✅ Filtered to {len(df_filtered)} approved posts")
        else:
            df_filtered = df
            print(f"📝 Using all {len(df_filtered)} posts")
        
        if len(df_filtered) == 0:
            print("❌ No posts to import after filtering")
            return False
        
        # Initialize RAG memory
        rag_memory = RAGMemory()
        success_count = 0
        error_count = 0
        
        print(f"\n🔄 Importing posts...")
        
        for index, row in df_filtered.iterrows():
            try:
                # Extract data from CSV
                topic = str(row[column_mapping['topic']]).strip()
                post_content = str(row[column_mapping['post']]).strip()
                
                if not topic or not post_content or topic == 'nan' or post_content == 'nan':
                    print(f"⚠️  Skipping row {index + 1}: empty topic or content")
                    error_count += 1
                    continue
                
                # Extract optional fields
                voice_quality = 8  # default
                if 'voice_quality' in column_mapping:
                    try:
                        voice_quality = int(float(row[column_mapping['voice_quality']]))
                    except:
                        voice_quality = 8
                
                post_quality = 8  # default
                if 'post_quality' in column_mapping:
                    try:
                        post_quality = int(float(row[column_mapping['post_quality']]))
                    except:
                        post_quality = 8
                
                feedback = "yes"  # default
                if 'feedback' in column_mapping:
                    feedback = str(row[column_mapping['feedback']]).strip()
                    if feedback == 'nan':
                        feedback = "yes"
                
                # Create post data
                post_data = {
                    "topic": topic,
                    "post": post_content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "client_id": EmailSettings.CLIENT_EMAIL.split('@')[0],
                    "feedback": feedback,
                    "voice_quality": voice_quality,
                    "post_quality": post_quality,
                    "post_hash": f"csv_{index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
                
                # Add to RAG
                if rag_memory.add_post(post_data):
                    success_count += 1
                    print(f"✅ Added: {topic[:50]}...")
                else:
                    error_count += 1
                    print(f"❌ Failed to add: {topic[:50]}...")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error processing row {index + 1}: {e}")
        
        print(f"\n📊 Import Summary:")
        print(f"   ✅ Successfully imported: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📚 Total posts in RAG: {rag_memory.get_stats()['total_posts']}")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        return False

def create_sample_csv():
    """Create a sample CSV file for reference."""
    sample_data = [
        {
            'topic': 'HR consultant pricing strategies',
            'post': 'Just had a client ask me about pricing their HR consulting services. Here\'s what I told them:\n\n1. Start with your value, not your costs\n2. Price based on outcomes, not hours\n3. Don\'t compete on price - compete on results\n\nWhen you focus on the transformation you deliver, clients will pay premium rates.\n\nWhat\'s your pricing strategy?',
            'voice_quality': 9,
            'post_quality': 9,
            'feedback': 'yes'
        },
        {
            'topic': 'Client acquisition for HR consultants',
            'post': 'The biggest mistake I see HR consultants make?\n\nTrying to be everything to everyone.\n\nInstead, focus on ONE specific problem you solve exceptionally well.\n\nFor me, it\'s helping HR consultants build systems that scale.\n\nWhen you niche down, you become the go-to expert.\n\nWhat\'s your specific niche?',
            'voice_quality': 8,
            'post_quality': 9,
            'feedback': 'approved'
        },
        {
            'topic': 'Building systems for HR consulting business',
            'post': 'Your HR consulting business will never scale if you\'re the system.\n\nI learned this the hard way.\n\nNow I have:\n- Standardized processes for every client\n- Templates for common deliverables\n- Automated follow-up sequences\n- Clear onboarding procedures\n\nSystems = Freedom\n\nWhat systems do you need to build?',
            'voice_quality': 9,
            'post_quality': 8,
            'feedback': 'yes'
        }
    ]
    
    filename = "sample_posts.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['topic', 'post', 'voice_quality', 'post_quality', 'feedback'])
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"✅ Created sample CSV file: {filename}")
    print("📝 You can use this as a template for your own CSV file")

def main():
    """Main function."""
    print("📚 CSV to RAG Importer")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Command line mode
        csv_file = sys.argv[1]
        if not os.path.exists(csv_file):
            print(f"❌ File not found: {csv_file}")
            sys.exit(1)
        
        # Auto-detect columns
        column_mapping = detect_csv_columns(csv_file)
        if not column_mapping:
            sys.exit(1)
        
        # Import
        filter_approved = input("Filter to approved posts only? (y/n): ").strip().lower() == 'y'
        success = import_csv_to_rag(csv_file, column_mapping, filter_approved)
        
        if success:
            print("✅ Import completed successfully!")
        else:
            print("❌ Import failed")
            sys.exit(1)
    
    else:
        # Interactive mode
        while True:
            print("\n" + "=" * 50)
            print("📚 CSV to RAG Importer")
            print("=" * 50)
            print("1. Import CSV file")
            print("2. Create sample CSV file")
            print("3. Show RAG statistics")
            print("4. Exit")
            print("=" * 50)
            
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                csv_file = input("Enter CSV file path: ").strip()
                if not os.path.exists(csv_file):
                    print(f"❌ File not found: {csv_file}")
                    continue
                
                # Auto-detect columns
                column_mapping = detect_csv_columns(csv_file)
                if not column_mapping:
                    continue
                
                # Import
                filter_approved = input("Filter to approved posts only? (y/n): ").strip().lower() == 'y'
                success = import_csv_to_rag(csv_file, column_mapping, filter_approved)
                
                if success:
                    print("✅ Import completed successfully!")
                else:
                    print("❌ Import failed")
            
            elif choice == "2":
                create_sample_csv()
            
            elif choice == "3":
                rag_memory = RAGMemory()
                stats = rag_memory.get_stats()
                print(f"\n📊 RAG Statistics:")
                print(f"   Total posts: {stats.get('total_posts', 0)}")
                print(f"   Average quality: {stats.get('avg_post_quality', 0)}/10")
            
            elif choice == "4":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-4.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 