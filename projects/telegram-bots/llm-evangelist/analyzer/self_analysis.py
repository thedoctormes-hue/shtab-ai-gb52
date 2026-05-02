#!/usr/bin/env python3
"""Самоанализ LLMevangelist для рекомендаций."""

import json
from pathlib import Path

def analyze_self():
    """Анализирует самого себя и предлагает улучшения."""
    self_path = Path(__file__).parent.parent
    
    self_data = {
        "project": "llm-evangelist",
        "uses_models": ["mistralai/mistral-small-creative", "tencent/hy3-preview:free"],
        "cost_per_review": "$0.001-0.005",
        "recommendation": None
    }
    
    # Проверяем актуальность моделей
    recommendations = []
    
    # Предлагаем дешевле
    recommendations.append({
        "type": "cost_optimization",
        "suggestion": "Заменить mistral-small на ling-2.6-flash:free для dry-run",
        "savings": "100% (free)"
    })
    
    # Предлагаем быстрее
    recommendations.append({
        "type": "performance",
        "suggestion": "Добавить fallback на deepseek-v4-flash при падении mistral",
        "benefit": "Повышение надежности"
    })
    
    self_data["recommendation"] = recommendations
    
    return self_data

def find_non_llm_projects(projects: list[dict]) -> list[dict]:
    """Находит проекты без LLM, где можно добавить."""
    non_llm = []
    
    for project in projects:
        if not project.get("llm_usage"):
            non_llm.append({
                "path": project["path"],
                "suggestion": "Можно добавить чат-бота или анализ данных"
            })
    
    return non_llm

if __name__ == "__main__":
    result = analyze_self()
    print(json.dumps(result, indent=2))