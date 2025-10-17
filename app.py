import streamlit as st
import os
from apify_client import ApifyClient
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstagramReelTranscript:
    def __init__(self):
        self.api_token = os.getenv('APIFY_API_TOKEN')
        if not self.api_token:
            st.error("Please set your APIFY_API_TOKEN in the .env file")
            st.stop()
        
        self.client = ApifyClient(self.api_token)
    
    def extract_reel_data(self, reel_url, task="transcription", model="gpt-4o-mini-transcribe", response_format="json"):
        """
        Extract complete data from Instagram reel using Apify API
        
        Args:
            reel_url (str): Instagram reel URL
            task (str): Task type (transcription, translation, etc.)
            model (str): Model to use for transcription
            response_format (str): Response format (json, text, etc.)
        
        Returns:
            dict: Extracted data from the reel
        """
        try:
            # Prepare the Actor input
            run_input = {
                "urls": [reel_url],
                "task": task,
                "model": model,
                "response_format": response_format,
            }
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Starting transcription...")
            progress_bar.progress(10)
            
            # Run the Actor and wait for it to finish
            status_text.text("Processing reel data...")
            progress_bar.progress(30)
            
            run = self.client.actor("linen_snack/instagram-videos-transcipt-subtitles-and-translate").call(run_input=run_input)
            
            status_text.text("Extracting results...")
            progress_bar.progress(70)
            
            # Fetch results from the run's dataset
            results = []
            dataset_id = run["defaultDatasetId"]
            
            for item in self.client.dataset(dataset_id).iterate_items():
                results.append(item)
            
            progress_bar.progress(100)
            status_text.text("Complete!")
            
            # Clear progress indicators
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            return {
                "success": True,
                "data": results,
                "dataset_url": f"https://console.apify.com/storage/datasets/{dataset_id}",
                "total_items": len(results)
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
    st.markdown("Extract complete transcript data from Instagram reels using AI-powered transcription")
    
    # Initialize the transcript extractor
    if 'extractor' not in st.session_state:
        st.session_state.extractor = InstagramReelTranscript()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        task_options = {
            "transcription": "Transcription Only",
            "translation": "Translation to English",
            "subtitles": "Generate Subtitles"
        }
        
        selected_task = st.selectbox(
            "Select Task Type",
            options=list(task_options.keys()),
            format_func=lambda x: task_options[x]
        )
        
        model_options = {
            "gpt-4o-mini-transcribe": "GPT-4o Mini (Fast)",
            "whisper-1": "Whisper-1 (Standard)",
            "whisper-large-v2": "Whisper Large V2 (High Quality)"
        }
        
        selected_model = st.selectbox(
            "Select Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x]
        )
        
        response_format = st.selectbox(
            "Response Format",
            options=["json", "text", "srt"],
            help="JSON for structured data, text for plain text, SRT for subtitle files"
        )
    
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
                        task=selected_task,
                        model=selected_model,
                        response_format=response_format
                    )
                
                if result["success"]:
                    st.success(f"✅ Successfully extracted data! Found {result['total_items']} items")
                    
                    # Display results
                    st.header("📊 Extracted Data")
                    
                    for i, item in enumerate(result["data"]):
                        with st.expander(f"Item {i+1} - View Details", expanded=True):
                            st.json(item)
                    
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
                        # Download dataset URL
                        st.markdown(f"[🔗 View in Apify Console]({result['dataset_url']})")
                
                else:
                    st.error(f"❌ Error extracting data: {result['error']}")
    
    with col2:
        st.header("ℹ️ Instructions")
        st.markdown("""
        ### How to use:
        1. **Get your Apify API token** from [Apify Console](https://console.apify.com/account/integrations)
        2. **Create a `.env` file** in this directory with:
           ```
           APIFY_API_TOKEN=your_token_here
           ```
        3. **Paste an Instagram reel URL** in the input field
        4. **Configure** your preferences in the sidebar
        5. **Click Extract** to get the transcript data
        
        ### Features:
        - 🎯 **Multiple task types**: Transcription, translation, subtitles
        - 🤖 **AI models**: GPT-4o Mini, Whisper variants
        - 📄 **Export formats**: JSON, text, SRT subtitles
        - 💾 **Download results** directly
        - 🔗 **Apify integration** for advanced usage
        
        ### Supported URLs:
        - Instagram Reels: `https://www.instagram.com/reel/...`
        - Public reels only (private accounts not supported)
        """)
        
        st.header("🔧 API Information")
        st.info("""
        This tool uses the Apify Instagram Reel Transcript API:
        - **Actor**: `linen_snack/instagram-videos-transcipt-subtitles-and-translate`
        - **Pricing**: $2.00/month + usage
        - **Features**: OpenAI Whisper API integration
        """)

if __name__ == "__main__":
    main()

