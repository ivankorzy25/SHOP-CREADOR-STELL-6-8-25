import json
import os
from datetime import datetime

def track_usage():
    usage_file = "cline_usage.json"
    
    # Cargar datos existentes o crear nuevos
    if os.path.exists(usage_file):
        with open(usage_file, "r") as f:
            usage_data = json.load(f)
    else:
        usage_data = {"daily_usage": []}
    
    # Agregar entrada de hoy
    today_entry = {
        "date": datetime.now().isoformat(),
        "providers": {
            "gemini_cli": {"used": 0, "limit": 1000, "remaining": 1000},
            "anthropic": {"used": 0, "limit": "unlimited"},
            "google_pro": {"used": 0, "limit": "varies"}
        },
        "tasks_completed": 0,
        "tokens_used": 0
    }
    
    usage_data["daily_usage"].append(today_entry)
    
    # Guardar datos actualizados
    with open(usage_file, "w") as f:
        json.dump(usage_data, f, indent=2)
    
    print(f"Usage tracking initialized for {today_entry['date']}")

if __name__ == "__main__":
    track_usage()
