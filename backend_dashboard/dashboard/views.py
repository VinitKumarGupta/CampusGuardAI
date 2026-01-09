from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from twilio.rest import Client
from .utils import get_vehicle_data, get_rewards_leaderboard

def tab_all_entries(request):
    data = get_vehicle_data()
    context = {
        'active_tab': 'all',
        'entries': data
    }
    return render(request, 'dashboard/tab_all.html', context)

def tab_violations(request):
    all_data = get_vehicle_data()
    # Filter only violations in Python
    violations = [d for d in all_data if d['is_violation']]
    
    context = {
        'active_tab': 'violations',
        'entries': violations
    }
    return render(request, 'dashboard/tab_violations.html', context)

def tab_rewards(request):
    leaderboard = get_rewards_leaderboard()
    context = {
        'active_tab': 'rewards',
        'drivers': leaderboard
    }
    return render(request, 'dashboard/tab_rewards.html', context)

def send_alert(request, track_id):
    """
    Sends an SMS via Twilio when the button is clicked.
    """
    # 1. Find the vehicle data
    all_data = get_vehicle_data()
    vehicle = next((item for item in all_data if item["track_id"] == int(track_id)), None)
    
    if not vehicle or not vehicle.get('phone_number'):
        return JsonResponse({'status': 'error', 'message': 'Phone number not found!'})

    # 2. Construct Message
    plate = vehicle.get('plate_number')
    violation = ", ".join(vehicle.get('violations', ['Unknown']))
    body_text = (
        f"⚠️ CAMPUS GUARD ALERT ⚠️\n"
        f"Vehicle {plate} detected violating rules: {violation}.\n"
        f"Please report to security office immediately."
    )

    # 3. Send via Twilio
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body_text,
            from_=settings.TWILIO_FROM_NUMBER,
            to=vehicle['phone_number']
        )
        print(f"SMS Sent: {message.sid}")
        return JsonResponse({'status': 'success', 'message': 'SMS Alert Sent!'})
        
    except Exception as e:
        print(f"Twilio Error: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)})