import streamlit as st
import os
import tempfile
import requests
from openai import OpenAI
import yt_dlp
import subprocess
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstagramReelTranscript:
    def __init__(self):
        pass
    
    def normalize_instagram_url(self, url):
        """Normalize Instagram URL to handle all formats"""
        if not url:
            return None
        
        # Remove whitespace
        url = url.strip()
        
        # Handle different Instagram URL formats
        # Support: reel/, p/, tv/, with/without www, with/without https
        instagram_patterns = [
            r'https?://(www\.)?instagram\.com/(reel|p|tv)/([A-Za-z0-9_-]+)',
            r'instagram\.com/(reel|p|tv)/([A-Za-z0-9_-]+)',
            r'(reel|p|tv)/([A-Za-z0-9_-]+)',
        ]
        
        import re
        # Extract the post ID from any format
        for pattern in instagram_patterns:
            match = re.search(pattern, url)
            if match:
                post_type = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                post_id = match.group(3) if len(match.groups()) >= 3 else match.group(2)
                
                # Normalize to standard format
                normalized = f"https://www.instagram.com/{post_type}/{post_id}/"
                return normalized
        
        # If no pattern matches, try to clean the URL
        if 'instagram.com' in url:
            # Remove query parameters and fragments
            url = url.split('?')[0].split('#')[0]
            # Ensure it ends with /
            if not url.endswith('/'):
                url += '/'
            # Ensure https://
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        
        return None
    
    def validate_instagram_url(self, url):
        """Validate if URL is a valid Instagram URL"""
        if not url:
            return False, "URL is empty"
        
        normalized = self.normalize_instagram_url(url)
        if not normalized:
            return False, "Invalid Instagram URL format"
        
        # Check if it's a supported type (reel, p, tv)
        if '/reel/' in normalized or '/p/' in normalized or '/tv/' in normalized:
            return True, normalized
        
        return False, "URL must be an Instagram reel, post, or TV video"
    
    def _init_openai_client(self):
        """Initialize OpenAI client - separated to avoid issues with __init__"""
        # Check Streamlit secrets first (for Streamlit Cloud), then environment variables
        try:
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                self.openai_key = st.secrets['OPENAI_API_KEY']
            else:
                self.openai_key = os.getenv('OPENAI_API_KEY')
        except Exception:
            # Fallback to environment variable if secrets access fails
            self.openai_key = os.getenv('OPENAI_API_KEY')
        
        # Validate API key
        if not self.openai_key:
            st.error("⚠️ **OpenAI API Key not found!**")
            st.markdown("""
            **For Streamlit Cloud:**
            1. Go to your app dashboard
            2. Click ⚙️ **Settings** → **Secrets**
            3. Add: `OPENAI_API_KEY = "your_key_here"`
            4. Click **Save**
            
            **For local development:**
            - Create a `.env` file with: `OPENAI_API_KEY=your_key_here`
            """)
            st.stop()
        
        # Validate API key format (should start with sk-)
        if not isinstance(self.openai_key, str) or not self.openai_key.strip():
            st.error("⚠️ **Invalid API Key Format!**")
            st.markdown("The API key appears to be empty or invalid. Please check your Streamlit Secrets.")
            st.stop()
        
        # Initialize OpenAI client with error handling
        # Use minimal initialization to avoid version conflicts
        try:
            # Just use API key - this works with all OpenAI library versions
            self.client = OpenAI(api_key=self.openai_key.strip())
        except TypeError as e:
            # Handle version compatibility issues
            error_msg = str(e)
            if 'proxies' in error_msg or 'unexpected keyword' in error_msg:
                st.error("⚠️ **OpenAI Library Version Issue**")
                st.markdown(f"""
                **Error:** {error_msg}
                
                This is a version compatibility issue. The fix has been deployed.
                Streamlit Cloud will automatically update dependencies.
                
                **If the error persists:**
                1. Wait a few minutes for Streamlit Cloud to rebuild
                2. Check that requirements.txt has: `openai>=1.12.0`
                3. The app should work after the rebuild completes
                """)
            else:
                st.error(f"⚠️ **Error initializing OpenAI client:** {error_msg}")
                st.markdown("""
                **Please check:**
                1. Your API key is correct in Streamlit Secrets
                2. The API key format is: `OPENAI_API_KEY = "sk-..."`
                3. Your OpenAI account has credits
                """)
            st.stop()
        except Exception as e:
            st.error(f"⚠️ **Error initializing OpenAI client:** {str(e)}")
            st.markdown("""
            **Please check:**
            1. Your API key is correct in Streamlit Secrets
            2. The API key format is: `OPENAI_API_KEY = "sk-..."`
            3. Your OpenAI account has credits
            """)
            st.stop()
    
    def download_instagram_video(self, url):
        """Download Instagram video using yt-dlp with improved error handling"""
        # Normalize URL first
        is_valid, normalized_url = self.validate_instagram_url(url)
        if not is_valid:
            return None, None
        
        url = normalized_url
        max_retries = 5  # Increased retries
        retry_delay = 5  # Longer delay between retries
        
        for attempt in range(max_retries):
            try:
                # Create a unique temporary file path
                temp_dir = tempfile.gettempdir()
                timestamp = int(time.time())
                temp_filename = f"instagram_video_{timestamp}.%(ext)s"
                
                # Configure yt-dlp options with better error handling
                # Updated for Instagram's stricter access requirements
                ydl_opts = {
                    'format': 'best[height<=720]/best/worst',  # Prefer lower resolution, fallback to best, then worst
                    'outtmpl': os.path.join(temp_dir, temp_filename),
                    'quiet': True,  # Quiet mode to avoid issues
                    'no_warnings': True,
                    'extract_flat': False,
                    'socket_timeout': 120,  # Increased timeout for Instagram
                    'retries': 10,  # More retries
                    'fragment_retries': 10,  # More fragment retries
                    'http_chunk_size': 10485760,  # 10MB chunks
                    'concurrent_fragment_downloads': 1,  # Single thread to avoid pipe issues
                    'ignoreerrors': False,
                    'no_check_certificate': False,  # Use proper certificates
                    'prefer_insecure': False,
                    # Updated user agent to look more like a real browser
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    # Add referer to look more legitimate
                    'referer': 'https://www.instagram.com/',
                    # Additional headers to bypass some restrictions
                    'headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Cache-Control': 'max-age=0',
                    },
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
                # Check if it's a rate limit or login required error
                is_rate_limit = 'rate-limit' in error_msg.lower() or 'login required' in error_msg.lower()
                
                if is_rate_limit:
                    st.warning(f"⚠️ Attempt {attempt + 1}/{max_retries}: Instagram rate limit detected")
                else:
                    st.warning(f"Attempt {attempt + 1}/{max_retries} failed: {error_msg[:100]}...")
                
                if attempt < max_retries - 1:
                    # Longer delay for rate limits
                    delay = retry_delay * (attempt + 1) if is_rate_limit else retry_delay
                    st.info(f"⏳ Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                else:
                    st.error(f"❌ All {max_retries} attempts failed. Last error: {error_msg[:200]}")
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
        """Extract audio from video file using ffmpeg"""
        try:
            # Generate audio file path
            audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
            
            # Use ffmpeg to extract audio
            # Convert to mono, 16kHz sample rate to save API costs
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ac', '1',  # Mono channel
                '-ar', '16000',  # 16kHz sample rate
                '-y',  # Overwrite output file
                audio_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(audio_path):
                return audio_path
            else:
                st.error(f"Audio extraction failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            st.error("Audio extraction timeout")
            return None
        except Exception as e:
            st.error(f"Error extracting audio: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path, model="whisper-1"):
        """Transcribe audio using OpenAI Whisper API"""
        # Initialize client if not already done
        if not hasattr(self, 'client'):
            self._init_openai_client()
        
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
                return {
                    "success": False, 
                    "error": """❌ **Failed to download Instagram video**

**Common reasons:**
- 🔒 **Private or restricted account** - The reel must be from a public account
- ⏱️ **Instagram rate limiting** - Instagram may temporarily block automated access
- 🚫 **Instagram blocking** - Instagram actively blocks automated downloads
- 🌐 **Network issues** - Connection problems or timeouts

**Solutions to try:**
1. ✅ Make sure the Instagram account is **public**
2. ⏳ **Wait 10-15 minutes** and try again (rate limit resets)
3. 🔄 Try a **different Instagram reel** URL
4. 📱 Use a reel from a **different account**

**Note:** Instagram has strict anti-bot measures. Some reels may not be accessible via automated tools. This is an Instagram limitation, not an issue with this app.

**Alternative:** You can download the video manually and use other transcription tools.""", 
                    "data": None
                }
            
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
        try:
            extractor = InstagramReelTranscript()
            extractor._init_openai_client()  # Initialize OpenAI client
            st.session_state.extractor = extractor
        except Exception as e:
            st.error(f"Error initializing app: {str(e)}")
            st.stop()
    
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
            "Instagram URL",
            placeholder="https://www.instagram.com/reel/... or instagram.com/p/...",
            help="Paste any Instagram reel, post, or TV video URL"
        )
        
        st.caption("Supports: reel/, p/, tv/ - with or without www, with or without https")
        
        # Extract button
        if st.button("🚀 Extract Transcript Data", type="primary", use_container_width=True):
            if not reel_url:
                st.error("Please enter an Instagram URL")
            else:
                try:
                    # Ensure extractor is initialized
                    if 'extractor' not in st.session_state or not hasattr(st.session_state.extractor, 'validate_instagram_url'):
                        extractor = InstagramReelTranscript()
                        extractor._init_openai_client()
                        st.session_state.extractor = extractor
                    
                    # Validate and normalize URL
                    is_valid, result = st.session_state.extractor.validate_instagram_url(reel_url)
                    if not is_valid:
                        st.error(f"❌ {result}")
                        st.info("""
                        **Supported Instagram URL formats:**
                        - `https://www.instagram.com/reel/ABC123/`
                        - `https://instagram.com/p/ABC123/`
                        - `https://www.instagram.com/tv/ABC123/`
                        - `instagram.com/reel/ABC123`
                        - `reel/ABC123`
                        """)
                    else:
                        # Use normalized URL
                        normalized_url = result
                        with st.spinner("Processing your Instagram video..."):
                            result = st.session_state.extractor.extract_reel_data(
                                reel_url=normalized_url,
                                model=selected_model
                            )
                except AttributeError as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Reinitializing extractor...")
                    try:
                        extractor = InstagramReelTranscript()
                        extractor._init_openai_client()
                        st.session_state.extractor = extractor
                        st.rerun()
                    except Exception as e2:
                        st.error(f"Failed to initialize: {str(e2)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
                    st.info("Please try again or refresh the page.")
                
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
        - **Reels**: `instagram.com/reel/...`
        - **Posts**: `instagram.com/p/...`
        - **TV Videos**: `instagram.com/tv/...`
        - Works with or without `www` and `https://`
        - Public content only
        """)
        
        st.header("🔧 Technical Details")
        st.info("""
        **This version uses:**
        - OpenAI Whisper API directly
        - yt-dlp for video downloading
        - ffmpeg for audio processing
        - No third-party API costs!
        
        **Note:** Instagram may block automated downloads due to rate limiting.
        Make sure reels are from public accounts.
        """)
        
        st.header("💰 Cost Comparison")
        st.success("""
        **vs Apify ($2/month + usage):**
        - OpenAI: ~$0.006/minute
        - Much cheaper for regular use!
        """)

if __name__ == "__main__":
    main()

