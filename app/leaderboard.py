import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    """Load leaderboard data from file"""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"single_player": [], "multiplayer": []}
    return {"single_player": [], "multiplayer": []}

def save_leaderboard(data):
    """Save leaderboard data to file"""
    try:
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def add_single_player_record(player_name, time, map_name, difficulty, laps):
    """Add a single player record to leaderboard"""
    leaderboard = load_leaderboard()
    
    record = {
        "name": player_name[:10],  # Limit to 10 characters
        "time": round(time, 2),
        "map": map_name,
        "difficulty": difficulty,
        "laps": laps,
        "date": datetime.now().strftime("%m/%d/%Y | %I:%M %p").upper()
    }
    
    leaderboard["single_player"].append(record)
    
    # Sort by time (fastest first) and keep top 10
    leaderboard["single_player"].sort(key=lambda x: x["time"])
    leaderboard["single_player"] = leaderboard["single_player"][:10]
    
    save_leaderboard(leaderboard)
    return record

def add_multiplayer_record(winner_name, loser_name, time, map_name, laps):
    """Add a multiplayer record to leaderboard"""
    leaderboard = load_leaderboard()
    
    record = {
        "winner": winner_name[:10],
        "loser": loser_name[:10],
        "time": round(time, 2),
        "map": map_name,
        "laps": laps,
        "date": datetime.now().strftime("%m/%d/%Y | %I:%M %p").upper()
    }
    
    leaderboard["multiplayer"].append(record)
    
    # Sort by time (fastest first) and keep top 10
    leaderboard["multiplayer"].sort(key=lambda x: x["time"])
    leaderboard["multiplayer"] = leaderboard["multiplayer"][:10]
    
    save_leaderboard(leaderboard)
    return record

def get_top_records(mode="single_player", limit=10, difficulty=None):
    """Get top records for a specific mode, optionally filtered by difficulty"""
    leaderboard = load_leaderboard()
    records = leaderboard.get(mode, [])
    
    # Filter by difficulty if specified (for single player)
    if mode == "single_player" and difficulty:
        records = [r for r in records if r.get("difficulty") == difficulty]
    
    return records[:limit]
