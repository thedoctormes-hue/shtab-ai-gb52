import subprocess
result = subprocess.run(["journalctl", "-u", "protocol-bot.service", "-n", "30", "--no-pager"], capture_output=True, text=True)
with open("/root/protocol/logs_output.txt", "w") as f:
    f.write(result.stdout)
    f.write(result.stderr)