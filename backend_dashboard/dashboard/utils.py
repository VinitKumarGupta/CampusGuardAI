import json
import os
from django.conf import settings

# Maps YOLO Track IDs to Real-World Data
MOCK_REGISTRY = {
    212: {
        "plate": "GJ27TF3843", 
        "owner": "Vinit Gupta", 
        "phone": "+919638460250"
    },
    150: {
        "plate": "GJ05AB1234",
        "owner": "Anusmita Sen",
        "phone": "+919106983613"
    }
}

# List of authorized plates
AUTHORIZED_PLATES = ["GJ27TF3843", "MH12AB1234", "KA01MN9999"]

# --- GAMIFICATION SETTINGS ---
CREDIT_PER_CLEAN_ENTRY = 2   # Rupees earned for safe driving
RISK_POINTS_PER_VIOLATION = 100 # Points accumulated for bad driving

def get_vehicle_data():
    json_path = os.path.join(settings.MEDIA_ROOT, 'output', 'vehicle_log.json')
    data = []
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                content = f.read()
                if content:
                    data = json.loads(content)
        except Exception as e:
            print(f"Error reading JSON: {e}")

    processed_data = []
    for entry in reversed(data):
        track_id = entry.get('track_id')
        
        # Inject Mock Data
        if track_id in MOCK_REGISTRY:
            mock_data = MOCK_REGISTRY[track_id]
            entry['plate_number'] = mock_data['plate']
            entry['owner_name'] = mock_data['owner']
            entry['phone_number'] = mock_data['phone']
        else:
            entry['owner_name'] = "Unknown"
            entry['phone_number'] = None

        plate = entry.get('plate_number', 'Unreadable')
        status = "Unknown"
        status_color = "text-muted"
        
        if plate != "Unreadable" and plate != "Pending OCR":
            if plate in AUTHORIZED_PLATES:
                status = "Authorized"
                status_color = "text-success"
            else:
                status = "Unauthorized"
                status_color = "text-danger"
        
        entry['auth_status'] = status
        entry['auth_color'] = status_color
        
        if entry.get('image_path') and entry.get('image_path') != "N/A":
            entry['display_image'] = f"output/violations/{entry['image_path']}"
        else:
            entry['display_image'] = None

        processed_data.append(entry)
        
    return processed_data

def get_rewards_leaderboard():
    """
    Calculates Wallet Balance and Risk Score.
    """
    raw_data = get_vehicle_data()
    leaderboard = {}

    for entry in raw_data:
        plate = entry.get('plate_number', 'Unreadable')
        
        if plate in ["Unreadable", "Pending OCR", "N/A"]:
            continue
            
        if plate not in leaderboard:
            leaderboard[plate] = {
                'plate': plate,
                'owner': entry.get('owner_name', 'Unknown'),
                'total_entries': 0,
                'violations': 0,
                'clean_entries': 0,
                'wallet_balance': 0,    # Earned Credits (₹)
                'risk_score': 0         # Cumulative Penalty
            }
        
        stats = leaderboard[plate]
        stats['total_entries'] += 1
        
        if entry['is_violation']:
            stats['violations'] += 1
            stats['risk_score'] += RISK_POINTS_PER_VIOLATION
        else:
            stats['clean_entries'] += 1
            stats['wallet_balance'] += CREDIT_PER_CLEAN_ENTRY

    # Determine Driver Status based on Risk Score
    results = []
    for plate, stats in leaderboard.items():
        if stats['risk_score'] == 0:
            stats['status'] = "🌟 Gold Member"
            stats['status_color'] = "text-success"
            stats['row_class'] = "table-success"
        elif stats['risk_score'] < 300:
            stats['status'] = "⚠️ At Risk"
            stats['status_color'] = "text-warning"
            stats['row_class'] = "table-warning"
        else:
            stats['status'] = "🚫 Blacklisted"
            stats['status_color'] = "text-danger"
            stats['row_class'] = "table-danger"
            stats['wallet_balance'] = 0 # Forfeit earnings if blacklisted
            
        results.append(stats)

    # Sort by Wallet Balance (Highest First)
    return sorted(results, key=lambda x: x['wallet_balance'], reverse=True)
