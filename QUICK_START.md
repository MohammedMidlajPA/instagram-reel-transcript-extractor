# Quick Start - Free Hosting in 5 Minutes

## Your App is Ready for Free Hosting! 🎉

Your Instagram Reel Transcript Extractor is ready to deploy for FREE using Streamlit Cloud.

## What You Have

✅ **Working App**: `app_openai.py` - Full-featured transcript extractor
✅ **Dependencies**: `requirements.txt` - All packages listed
✅ **Config**: `.streamlit/config.toml` - Streamlit settings
✅ **Deployment Files**: `Procfile`, `render.yaml` - For alternative hosting

## Deploy to Streamlit Cloud (FREE)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Visit**: https://share.streamlit.io
2. **Sign in** with your GitHub account
3. **Click**: "New app"
4. **Select**: Your repository
5. **Main file**: `app_openai.py`
6. **Click**: "Deploy"

### Step 3: Add API Key

1. In your app dashboard, click **⚙️ Settings**
2. Go to **Secrets** tab
3. Add:
   ```
   OPENAI_API_KEY=your_key_here
   ```
4. **Save**

### Step 4: Done! 🚀

Your app is live at: `https://your-app-name.streamlit.app`

## Test Locally First

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY=your_key_here
# Or create .env file with: OPENAI_API_KEY=your_key_here

# Run app
streamlit run app_openai.py
```

## Features

- ✅ Download Instagram reels
- ✅ Extract audio
- ✅ Transcribe with OpenAI Whisper
- ✅ Timestamped segments
- ✅ Export as JSON or TXT
- ✅ Multiple Whisper models
- ✅ Free hosting ready

## Cost

- **Hosting**: FREE (Streamlit Cloud)
- **OpenAI API**: ~$0.006 per minute of video
  - 1 min = $0.006
  - 10 min = $0.06
  - 100 min = $0.60

## Need Help?

See [FREE_HOSTING_GUIDE.md](FREE_HOSTING_GUIDE.md) for detailed instructions.

## Files Overview

- `app_openai.py` - Main application (use this one!)
- `app_minimal.py` - Simplified version (demo)
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `FREE_HOSTING_GUIDE.md` - Detailed hosting guide
- `Procfile` - For Railway/Render deployment
- `render.yaml` - For Render deployment

---

**You're all set! Just push to GitHub and deploy! 🚀**

