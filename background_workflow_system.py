#!/usr/bin/env python3
"""
Background Workflow System for LinkedIn Content
Runs the complete system in the background with 3 daily emails at 1-hour intervals
"""

import sys
import os
import time
import logging
import signal
import atexit
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_handler.email_scheduler import EmailScheduler
from final_integrated_system import FinalIntegratedSystem
from enhanced_feedback_processor import EnhancedFeedbackProcessor
from config.email_config import EmailSettings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackgroundWorkflowSystem:
    """Background workflow system that runs continuously."""
    
    def __init__(self):
        """Initialize the background workflow system."""
        self.email_scheduler = EmailScheduler()
        self.integrated_system = FinalIntegratedSystem()
        self.enhanced_feedback_processor = EnhancedFeedbackProcessor()
        self.running = False
        self.pid_file = "background_workflow.pid"
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Register cleanup function
        atexit.register(self._cleanup)
        
        logger.info("🚀 Background Workflow System initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def _cleanup(self):
        """Cleanup function called on exit."""
        if self.running:
            self.stop()
    
    def write_pid_file(self):
        """Write PID to file for process management."""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"📝 PID file written: {self.pid_file}")
        except Exception as e:
            logger.error(f"❌ Error writing PID file: {e}")
    
    def remove_pid_file(self):
        """Remove PID file."""
        try:
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
                logger.info(f"🗑️ PID file removed: {self.pid_file}")
        except Exception as e:
            logger.error(f"❌ Error removing PID file: {e}")
    
    def start(self):
        """Start the background workflow system."""
        try:
            logger.info("🚀 Starting Background Workflow System")
            logger.info("=" * 80)
            logger.info("📋 System Features:")
            logger.info("   📧 3 daily emails at 1-hour intervals (9 AM, 10 AM, 11 AM UK)")
            logger.info("   🔄 Continuous email monitoring")
            logger.info("   🧠 AI-powered content generation")
            logger.info("   📚 RAG-enhanced learning")
            logger.info("   🔄 Client feedback processing")
            logger.info("=" * 80)
            
            # Write PID file
            self.write_pid_file()
            
            # Start email scheduler
            logger.info("📅 Starting email scheduler...")
            self.email_scheduler.start_scheduler()
            
            # Mark as running
            self.running = True
            
            logger.info("✅ Background workflow system started successfully")
            logger.info("🔄 System is now running in background mode")
            logger.info("📧 Email schedule:")
            for i, time in enumerate(EmailSettings.SCHEDULE_TIMES, 1):
                logger.info(f"   Email {i}: {time} {EmailSettings.SCHEDULE_TIMEZONE}")
            logger.info("=" * 80)
            
            # Main background loop
            self._run_background_loop()
            
        except Exception as e:
            logger.error(f"❌ Error starting background system: {e}")
            self.stop()
            raise
    
    def _run_background_loop(self):
        """Main background processing loop."""
        cycle_count = 0
        email_check_interval = 60  # Check emails every 60 seconds for faster response
        feedback_check_interval = 300  # Check feedback every 5 minutes
        last_feedback_check = time.time()
        
        logger.info(f"🔄 Starting background processing loop")
        logger.info(f"   📧 Email check interval: {email_check_interval}s (fast response)")
        logger.info(f"   🔄 Feedback check interval: {feedback_check_interval}s (efficient)")
        
        while self.running:
            try:
                cycle_count += 1
                current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                
                logger.info(f"\n🔄 Background Cycle {cycle_count} - {current_time}")
                logger.info("-" * 60)
                
                # ALWAYS check for email replies (fast response)
                logger.info("📧 Checking for email replies...")
                email_replies = self.integrated_system.run_phase1_email_monitoring()
                
                if email_replies:
                    logger.info(f"📧 Found {len(email_replies)} new email replies - processing immediately!")
                    generated_posts = self.integrated_system.run_phase2_content_generation(email_replies)
                    logger.info(f"📝 Generated {len(generated_posts)} posts from {len(email_replies)} emails")
                else:
                    logger.info("📭 No new emails to process")
                
                # Check feedback processing less frequently (every 5 minutes)
                current_time_seconds = time.time()
                if current_time_seconds - last_feedback_check >= feedback_check_interval:
                    logger.info("🔄 Running enhanced feedback processing...")
                    self.enhanced_feedback_processor.run_enhanced_feedback_loop(hours_back=1)
                    
                    # Get processed feedback for reporting
                    posts_with_feedback = self.enhanced_feedback_processor.monitor_for_feedback(hours_back=1)
                    if posts_with_feedback:
                        logger.info(f"🔄 Enhanced feedback processed {len(posts_with_feedback)} items")
                    else:
                        logger.info("📭 No new feedback to process")
                    
                    last_feedback_check = current_time_seconds
                else:
                    logger.info("⏳ Skipping feedback check (not time yet)")
                
                # Print system status every 10 cycles
                if cycle_count % 10 == 0:
                    self.integrated_system.print_system_status()
                
                logger.info(f"⏳ Waiting {email_check_interval} seconds before next email check...")
                time.sleep(email_check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Background loop interrupted")
                break
            except Exception as e:
                logger.error(f"❌ Error in background loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def stop(self):
        """Stop the background workflow system."""
        try:
            logger.info("🛑 Stopping Background Workflow System...")
            
            # Mark as not running
            self.running = False
            
            # Stop email scheduler
            if hasattr(self, 'email_scheduler'):
                self.email_scheduler.stop_scheduler()
                logger.info("📧 Email scheduler stopped")
            
            # Remove PID file
            self.remove_pid_file()
            
            logger.info("✅ Background workflow system stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping background system: {e}")
    
    def get_status(self):
        """Get current system status."""
        try:
            status = {
                "running": self.running,
                "pid": os.getpid() if self.running else None,
                "pid_file_exists": os.path.exists(self.pid_file),
                "email_scheduler_status": self.email_scheduler.get_scheduler_status(),
                "current_time": datetime.now(timezone.utc).isoformat()
            }
            return status
        except Exception as e:
            logger.error(f"❌ Error getting status: {e}")
            return {"running": False, "error": str(e)}

def check_if_running():
    """Check if background workflow is already running."""
    pid_file = "background_workflow.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            try:
                os.kill(pid, 0)  # Send signal 0 to check if process exists
                return True, pid
            except OSError:
                # Process not running, remove stale PID file
                os.remove(pid_file)
                return False, None
        except Exception:
            return False, None
    return False, None

def main():
    """Main function to run the background workflow system."""
    
    print("🚀 Background Workflow System for LinkedIn Content")
    print("=" * 80)
    print(f"👤 Client: {EmailSettings.CLIENT_NAME}")
    print(f"📧 Client Email: {EmailSettings.TO_EMAIL}")
    print("=" * 80)
    print("📧 Email Schedule:")
    for i, time in enumerate(EmailSettings.SCHEDULE_TIMES, 1):
        print(f"   Email {i}: {time} {EmailSettings.SCHEDULE_TIMEZONE}")
    print("=" * 80)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            # Check if already running
            is_running, pid = check_if_running()
            if is_running:
                print(f"❌ Background workflow is already running (PID: {pid})")
                print("💡 Use 'python3 background_workflow_system.py stop' to stop it first")
                return
            
            # Start the system
            system = BackgroundWorkflowSystem()
            system.start()
            
        elif command == "stop":
            # Check if running
            is_running, pid = check_if_running()
            if not is_running:
                print("❌ Background workflow is not running")
                return
            
            # Stop the system
            try:
                os.kill(pid, signal.SIGTERM)
                print(f"📡 Sent stop signal to process {pid}")
                print("⏳ Waiting for graceful shutdown...")
                time.sleep(3)
                
                # Check if still running
                is_running, _ = check_if_running()
                if is_running:
                    print("⚠️ Process didn't stop gracefully, forcing termination...")
                    os.kill(pid, signal.SIGKILL)
                
                print("✅ Background workflow stopped")
                
            except Exception as e:
                print(f"❌ Error stopping background workflow: {e}")
        
        elif command == "status":
            # Get status
            is_running, pid = check_if_running()
            if is_running:
                print(f"✅ Background workflow is running (PID: {pid})")
                
                # Try to get detailed status
                try:
                    system = BackgroundWorkflowSystem()
                    status = system.get_status()
                    print(f"📧 Email scheduler: {'Running' if status.get('email_scheduler_status', {}).get('scheduler_running') else 'Stopped'}")
                    print(f"🕐 Current time: {status.get('current_time', 'Unknown')}")
                except Exception as e:
                    print(f"⚠️ Could not get detailed status: {e}")
            else:
                print("❌ Background workflow is not running")
        
        elif command == "restart":
            # Restart the system
            print("🔄 Restarting background workflow...")
            
            # Stop if running
            is_running, pid = check_if_running()
            if is_running:
                try:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(3)
                    print("✅ Stopped existing process")
                except Exception as e:
                    print(f"⚠️ Error stopping existing process: {e}")
            
            # Start new process
            system = BackgroundWorkflowSystem()
            system.start()
        
        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Available commands: start, stop, status, restart")
    
    else:
        # No command specified, show help
        print("💡 Usage:")
        print("   python3 background_workflow_system.py start    - Start background workflow")
        print("   python3 background_workflow_system.py stop     - Stop background workflow")
        print("   python3 background_workflow_system.py status   - Check status")
        print("   python3 background_workflow_system.py restart  - Restart background workflow")
        print("=" * 80)
        print("📋 System will:")
        print("   📧 Send 3 daily emails at 1-hour intervals")
        print("   🔄 Monitor for email replies continuously")
        print("   🧠 Generate LinkedIn content automatically")
        print("   📚 Learn from feedback using RAG")
        print("   🔄 Process client feedback continuously")

if __name__ == "__main__":
    main() 