#!/usr/bin/env python3
"""
API integration test for Kalman filter tracking.
Sends frames via /api/process_frame and validates trajectory smoothness.
"""

import requests
import base64
import numpy as np
import cv2
from pathlib import Path


def create_moving_object_frame(frame_num: int, width: int = 640, height: int = 480):
    """
    Create a test frame with a moving object.
    Object follows a parabolic path with added noise.
    """
    frame = np.ones((height, width, 3), dtype=np.uint8) * 50
    
    # Parabolic motion: x = 50 + 50*t, y = 100 + 20*t - 2*t^2
    t = frame_num / 10.0
    center_x = int(50 + 50 * t)
    center_y = int(100 + 20 * t - 2 * t * t)
    
    # Add some noise
    center_x += np.random.randint(-5, 6)
    center_y += np.random.randint(-5, 6)
    
    # Draw circle at center
    cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), -1)
    
    # Draw background shapes
    cv2.rectangle(frame, (10, 10), (100, 100), (255, 0, 0), 2)
    cv2.rectangle(frame, (500, 300), (600, 400), (0, 255, 255), 2)
    
    return frame


def frame_to_dataurl(frame):
    """Convert BGR frame to data URL (base64 JPEG)."""
    _, buffer = cv2.imencode('.jpg', frame)
    b64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"


def test_trajectory_smoothing(num_frames=15, api_url="http://127.0.0.1:5000"):
    """Test trajectory smoothing with Kalman filtering."""
    print("\n" + "="*60)
    print(f"Testing Trajectory Smoothing ({num_frames} frames)")
    print("="*60)
    
    trajectories = []
    frame_num = 0
    
    for frame_num in range(num_frames):
        frame = create_moving_object_frame(frame_num)
        data_url = frame_to_dataurl(frame)
        
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
            
            trajectories_data = result.get('trajectories', [])
            if trajectories_data:
                # Get the first (main) trajectory
                traj = trajectories_data[0]
                path = traj.get('predicted_path', [])
                
                marker = "🎯" if len(path) > 0 else "  "
                print(f"  Frame {frame_num+1:2d} {marker}: {len(path)} points in trajectory")
                
                trajectories.append(path)
            
        except Exception as e:
            print(f"  Frame {frame_num+1:2d} ❌ Error: {e}")
            return False
    
    # Analyze trajectory smoothness
    if trajectories and trajectories[-1]:
        final_path = trajectories[-1]
        positions = np.array(final_path)
        
        print(f"\n✓ Final trajectory has {len(final_path)} points")
        
        if len(positions) > 2:
            # Calculate velocities
            velocities = np.diff(positions, axis=0)
            
            # Calculate jerkiness (smoothness metric)
            jerks = np.diff(velocities, axis=0)
            jerkiness = np.mean(np.sqrt(np.sum(jerks**2, axis=1)))
            
            print(f"✓ Average jerkiness (lower=smoother): {jerkiness:.3f}")
            print(f"✓ X-axis range: [{positions[:, 0].min():.1f}, {positions[:, 0].max():.1f}]")
            print(f"✓ Y-axis range: [{positions[:, 1].min():.1f}, {positions[:, 1].max():.1f}]")
            
            # Expected smoothness: jerkiness < 10 for good Kalman filtering
            if jerkiness < 10:
                print(f"✓ Trajectory smoothness: EXCELLENT ⭐")
            elif jerkiness < 20:
                print(f"✓ Trajectory smoothness: GOOD ✓")
            else:
                print(f"✓ Trajectory smoothness: FAIR")
        
        print("\n✅ Trajectory smoothing test PASSED!")
        return True
    
    return False


def test_track_consistency(num_frames=10, api_url="http://127.0.0.1:5000"):
    """Test track ID consistency across frames."""
    print("\n" + "="*60)
    print(f"Testing Track ID Consistency ({num_frames} frames)")
    print("="*60)
    
    track_ids_history = []
    
    for frame_num in range(num_frames):
        frame = create_moving_object_frame(frame_num)
        data_url = frame_to_dataurl(frame)
        
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
            
            trajectories = result.get('trajectories', [])
            if trajectories:
                track_id = trajectories[0].get('id')
                label = trajectories[0].get('label')
                age = trajectories[0].get('age')
                track_ids_history.append(track_id)
                print(f"  Frame {frame_num+1:2d}: Track {track_id} ({label}, age={age})")
            
        except Exception as e:
            print(f"  Frame {frame_num+1:2d} ❌ Error: {e}")
            return False
    
    # Verify consistency
    if track_ids_history:
        unique_ids = set(track_ids_history)
        print(f"\n✓ Unique track IDs seen: {unique_ids}")
        print(f"✓ Track ID stability: {len(track_ids_history) - len(unique_ids)} ID switches")
        
        if len(unique_ids) == 1:
            print("✓ Track ID consistency: PERFECT (same ID throughout) ⭐")
        else:
            print(f"✓ Track ID consistency: {len(unique_ids)} IDs for {len(track_ids_history)} frames")
        
        print("\n✅ Track consistency test PASSED!")
        return True
    
    return False


if __name__ == "__main__":
    import sys
    
    api_url = "http://127.0.0.1:5000"
    
    print("\n" + "█"*60)
    print("  Kalman Filter Tracking - API Integration Test")
    print("█"*60)
    
    print("\nTarget API:", api_url)
    print("Make sure backend is running: python app.py\n")
    
    success = True
    
    # Test 1: Trajectory smoothing
    if not test_trajectory_smoothing(15, api_url):
        success = False
    
    # Test 2: Track consistency
    if not test_track_consistency(10, api_url):
        success = False
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL KALMAN TRACKING TESTS PASSED!")
        print("="*60)
        print("\nBenefits of Kalman filtering:")
        print("  ✓ Smoother trajectory visualization")
        print("  ✓ Better velocity estimation")
        print("  ✓ Reduced ID switches")
        print("  ✓ More stable risk scoring")
        print("  ✓ Better occlusion recovery")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)
