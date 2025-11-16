#!/usr/bin/env python3
"""
Test script for Instagram Reel Transcript Extractor
This script tests the improved download functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_openai import InstagramReelTranscript
import streamlit as st

def test_download():
    """Test the download functionality"""
    print("🧪 Testing Instagram Reel Transcript Extractor...")
    
    # Test URL (you can replace this with any public Instagram reel)
    test_url = "https://www.instagram.com/reel/DPtssWqAZq3/?utm_source=ig_web_copy_link&igsh=MzRIC"
    
    try:
        # Initialize the extractor
        extractor = InstagramReelTranscript()
        print("✅ Extractor initialized successfully")
        
        # Test video download
        print("📥 Testing video download...")
        video_path, video_info = extractor.download_instagram_video(test_url)
        
        if video_path:
            print(f"✅ Video downloaded successfully: {video_path}")
            print(f"📊 Video info: {video_info.get('title', 'Unknown') if video_info else 'Unknown'}")
            
            # Test alternative method if primary fails
            if not video_path:
                print("🔄 Trying alternative download method...")
                video_path, video_info = extractor.download_instagram_video_alternative(test_url)
                
                if video_path:
                    print(f"✅ Alternative method succeeded: {video_path}")
                else:
                    print("❌ Alternative method also failed")
        else:
            print("❌ Video download failed")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_download()

