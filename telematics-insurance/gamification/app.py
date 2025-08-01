"""
Gamification Microservice
Handles points, badges, and leaderboard APIs
"""
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Mock data storage (replace with database in production)
drivers_data = {}
leaderboard = []

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "gamification"})

@app.route('/points/award', methods=['POST'])
def award_points():
    """Award points to a driver"""
    data = request.get_json()
    
    driver_id = data.get('driver_id')
    points = data.get('points', 0)
    reason = data.get('reason', 'General')
    
    if not driver_id:
        return jsonify({"error": "driver_id required"}), 400
    
    # Initialize driver if not exists
    if driver_id not in drivers_data:
        drivers_data[driver_id] = {
            'total_points': 0,
            'level': 1,
            'badges': [],
            'history': []
        }
    
    # Award points
    drivers_data[driver_id]['total_points'] += points
    drivers_data[driver_id]['history'].append({
        'points': points,
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    })
    
    # Update level
    new_level = calculate_level(drivers_data[driver_id]['total_points'])
    drivers_data[driver_id]['level'] = new_level
    
    return jsonify({
        "driver_id": driver_id,
        "points_awarded": points,
        "total_points": drivers_data[driver_id]['total_points'],
        "current_level": new_level,
        "reason": reason
    })

@app.route('/driver/<driver_id>/stats', methods=['GET'])
def get_driver_stats(driver_id):
    """Get driver gamification statistics"""
    if driver_id not in drivers_data:
        return jsonify({"error": "Driver not found"}), 404
    
    driver_stats = drivers_data[driver_id]
    
    return jsonify({
        "driver_id": driver_id,
        "total_points": driver_stats['total_points'],
        "level": driver_stats['level'],
        "level_name": get_level_name(driver_stats['level']),
        "badges": driver_stats['badges'],
        "points_to_next_level": calculate_points_to_next_level(driver_stats['total_points']),
        "recent_activity": driver_stats['history'][-10:]  # Last 10 activities
    })

@app.route('/badges/award', methods=['POST'])
def award_badge():
    """Award a badge to a driver"""
    data = request.get_json()
    
    driver_id = data.get('driver_id')
    badge_name = data.get('badge_name')
    badge_description = data.get('badge_description', '')
    
    if not driver_id or not badge_name:
        return jsonify({"error": "driver_id and badge_name required"}), 400
    
    if driver_id not in drivers_data:
        drivers_data[driver_id] = {
            'total_points': 0,
            'level': 1,
            'badges': [],
            'history': []
        }
    
    # Check if badge already earned
    if badge_name not in drivers_data[driver_id]['badges']:
        drivers_data[driver_id]['badges'].append(badge_name)
        
        # Award bonus points for badge
        bonus_points = get_badge_points(badge_name)
        drivers_data[driver_id]['total_points'] += bonus_points
        
        drivers_data[driver_id]['history'].append({
            'type': 'badge',
            'badge_name': badge_name,
            'points': bonus_points,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({
            "driver_id": driver_id,
            "badge_awarded": badge_name,
            "description": badge_description,
            "bonus_points": bonus_points,
            "total_badges": len(drivers_data[driver_id]['badges'])
        })
    else:
        return jsonify({"message": "Badge already earned"}), 200

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get current leaderboard"""
    # Sort drivers by points
    sorted_drivers = sorted(
        [(driver_id, data) for driver_id, data in drivers_data.items()],
        key=lambda x: x[1]['total_points'],
        reverse=True
    )
    
    leaderboard = []
    for rank, (driver_id, data) in enumerate(sorted_drivers[:10], 1):
        leaderboard.append({
            "rank": rank,
            "driver_id": driver_id,
            "total_points": data['total_points'],
            "level": data['level'],
            "level_name": get_level_name(data['level']),
            "badges_count": len(data['badges'])
        })
    
    return jsonify({"leaderboard": leaderboard})

@app.route('/challenges', methods=['GET'])
def get_challenges():
    """Get available challenges"""
    challenges = [
        {
            "id": "smooth_driving_week",
            "title": "Smooth Driving Week",
            "description": "Complete 5 trips with smooth acceleration and braking",
            "reward_points": 200,
            "progress_required": 5,
            "active": True
        },
        {
            "id": "phone_free_month",
            "title": "Phone-Free Month",
            "description": "30 days without phone usage while driving",
            "reward_points": 500,
            "progress_required": 30,
            "active": True
        },
        {
            "id": "speed_master",
            "title": "Speed Master",
            "description": "Maintain speed compliance for 10 consecutive trips",
            "reward_points": 150,
            "progress_required": 10,
            "active": True
        }
    ]
    
    return jsonify({"challenges": challenges})

def calculate_level(total_points):
    """Calculate driver level based on total points"""
    level_thresholds = [0, 500, 1500, 3000, 5000, 10000, 20000]
    
    for level, threshold in enumerate(level_thresholds[1:], 1):
        if total_points < threshold:
            return level
    
    return len(level_thresholds)

def get_level_name(level):
    """Get level name from level number"""
    level_names = {
        1: "Learner",
        2: "Careful Driver",
        3: "Safe Driver", 
        4: "Expert Driver",
        5: "Master Driver",
        6: "Legendary Driver"
    }
    return level_names.get(level, "Unknown")

def calculate_points_to_next_level(total_points):
    """Calculate points needed for next level"""
    level_thresholds = [0, 500, 1500, 3000, 5000, 10000, 20000]
    
    for threshold in level_thresholds[1:]:
        if total_points < threshold:
            return threshold - total_points
    
    return 0  # Max level reached

def get_badge_points(badge_name):
    """Get bonus points for specific badges"""
    badge_points = {
        "safe_driver": 100,
        "phone_free_champion": 150,
        "smooth_operator": 75,
        "speed_master": 100,
        "eco_warrior": 125,
        "night_owl": 80,
        "highway_hero": 90
    }
    return badge_points.get(badge_name, 50)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)
