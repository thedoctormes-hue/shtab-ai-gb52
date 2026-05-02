import subprocess
result = subprocess.run(["python3", "/root/LabDoctorM/protocol/clean_db.py"], capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)