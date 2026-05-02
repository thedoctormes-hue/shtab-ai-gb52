import asyncio
import sys
import os
sys.path.insert(0, '/root/LabDoctorM/VPNDaemonRobot')

# Run the main bot from bot/main.py
from bot.main import main, dp, bot

if __name__ == "__main__":
    asyncio.run(main())