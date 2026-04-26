import cv2
import os
import numpy as np
from config import TEMP_DIR
import google.generativeai as genai
from config import GEMINI_API_KEY
import re

genai.configure(api_key=GEMINI_API_KEY)

def extract_anime_name_from_text(text):
    """Extract anime name from video filename or caption"""
    patterns = [
        r'⛩\s*([^\[]+)',
        r'🔰\s*([^\n]+)',
        r'^([A-Za-z0-9\s:]+)\[',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return None

def extract_key_frames(video_path, num_frames=10):
    """Extract key frames from video"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps
    
    # Extract frames at intervals
    interval = total_frames // (num_frames + 1)
    frames = []
    frame_paths = []
    
    for i in range(1, num_frames + 1):
        frame_number = i * interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if ret:
            # Check frame quality
            if is_good_frame(frame):
                frame_path = os.path.join(TEMP_DIR, f"frame_{i}.jpg")
                cv2.imwrite(frame_path, frame)
                frames.append(frame)
                frame_paths.append(frame_path)
    
    cap.release()
    return frame_paths

def is_good_frame(frame):
    """Check if frame is good quality"""
    # Check brightness
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    
    # Check sharpness
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    return brightness > 30 and brightness < 225 and laplacian_var > 100

def analyze_frame_with_ai(frame_path):
    """Use Gemini to analyze if frame is suitable for thumbnail"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with open(frame_path, 'rb') as f:
            image_data = f.read()
        
        prompt = """Analyze this anime frame and rate it from 1-10 for thumbnail suitability.
        Consider: character visibility, action/emotion, composition, visual appeal.
        Respond with only a number between 1-10."""
        
        response = model.generate_content([prompt, {'mime_type': 'image/jpeg', 'data': image_data}])
        score = int(response.text.strip())
        return score
    except:
        return 5