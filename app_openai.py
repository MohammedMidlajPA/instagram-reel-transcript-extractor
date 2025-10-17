import streamlit as st
import os
import tempfile
import requests
from openai import OpenAI
import yt_dlp
from pydub import AudioSegment
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstagramReelTranscript:
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_key:
            st.error("Please set your OPENAI_API_KEY in the .env file")
            st.stop()
        
        self.client = OpenAI(api_key=self.openai_key)
    
    def download_instagram_video(self, url):
        """Download Instagram video using yt-dlp with improved error handling"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Create a unique temporary file path
                temp_dir = tempfile.gettempdir()
                timestamp = int(time.time())
                temp_filename = f"instagram_video_{timestamp}.%(ext)s"
                
                # Configure yt-dlp options with better error handling
                ydl_opts = {
                    'format': 'best[height<=720]/best',  # Prefer lower resolution, fallback to best
                    'outtmpl': os.path.join(temp_dir, temp_filename),
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'socket_timeout': 30,  # 30 second timeout
                    'retries': 3,  # Retry failed downloads
                    'fragment_retries': 3,  # Retry failed fragments
                    'http_chunk_size': 10485760,  # 10MB chunks
                    'concurrent_fragment_downloads': 1,  # Single thread to avoid pipe issues
                    'ignoreerrors': False,
                    'no_check_certificate': True,  # Sometimes helps with SSL issues
                    'prefer_insecure': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Extract info first
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        raise Exception("Could not extract video information")
                    
                    video_title = info.get('title', 'instagram_video')
                    video_id = info.get('id', str(timestamp))
                    
                    # Clean title for filename
                    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title[:50]  # Limit length
                    
                    # Update output template with safe title
                    ydl_opts['outtmpl'] = os.path.join(temp_dir, f"{safe_title}_{video_id}.%(ext)s")
                    
                    # Download the video
                    ydl.download([url])
                    
                    # Find the downloaded file
                    downloaded_files = []
                    for file in os.listdir(temp_dir):
                        if (file.startswith(safe_title) or file.startswith(f"instagram_video_{timestamp}")) and \
                           file.endswith(('.mp4', '.webm', '.mkv', '.mov', '.m4v')):
                            file_path = os.path.join(temp_dir, file)
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                downloaded_files.append((file_path, os.path.getctime(file_path)))
                    
                    if downloaded_files:
                        # Get the most recent file
                        video_path = max(downloaded_files, key=lambda x: x[1])[0]
                        return video_path, info
                    
                    # If no files found, try to find any recent video files
                    all_video_files = []
                    for file in os.listdir(temp_dir):
                        if file.endswith(('.mp4', '.webm', '.mkv', '.mov', '.m4v')):
                            file_path = os.path.join(temp_dir, file)
                            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                                # Check if file was created recently (within last 5 minutes)
                                if time.time() - os.path.getctime(file_path) < 300:
                                    all_video_files.append((file_path, os.path.getctime(file_path)))
                    
                    if all_video_files:
                        video_path = max(all_video_files, key=lambda x: x[1])[0]
                        return video_path, info
                    
                    raise Exception("No video file found after download")
                    
            except Exception as e:
                error_msg = str(e)
                st.warning(f"Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
                
                if attempt < max_retries - 1:
                    st.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    st.error(f"All attempts failed. Last error: {error_msg}")
                    return None, None
        
        return None, None
    
    def download_instagram_video_alternative(self, url):
        """Alternative download method using different yt-dlp configuration"""
        try:
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            
            # Alternative configuration - more conservative approach
            ydl_opts = {
                'format': 'worst[height<=480]/worst',  # Use lower quality to avoid issues
                'outtmpl': os.path.join(temp_dir, f'instagram_alt_{timestamp}.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 60,  # Longer timeout
                'retries': 5,
                'fragment_retries': 5,
                'http_chunk_size': 5242880,  # Smaller chunks (5MB)
                'concurrent_fragment_downloads': 1,
                'ignoreerrors': True,  # Ignore errors and continue
                'no_check_certificate': True,
                'prefer_insecure': True,  # Try HTTP first
                'user_agent': 'Instagram 219.0.0.12.117 Android',
                'referer': 'https://www.instagram.com/',
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-us,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                    'Connection': 'keep-alive',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None, None
                
                # Download with alternative settings
                ydl.download([url])
                
                # Find downloaded file
                for file in os.listdir(temp_dir):
                    if file.startswith(f'instagram_alt_{timestamp}') and \
                       file.endswith(('.mp4', '.webm', '.mkv', '.mov', '.m4v')):
                        file_path = os.path.join(temp_dir, file)
                        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                            return file_path, info
                
                return None, None
                
        except Exception as e:
            st.warning(f"Alternative download method failed: {str(e)}")
            return None, None
    
    def extract_audio(self, video_path):
        """Extract audio from video file"""
        try:
            # Load video and extract audio
            video = AudioSegment.from_file(video_path)
            
            # Convert to mono and reduce sample rate to save API costs
            audio = video.set_channels(1).set_frame_rate(16000)
            
            # Save audio file
            audio_path = video_path.replace('.mp4', '.mp3').replace('.webm', '.mp3')
            audio.export(audio_path, format="mp3")
            
            return audio_path
        except Exception as e:
            st.error(f"Error extracting audio: {str(e)}")
            return None
    
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
            return transcript
        except Exception as e:
            st.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def extract_reel_data(self, reel_url, model="whisper-1"):
        """
        Extract complete data from Instagram reel using OpenAI API
        
        Args:
            reel_url (str): Instagram reel URL
            model (str): Whisper model to use
        
        Returns:
            dict: Extracted data from the reel
        """
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Download video
            status_text.text("📥 Downloading Instagram video...")
            progress_bar.progress(20)
            
            video_path, video_info = self.download_instagram_video(reel_url)
            if not video_path:
                # Try alternative download method
                st.warning("Primary download failed, trying alternative method...")
                video_path, video_info = self.download_instagram_video_alternative(reel_url)
                
            if not video_path:
                return {"success": False, "error": "Failed to download video. This could be due to:\n- Private or restricted Instagram account\n- Network connectivity issues\n- Instagram rate limiting\n- Video format not supported\n- Instagram blocking automated downloads\n\nTry again in a few minutes or with a different Instagram reel.", "data": None}
            
            # Step 2: Extract audio
            status_text.text("🎵 Extracting audio from video...")
            progress_bar.progress(40)
            
            audio_path = self.extract_audio(video_path)
            if not audio_path:
                return {"success": False, "error": "Failed to extract audio", "data": None}
            
            # Step 3: Transcribe audio
            status_text.text("🎤 Transcribing audio with OpenAI Whisper...")
            progress_bar.progress(60)
            
            transcript = self.transcribe_audio(audio_path, model)
            if not transcript:
                return {"success": False, "error": "Failed to transcribe audio", "data": None}
            
            # Step 4: Process results
            status_text.text("📊 Processing results...")
            progress_bar.progress(80)
            
            # Clean up temporary files
            try:
                os.remove(video_path)
                os.remove(audio_path)
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
                    "video_title": video_info.get('title', 'Unknown') if video_info else 'Unknown',
                    "uploader": video_info.get('uploader', 'Unknown') if video_info else 'Unknown',
                    "view_count": video_info.get('view_count', 0) if video_info else 0,
                    "like_count": video_info.get('like_count', 0) if video_info else 0,
                    "description": video_info.get('description', '') if video_info else '',
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
        page_title="Instagram Reel Transcript Extractor (OpenAI)",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 Instagram Reel Transcript Extractor")
    st.markdown("Extract complete transcript data from Instagram reels using OpenAI Whisper API")
    
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
                            
                            with col_meta2:
                                st.metric("Views", item["metadata"]["view_count"])
                                st.metric("Likes", item["metadata"]["like_count"])
                                st.metric("Uploader", item["metadata"]["uploader"])
                            
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
        """)
        
        st.header("🔧 Technical Details")
        st.info("""
        **This version uses:**
        - OpenAI Whisper API directly
        - yt-dlp for video downloading
        - pydub for audio processing
        - No third-party API costs!
        """)
        
        st.header("💰 Cost Comparison")
        st.success("""
        **vs Apify ($2/month + usage):**
        - OpenAI: ~$0.006/minute
        - Much cheaper for regular use!
        """)

if __name__ == "__main__":
    main()

