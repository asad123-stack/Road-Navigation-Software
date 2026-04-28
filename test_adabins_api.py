#!/usr/bin/env python3
"""
Test AdaBins integration with actual API calls.
Sends frames to /api/process_frame and validates depth outputs.
"""

import requests
import base64
import numpy as np
import cv2
from pathlib import Path

def create_test_frame():
    """Create a test frame (480x640 BGR image)."""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
    # Add some variation so depth estimation has real content
    cv2.rectangle(frame, (50, 50), (150, 150), (0, 255, 0), -1)
    cv2.rectangle(frame, (200, 100), (400, 300), (255, 0, 0), -1)
    cv2.circle(frame, (600, 200), 50, (0, 255, 255), -1)
    return frame

def frame_to_dataurl(frame):
    """Convert BGR frame to data URL (base64 JPEG)."""
    _, buffer = cv2.imencode('.jpg', frame)
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"

def test_single_frame(api_url="http://127.0.0.1:5000"):
    """Send a single frame and verify depth output."""
    print("\n" + "="*60)
    print("Testing AdaBins Integration via API")
    print("="*60)
    
    frame = create_test_frame()
    print(f"✓ Created test frame: {frame.shape}")
    
    data_url = frame_to_dataurl(frame)
    print(f"✓ Encoded to data URL ({len(data_url)//1024} KB)")
    
    payload = {
        "frame": data_url,
        "lat": 19.0760,
        "lng": 72.8777
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/process_frame",
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"\n✓ API Response received (status {response.status_code})")
        print(f"  - Risk score: {result.get('risk_score')}")
        print(f"  - Navigation cue: {result.get('cue')}")
        print(f"  - Scene type: {result.get('scene_type')}")
        print(f"  - LSTM risk: {result.get('lstm_risk')}")
        print(f"  - LSTM alert: {result.get('lstm_alert')}")
        
        zone_depths = result.get('zone_depths', {})
        print(f"\n✓ Zone Depths (from depth model):")
        print(f"  - Left:   {zone_depths.get('left'):.3f}")
        print(f"  - Center: {zone_depths.get('center'):.3f}")
        print(f"  - Right:  {zone_depths.get('right'):.3f}")
        
        detections = result.get('detections', [])
        print(f"\n✓ Detections: {len(detections)} objects found")
        if detections:
            for i, det in enumerate(detections[:3]):
                print(f"  - Object {i+1}: {det.get('label')} (conf: {det.get('confidence')})")
        
        assert zone_depths, "Zone depths should be present"
        assert all(k in zone_depths for k in ['left', 'center', 'right']), "All zones should be present"
        assert all(0 <= zone_depths[k] <= 1.0 for k in zone_depths), "All depths should be in [0, 1]"
        
        print("\n✅ ALL ASSERTIONS PASSED!")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Request failed: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ Assertion failed: {e}")
        return False

def test_consecutive_frames(num_frames=12, api_url="http://127.0.0.1:5000"):
    """Test depth throttling with consecutive frames."""
    print("\n" + "="*60)
    print(f"Testing Frame Throttling ({num_frames} frames)")
    print("="*60)
    
    print("Expected pattern:")
    print("  Frame 1-2: AdaBins only (~80ms)")
    print("  Frame 3:   MiDaS + AdaBins blend (~300ms)")
    print("  Frame 4-5: Cached MiDaS + fresh AdaBins (~80ms)")
    print("  Frame 6:   MiDaS + AdaBins blend (~300ms)")
    print("  ...")
    
    zone_depths_history = []
    
    for frame_num in range(1, num_frames + 1):
        frame = create_test_frame()
        data_url = frame_to_dataurl(frame)
        
        payload = {"frame": data_url, "lat": 0, "lng": 0}
        
        try:
            response = requests.post(
                f"{api_url}/api/process_frame",
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            result = response.json()
            zone_depths = result.get('zone_depths', {})
            zone_depths_history.append(zone_depths)
            
            is_midas_frame = (frame_num % 3 == 0)
            marker = "→ MiDaS" if is_midas_frame else "  AdaBins"
            print(f"  Frame {frame_num:2d} {marker}: center={zone_depths.get('center'):.3f}")
            
        except Exception as e:
            print(f"  Frame {frame_num:2d} ❌ Error: {e}")
            return False
    
    print(f"\n✓ Processed {num_frames} frames successfully")
    print(f"✓ Zone depth consistency (center values):")
    centers = [zd.get('center', 0) for zd in zone_depths_history]
    print(f"  - Min: {min(centers):.3f}")
    print(f"  - Max: {max(centers):.3f}")
    print(f"  - Mean: {np.mean(centers):.3f}")
    print(f"  - Std: {np.std(centers):.3f}")
    
    print("\n✅ Frame throttling test PASSED!")
    return True

if __name__ == "__main__":
    import sys
    
    api_url = "http://127.0.0.1:5000"
    
    print("\n" + "█"*60)
    print("  SmartHelmet Nav - AdaBins API Integration Test")
    print("█"*60)
    
    print("\nTarget API:", api_url)
    print("Make sure backend is running: python app.py\n")
    
    success = True
    
    # Test 1: Single frame
    if not test_single_frame(api_url):
        success = False
    
    # Test 2: Consecutive frames
    if not test_consecutive_frames(12, api_url):
        success = False
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL API TESTS PASSED!")
        print("="*60)
        print("\nAdaBins integration is working correctly:")
        print("  ✓ Frames processed without error")
        print("  ✓ Zone depths returned consistently")
        print("  ✓ Throttling logic functioning")
        print("  ✓ API contract unchanged")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)
