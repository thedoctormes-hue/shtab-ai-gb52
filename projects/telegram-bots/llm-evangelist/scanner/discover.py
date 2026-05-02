#!/usr/bin/env python3
"""Scanner для обнаружения LLM проектов в лаборатории."""

import json
import os
import re
from pathlib import Path

LAB_ROOT = Path("/root/LabDoctorM")
EXCLUDE_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".qwen", "tmp", "temp", "logs", "log"}

LLM_PATTERNS = [
    (r'["\'](?:google/|mistralai/|anthropic/|deepseek/|openai/|x-ai/)[^"\']+["\']', "model_string"),
    (r'"model":\s*["\']([^"\']+)["\']', "model_json"),
    (r'MODEL\s*=\s*["\']([^"\']+)["\']', "model_constant"),
    (r'llm_primary["\']?\s*[:=]\s*["\']([^"\']+)["\']', "llm_config"),
    (r'LLM_MODEL["\']?\s*=\s*["\']([^"\']+)["\']', "llm_model"),
]


def scan_project(project_path: Path) -> dict | None:
    """Сканирует проект на наличие LLM использования."""
    py_files = list(project_path.rglob("*.py"))
    if not py_files:
        return None

    findings = {"path": str(project_path.relative_to(LAB_ROOT)), "llm_usage": False, "detected_patterns": [], "models_used": [], "tasks": []}

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            for pattern, ptype in LLM_PATTERNS:
                matches = re.findall(pattern, content)
                for m in matches:
                    findings["llm_usage"] = True
                    if ptype not in findings["detected_patterns"]:
                        findings["detected_patterns"].append(ptype)
                    clean_model = m.strip('"\'').strip()
                    if clean_model and clean_model not in findings["models_used"]:
                        findings["models_used"].append(clean_model)
        except Exception:
            continue

    if findings["llm_usage"]:
        findings["tasks"].append("chat" if findings["models_used"] else "unknown")
        return findings
    return None


def scan_laboratory() -> list[dict]:
    """Сканирует всю лабораторию на LLM проекты."""
    projects = {}
    
    for item in LAB_ROOT.rglob("*"):
        if item.is_dir() and item.name not in EXCLUDE_DIRS and not item.name.startswith("."):
            result = scan_project(item)
            if result:
                path = result["path"]
                # Сохраняем самый глубокий путь для каждого уникального набора моделей
                key = tuple(sorted(result["models_used"]))
                if key not in projects or path.count("/") > projects[key]["path"].count("/"):
                    projects[key] = result

    final = list(projects.values())
    config_path = LAB_ROOT / "projects" / "telegram-bots" / "llm-evangelist" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump({"projects": final, "updated": str(os.popen('date').read().strip())}, f, indent=2)

    return final


if __name__ == "__main__":
    results = scan_laboratory()
    for p in results:
        print(f"{p['path']}: models={p['models_used'][:3]}")