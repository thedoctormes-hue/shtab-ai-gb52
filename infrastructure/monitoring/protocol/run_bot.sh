#!/bin/bash
set -a
source /root/LabDoctorM/protocol/.env
set +a
exec /root/LabDoctorM/venv/bin/python3 -m bot.main
