import streamlit as st
import os
import requests
from openai import OpenAI
import json
import time
from dotenv import load_dotenv
import tempfile
import subprocess
import sys

# Load environment variables
load_dotenv()

class InstagramReelTranscript:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_key:
            st.error("Please set your OPENAI_API_KEY in the environment variables")
            st.stop()
        
        self.client = OpenAI(api_key=self.openai_key)
    
    def download_video_with_ytdlp(self, url):
        """Download video using yt-dlp"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_file.close()
            
            # Use yt-dlp to download
            cmd = [
                'yt-dlp',
                '--format', 'best[filesize<50M]',
                '--output', temp_file.name,
                '--quiet',
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(temp_file.name):
                return temp_file.name, None
            else:
                return None, f"Download failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return None, "Download timeout"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def extract_audio_with_ffmpeg(self, video_path):
        """Extract audio using ffmpeg"""
        try:
            audio_path = video_path.replace('.mp4', '.mp3')
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ac', '1',
                '-ar', '16000',
                '-y',
                audio_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(audio_path):
                return audio_path, None
            else:
                return None, f"Audio extraction failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return None, "Audio extraction timeout"
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def transcribe_audio(self, audio_path, model="whisper-1"):
        """Transcribe audio using OpenAI Whisper API"""
        try:
            with open(audio_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )
            return transcript, None
        except Exception as e:
            return None, f"Error transcribing audio: {str(e)}"
    
    def extract_reel_data(self, reel_url, model="whisper-1"):
        """Extract complete data from Instagram reel"""
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Download video
            status_text.text("📥 Downloading Instagram video...")
            progress_bar.progress(20)
            
            video_path, error = self.download_video_with_ytdlp(reel_url)
            if not video_path:
                return {"success": False, "error": error or "Failed to download video", "data": None}
            
            # Step 2: Extract audio
            status_text.text("🎵 Extracting audio from video...")
            progress_bar.progress(40)
            
            audio_path, error = self.extract_audio_with_ffmpeg(video_path)
            if not audio_path:
                # Clean up video file
                try:
                    os.unlink(video_path)
                except:
                    pass
                return {"success": False, "error": error or "Failed to extract audio", "data": None}
            
            # Step 3: Transcribe audio
            status_text.text("🎤 Transcribing audio with OpenAI Whisper...")
            progress_bar.progress(60)
            
            transcript, error = self.transcribe_audio(audio_path, model)
            if not transcript:
                # Clean up files
                try:
                    os.unlink(video_path)
                    os.unlink(audio_path)
                except:
                    pass
                return {"success": False, "error": error or "Failed to transcribe audio", "data": None}
            
            # Step 4: Process results
            status_text.text("📊 Processing results...")
            progress_bar.progress(80)
            
            # Clean up temporary files
            try:
                os.unlink(video_path)
                os.unlink(audio_path)
            except:
                pass
            
            # Format results
            result = {
                "url": reel_url,
                "transcript": transcript.text,
                "language": transcript.language,
                "duration": transcript.duration,
                "segments": [
                    {
                        "start": seg.start,
                        "end": seg.end,
                        "text": seg.text
                    } for seg in transcript.segments
                ] if hasattr(transcript, 'segments') else [],
                "metadata": {
                    "model_used": model,
                    "processing_time": time.time(),
                }
            }
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            return {
                "success": True,
                "data": [result],
                "total_items": 1
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

def main():
    st.set_page_config(
        page_title="Instagram Reel Transcript Extractor",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 Instagram Reel Transcript Extractor")
    st.markdown("Extract complete transcript data from Instagram reels using OpenAI Whisper API")
    
    # Show deployment info
    st.info("🚀 **Deployed on Vercel** - Optimized for serverless deployment")
    
    # Initialize the transcript extractor
    if 'extractor' not in st.session_state:
        st.session_state.extractor = InstagramReelTranscript()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        model_options = {
            "whisper-1": "Whisper-1 (Standard)",
            "whisper-large-v2": "Whisper Large V2 (High Quality)",
            "whisper-large-v3": "Whisper Large V3 (Latest)"
        }
        
        selected_model = st.selectbox(
            "Select Whisper Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            help="Whisper-1 is fastest and cheapest, Large V3 is most accurate"
        )
        
        st.markdown("---")
        st.markdown("### 💰 Cost Information")
        st.info("""
        **OpenAI Whisper Pricing:**
        - Whisper-1: $0.006 per minute
        - Whisper Large V2: $0.006 per minute  
        - Whisper Large V3: $0.006 per minute
        
        *Much cheaper than Apify!*
        """)
        
        st.markdown("### ⚠️ Vercel Limitations")
        st.warning("""
        **Current Limitations:**
        - Max video size: 50MB
        - Processing time: ~30 seconds
        - Serverless execution limits
        
        *For larger videos, consider local deployment*
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Enter Instagram Reel URL")
        
        # URL input
        reel_url = st.text_input(
            "Instagram Reel URL",
            placeholder="https://www.instagram.com/reel/...",
            help="Paste the Instagram reel URL you want to transcribe"
        )
        
        # Extract button
        if st.button("🚀 Extract Transcript Data", type="primary", use_container_width=True):
            if not reel_url:
                st.error("Please enter an Instagram reel URL")
            elif "instagram.com/reel/" not in reel_url:
                st.error("Please enter a valid Instagram reel URL")
            else:
                with st.spinner("Processing your reel..."):
                    result = st.session_state.extractor.extract_reel_data(
                        reel_url=reel_url,
                        model=selected_model
                    )
                
                if result["success"]:
                    st.success(f"✅ Successfully extracted data!")
                    
                    # Display results
                    st.header("📊 Extracted Data")
                    
                    for i, item in enumerate(result["data"]):
                        with st.expander(f"Transcript Results", expanded=True):
                            st.subheader("📝 Full Transcript")
                            st.write(item["transcript"])
                            
                            st.subheader("📊 Metadata")
                            col_meta1, col_meta2 = st.columns(2)
                            
                            with col_meta1:
                                st.metric("Language", item["language"])
                                st.metric("Duration", f"{item['duration']:.1f}s")
                                st.metric("Model Used", item["metadata"]["model_used"])
                            
                            if item["segments"]:
                                st.subheader("⏱️ Timestamped Segments")
                                for seg in item["segments"][:10]:  # Show first 10 segments
                                    st.write(f"**{seg['start']:.1f}s - {seg['end']:.1f}s:** {seg['text']}")
                                
                                if len(item["segments"]) > 10:
                                    st.write(f"... and {len(item['segments']) - 10} more segments")
                    
                    # Download options
                    st.header("💾 Download Options")
                    
                    col_download1, col_download2 = st.columns(2)
                    
                    with col_download1:
                        # Download as JSON
                        json_data = json.dumps(result["data"], indent=2)
                        st.download_button(
                            label="📄 Download as JSON",
                            data=json_data,
                            file_name=f"instagram_reel_transcript_{int(time.time())}.json",
                            mime="application/json"
                        )
                    
                    with col_download2:
                        # Download as text
                        text_data = result["data"][0]["transcript"]
                        st.download_button(
                            label="📝 Download as Text",
                            data=text_data,
                            file_name=f"instagram_reel_transcript_{int(time.time())}.txt",
                            mime="text/plain"
                        )
                
                else:
                    st.error(f"❌ Error extracting data: {result['error']}")
    
    with col2:
        st.header("ℹ️ Instructions")
        st.markdown("""
        ### How to use:
        1. **Paste an Instagram reel URL** in the input field
        2. **Select Whisper model** in the sidebar
        3. **Click Extract** to get the transcript data
        4. **View and download** results
        
        ### Features:
        - 🎯 **Direct OpenAI Integration**: No third-party costs
        - 🤖 **Multiple Whisper Models**: Choose quality vs speed
        - 📄 **Timestamped Segments**: Precise timing information
        - 💾 **Multiple Export Formats**: JSON and text
        - 💰 **Cost Effective**: Only pay OpenAI directly
        
        ### Supported URLs:
        - Instagram Reels: `https://www.instagram.com/reel/...`
        - Public reels only
        - Max size: 50MB (Vercel limit)
        """)
        
        st.header("🔧 Technical Details")
        st.info("""
        **This version uses:**
        - OpenAI Whisper API directly
        - yt-dlp for video downloading
        - ffmpeg for audio processing
        - Optimized for Vercel serverless
        """)
        
        st.header("🚀 Deployment")
        st.success("""
        **Deployed on Vercel:**
        - Serverless architecture
        - Global CDN
        - Automatic scaling
        """)

if __name__ == "__main__":
    main()
