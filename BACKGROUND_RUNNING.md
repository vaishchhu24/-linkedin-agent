# 🚀 Running LinkedIn Agent in Background

This guide shows you how to run the LinkedIn content generation system continuously in the background.

## 📋 Quick Start (Recommended)

### 1. Start the System
```bash
./run_background.sh
```

### 2. Check Status
```bash
./check_status.sh
```

### 3. Monitor Logs
```bash
tail -f logs/linkedin_agent_*.log
```

### 4. Stop the System
```bash
./stop_background.sh
```

## 🔧 Background Running Options

### Option 1: Simple Background Script (Recommended)
- **Best for**: Development and testing
- **Pros**: Easy to start/stop, good logging
- **Cons**: Stops when you log out (unless using nohup)

```bash
# Start
./run_background.sh

# Check status
./check_status.sh

# Stop
./stop_background.sh
```

### Option 2: macOS LaunchDaemon (Permanent)
- **Best for**: Production on macOS
- **Pros**: Starts automatically on boot, survives reboots
- **Cons**: More complex setup

```bash
# Copy plist to LaunchDaemons
sudo cp com.linkedin.agent.plist /Library/LaunchDaemons/

# Load the service
sudo launchctl load /Library/LaunchDaemons/com.linkedin.agent.plist

# Start the service
sudo launchctl start com.linkedin.agent

# Check status
sudo launchctl list | grep linkedin

# Stop the service
sudo launchctl stop com.linkedin.agent

# Unload the service
sudo launchctl unload /Library/LaunchDaemons/com.linkedin.agent.plist
```

### Option 3: Linux SystemD Service (Permanent)
- **Best for**: Production on Linux servers
- **Pros**: Starts automatically on boot, survives reboots
- **Cons**: Linux only

```bash
# Copy service file
sudo cp linkedin-agent.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable linkedin-agent

# Start service
sudo systemctl start linkedin-agent

# Check status
sudo systemctl status linkedin-agent

# View logs
sudo journalctl -u linkedin-agent -f

# Stop service
sudo systemctl stop linkedin-agent
```

### Option 4: Screen/Tmux (Development)
- **Best for**: Development and testing
- **Pros**: Can attach/detach, survives disconnections
- **Cons**: Manual management

```bash
# Using screen
screen -S linkedin-agent
python3 final_integrated_system.py
# Press Ctrl+A, then D to detach

# Reattach
screen -r linkedin-agent

# Using tmux
tmux new-session -d -s linkedin-agent 'python3 final_integrated_system.py'

# Attach
tmux attach-session -t linkedin-agent

# Detach: Ctrl+B, then D
```

## 📊 Monitoring and Management

### Check System Status
```bash
./check_status.sh
```

### Monitor Logs
```bash
# Real-time logs
tail -f logs/linkedin_agent_*.log

# Last 50 lines
tail -50 logs/linkedin_agent_*.log

# Search for errors
grep "ERROR" logs/linkedin_agent_*.log
```

### System Information
```bash
# Check if process is running
ps aux | grep final_integrated_system

# Check memory usage
ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep final_integrated_system

# Check disk usage
du -sh logs/
```

## 🔍 Troubleshooting

### Common Issues

1. **Process not starting**
   ```bash
   # Check Python path
   which python3
   
   # Check dependencies
   pip3 list | grep openai
   ```

2. **Permission denied**
   ```bash
   # Make scripts executable
   chmod +x *.sh
   ```

3. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :587  # For SMTP
   ```

4. **Log files not created**
   ```bash
   # Create logs directory
   mkdir -p logs
   
   # Check permissions
   ls -la logs/
   ```

### Restart the System
```bash
# Stop
./stop_background.sh

# Wait a moment
sleep 5

# Start
./run_background.sh
```

## 📈 Performance Monitoring

### Memory Usage
```bash
# Monitor memory usage
watch -n 5 'ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem | grep final_integrated_system'
```

### Log Rotation
```bash
# Archive old logs (run daily via cron)
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
```

## 🎯 What the System Does in Background

When running in background, the system:

1. **📧 Sends daily emails** at 10 AM UK time
2. **🔍 Monitors for replies** every 5 minutes
3. **📝 Generates LinkedIn posts** when replies are received
4. **🔄 Processes feedback** and revises posts
5. **📚 Learns from approved posts** only
6. **📊 Logs all activity** to timestamped files

## 🚨 Important Notes

- **Backup your data**: The system stores data in `data/` directory
- **Monitor logs**: Check logs regularly for errors
- **Test first**: Run in foreground first to ensure everything works
- **API limits**: Monitor OpenAI API usage
- **Email limits**: Be aware of email sending limits

## 📞 Support

If you encounter issues:

1. Check the logs: `tail -f logs/linkedin_agent_*.log`
2. Check system status: `./check_status.sh`
3. Restart the system: `./stop_background.sh && ./run_background.sh`
4. Check dependencies: `pip3 list | grep -E "(openai|langchain)"` 