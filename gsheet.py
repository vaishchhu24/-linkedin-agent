import importlib.util
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
CREDS_JSON = config.CREDS_JSON
SPREADSHEET_ID = config.SPREADSHEET_ID
SHEET_NAME = config.SHEET_NAME

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

def test_gsheet_connection():
    """Test function to verify Google Sheets connection and capabilities"""
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        
        # Test reading the sheet
        request = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1:C10"
        )
        response = request.execute()
        
        print("✅ Google Sheets connection successful!")
        print(f"   Sheet: {SHEET_NAME}")
        print(f"   Current data rows: {len(response.get('values', []))}")
        
        # Test writing a long string
        test_long_text = "This is a test of a very long string. " * 50  # ~2000 characters
        test_row = [[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "TEST", test_long_text]]
        
        write_request = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": test_row},
        )
        write_response = write_request.execute()
        
        # Read back what was actually saved
        read_request = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!C{write_response.get('updates', {}).get('updatedRows', 1)}"
        )
        saved_test = read_request.execute()
        
        if saved_test.get('values'):
            saved_length = len(saved_test['values'][0][0])
            original_length = len(test_long_text)
            print(f"   Test write successful!")
            print(f"   Original length: {original_length} characters")
            print(f"   Saved length: {saved_length} characters")
            print(f"   Truncation: {original_length - saved_length} characters lost")
            
            if saved_length >= original_length * 0.95:
                print("   ✅ No significant truncation detected")
            else:
                print("   ⚠️ Significant truncation detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Sheets test failed: {e}")
        return False

def write_post_to_gsheet(topic, post):
    try:
        # Setup
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(CREDS_JSON, scopes=scope)
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        # Format current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Debug: Print what we're about to save
        print(f"📝 Saving to Google Sheets:")
        print(f"   Timestamp: {timestamp}")
        print(f"   Topic: {topic}")
        print(f"   Post length: {len(post)} characters")
        print(f"   Full post content:")
        print(f"   {'='*50}")
        print(post)
        print(f"   {'='*50}")

        # Method 1: Try to save as single cell first
        try:
            row = [[timestamp, topic, post]]
            
            request = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row},
            )
            response = request.execute()
            
            # Verify the saved content by reading it back
            read_request = sheet.values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!C{response.get('updates', {}).get('updatedRows', 1)}"
            )
            saved_content = read_request.execute()
            
            if saved_content.get('values') and len(saved_content['values'][0][0]) >= len(post) * 0.9:  # Allow 10% tolerance
                print(f"✅ Full post saved successfully in single cell!")
                print(f"   Saved length: {len(saved_content['values'][0][0])} characters")
                return True
            else:
                print(f"⚠️ Post may have been truncated. Trying alternative method...")
                raise Exception("Content truncated")
                
        except Exception as e:
            print(f"🔄 Trying alternative method due to: {e}")
            
            # Method 2: Split long posts into multiple cells
            # Split post into chunks of ~500 characters
            chunk_size = 500
            post_chunks = [post[i:i+chunk_size] for i in range(0, len(post), chunk_size)]
            
            # Create row with timestamp, topic, and multiple post chunks
            row_data = [timestamp, topic]
            row_data.extend(post_chunks)
            
            # Also add a full post column at the end
            row_data.append(post)
            
            row = [row_data]
            
            request = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!A1",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row},
            )
            response = request.execute()
            
            print(f"✅ Post saved using chunked method!")
            print(f"   Split into {len(post_chunks)} chunks")
            print(f"   Full post also saved in last column")
            return True
        
    except Exception as e:
        print(f"❌ Error saving to Google Sheets: {e}")
        print(f"   Post content length: {len(post) if post else 0}")
        print(f"   Topic: {topic}")
        return False

# Test function call
if __name__ == "__main__":
    test_gsheet_connection()
