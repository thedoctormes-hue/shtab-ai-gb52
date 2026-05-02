#!/usr/bin/env python3
import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ZavLabVibecodingMCP")

LAB_ROOT = "/root/LabDoctorM"
QWEN_MEMORY = "/root/.qwen/projects/-root-LabDoctorM/memory"
SKILLS_DIR = "/root/.qwen/skills"
RULES_FILE = "/root/.qwen/rules.md"


@mcp.tool()
def list_qwen_files():
    """List all QWEN.md files in LabDoctorM projects"""
    qwen_files = []
    for root, dirs, files in os.walk(LAB_ROOT):
        if "QWEN.md" in files:
            qwen_files.append(os.path.join(root, "QWEN.md"))
    return str(qwen_files)


@mcp.tool()
def read_qwen_file(file_path: str):
    """Read content of a QWEN.md file. Only allow paths in LabDoctorM."""
    if not file_path.startswith(LAB_ROOT):
        return "Error: Only files in LabDoctorM are allowed"
    if not os.path.exists(file_path):
        return "Error: File not found"
    with open(file_path, "r") as f:
        return f.read()


@mcp.tool()
def list_skills():
    """List all available user skills"""
    if not os.path.exists(SKILLS_DIR):
        return "[]"
    skills = []
    for f in os.listdir(SKILLS_DIR):
        if f.endswith(".md") or f.endswith(".skill"):
            skills.append(f)
    return str(skills)


@mcp.tool()
def read_memory_files():
    """List all memory files in ZavLab memory directory"""
    if not os.path.exists(QWEN_MEMORY):
        return "[]"
    files = [f for f in os.listdir(QWEN_MEMORY) if f.endswith(".md")]
    return str(files)


@mcp.tool()
def get_deploy_history(service_name: str = ""):
    """Get systemd deploy history for a service. If empty, list all lab services."""
    if service_name:
        cmd = f"journalctl -u {service_name} --no-pager -n 20"
    else:
        cmd = "ls /etc/systemd/system/ | grep -E '(mskgastrodigestbot|aiderdm|hrdamon|vpndaemon|stenographer|maildaemon)'"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def read_rules():
    """Read global rules from ~/.qwen/rules.md"""
    if not os.path.exists(RULES_FILE):
        return "Rules file not found"
    with open(RULES_FILE, "r") as f:
        return f.read()


if __name__ == "__main__":
    mcp.run()
