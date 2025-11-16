# 🎬 Instagram Reel Transcript Extractor

A powerful Python application that extracts complete transcript data from Instagram reels using OpenAI's Whisper API. This tool downloads Instagram videos, extracts audio, and provides accurate transcriptions with timestamps.

## ✨ Features

- 🎯 **Direct OpenAI Integration** - No third-party costs, pay only OpenAI directly
- 🤖 **Multiple Whisper Models** - Choose between Whisper-1, Large V2, or Large V3
- 📄 **Timestamped Segments** - Precise timing information for each segment
- 💾 **Multiple Export Formats** - Download as JSON or plain text
- 🎨 **Beautiful UI** - Professional Streamlit interface
- ⚡ **Real-time Processing** - Live progress indicators
- 🔧 **Error Handling** - Robust error management and user feedback
- 💰 **Cost Effective** - Much cheaper than Apify or other services

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- ffmpeg (for audio processing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohammedMidlajPA/instagram-reel-transcript-extractor.git
   cd instagram-reel-transcript-extractor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install ffmpeg:**
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

4. **Set up environment variables:**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application:**
   ```bash
   streamlit run app_openai.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:8501`

## 📋 Usage

1. **Enter Instagram Reel URL** - Paste any Instagram reel link
2. **Select Whisper Model** - Choose quality vs speed trade-off
3. **Click Extract** - Process the video and get transcript
4. **View Results** - See full transcript with timestamps
5. **Download** - Export as JSON or text file

## 💰 Pricing

**OpenAI Whisper API Pricing:**
- Whisper-1: $0.006 per minute
- Whisper Large V2: $0.006 per minute
- Whisper Large V3: $0.006 per minute

*Much cheaper than Apify or other third-party services!*

## 🔧 Technical Details

### Architecture
- **Frontend:** Streamlit web interface
- **Backend:** Python with OpenAI API
- **Video Processing:** yt-dlp for downloading Instagram videos
- **Audio Processing:** pydub with ffmpeg for audio extraction
- **Transcription:** OpenAI Whisper API

### Supported Formats
- **Input:** Instagram Reel URLs
- **Output:** JSON with timestamps, plain text
- **Audio:** MP3, WAV (converted from video)

### Dependencies
- `streamlit` - Web interface
- `openai` - Whisper API integration
- `yt-dlp` - Video downloading
- `pydub` - Audio processing
- `python-dotenv` - Environment variables
- `requests` - HTTP requests
- `numpy` - Numerical operations

## 📁 Project Structure

```
instagram-reel-transcript-extractor/
├── app_openai.py          # Main Streamlit application
├── app.py                 # Original Apify version
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in repo)
├── env_example.txt        # Environment variables template
├── README.md              # This file
├── .gitignore            # Git ignore rules
└── DEPLOYMENT.md          # Deployment instructions
```

## 🛠️ Development

### Running Locally

1. **Start the development server:**
   ```bash
   streamlit run app_openai.py
   ```

2. **Access the application:**
   - Local: `http://localhost:8501`
   - Network: `http://your-ip:8501`

### Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Deployment Options

### 🆓 FREE Hosting - Streamlit Cloud (Recommended)

**100% Free Forever - No Credit Card Required!**

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository
6. Set Main file: `app_openai.py`
7. Add `OPENAI_API_KEY` in Secrets
8. Deploy! Your app will be live at `https://your-app.streamlit.app`

**See [FREE_HOSTING_GUIDE.md](FREE_HOSTING_GUIDE.md) for detailed instructions.**

### Local Development
- Run with Streamlit locally
- Perfect for development and testing
- `streamlit run app_openai.py`

### Alternative Free Hosting
- **Render** - Free tier (apps sleep after inactivity)
- **Railway** - Free $5 credit
- **PythonAnywhere** - Free tier with limitations

### Cloud Deployment (Paid)
- **Railway** - Recommended for Python apps
- **Render** - Good for full-stack applications
- **Heroku** - Traditional PaaS
- **AWS Lambda** - Serverless option
- **Google Cloud Functions** - Alternative serverless

## 🔍 Troubleshooting

### Common Issues

1. **ffmpeg not found:**
   ```bash
   # Install ffmpeg
   brew install ffmpeg  # macOS
   sudo apt install ffmpeg  # Ubuntu
   ```

2. **yt-dlp format error:**
   - The app automatically handles format selection
   - If issues persist, try different Instagram URLs

3. **OpenAI API errors:**
   - Check your API key in `.env`
   - Verify you have sufficient credits
   - Check rate limits

4. **Streamlit email prompt:**
   ```bash
   echo "" | streamlit run app_openai.py
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** - For the amazing Whisper API
- **Streamlit** - For the beautiful web framework
- **yt-dlp** - For video downloading capabilities
- **pydub** - For audio processing

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Open an [Issue](https://github.com/MohammedMidlajPA/instagram-reel-transcript-extractor/issues)
3. Create a [Discussion](https://github.com/MohammedMidlajPA/instagram-reel-transcript-extractor/discussions)

---

**Made with ❤️ for content creators and developers**
