import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib.util
import os
import sys

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import from the root config.py file
spec = importlib.util.spec_from_file_location("config", os.path.join(project_root, "config.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)
RESEND_API_KEY = config.RESEND_API_KEY
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import time
import pytz

def send_topic_prompt_email(client_email: str = "vaishnavisingh24011@gmail.com"):
    """
    Send a topic prompt email using the existing email handler pattern.
    """
    try:
        data = {
            "from": "Empowrd Agent <vaishnavis@valixio.site>",
            "to": [client_email],
            "subject": "Got a topic in mind for today's post?",
            "html": """
                <p>Hey! 👋</p>
                <p>Do you have a specific topic you'd like us to write about today?</p>
                <p>Reply with "Yes + your topic" or just "No" and we'll handle it.</p>
                <p>Best regards,<br>Your LinkedIn Content Team</p>
            """
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json=data
        )

        print(f"📧 Email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📧 Email status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Topic prompt email sent to {client_email}")
            return True
        else:
            print(f"❌ Error sending email: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error sending topic prompt email: {e}")
        return False

def start_email_scheduler(client_email: str = "vaishnavisingh24011@gmail.com", time: str = "09:00"):
    """
    Start the email scheduler to send daily topic prompts.
    
    Args:
        client_email: The client's email address
        time: Time to send the email (format: "HH:MM")
    """
    try:
        # Parse time
        hour, minute = map(int, time.split(':'))
        
        # Create scheduler
        scheduler = BlockingScheduler()
        
        # Add daily job with UK timezone
        uk_tz = pytz.timezone('Europe/London')
        scheduler.add_job(
            func=send_topic_prompt_email,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=uk_tz),
            args=[client_email],
            id='daily_topic_prompt',
            name='Send daily topic prompt email',
            replace_existing=True
        )
        
        print(f"📅 Email scheduler started!")
        print(f"📅 Will send topic prompts to {client_email} daily at {time} UK time")
        
        # Get next run time safely
        try:
            job = scheduler.get_job('daily_topic_prompt')
            if job and hasattr(job, 'next_run_time') and job.next_run_time:
                print(f"📅 Next run: {job.next_run_time}")
            else:
                print("📅 Next run: Will be calculated automatically")
        except Exception as e:
            print("📅 Next run: Will be calculated automatically")
            
        print("🔄 Scheduler is running... Press Ctrl+C to stop")
        
        # Start the scheduler
        scheduler.start()
        
    except Exception as e:
        print(f"❌ Error starting email scheduler: {e}")
        return False

def send_manual_topic_prompt(client_email: str = "vaishnavisingh24011@gmail.com"):
    """
    Send a manual topic prompt email (for testing or immediate sending).
    """
    print(f"📧 Sending manual topic prompt to {client_email}...")
    return send_topic_prompt_email(client_email)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Scheduler for LinkedIn Topic Prompts')
    parser.add_argument('--action', choices=['send', 'schedule'], default='send',
                       help='Action to perform: send (manual) or schedule (automatic)')
    parser.add_argument('--email', default='vaishnavisingh24011@gmail.com',
                       help='Client email address')
    parser.add_argument('--time', default='09:00',
                       help='Time to send emails (format: HH:MM)')
    
    args = parser.parse_args()
    
    if args.action == 'send':
        send_manual_topic_prompt(args.email)
    elif args.action == 'schedule':
        start_email_scheduler(args.email, args.time)