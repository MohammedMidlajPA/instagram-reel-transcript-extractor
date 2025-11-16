# Free Hosting Guide - Instagram Reel Transcript Extractor

## Best Option: Streamlit Cloud (100% Free)

Streamlit Cloud is the perfect free hosting solution for your Streamlit app. It's completely free with no credit card required.

### Step 1: Prepare Your Repository

1. Make sure your code is on GitHub
2. Ensure you have these files:
   - `app_openai.py` (main app file)
   - `requirements.txt` (dependencies)
   - `.streamlit/config.toml` (optional config)

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub** (use your GitHub account)
3. **Click "New app"**
4. **Select your repository** from the dropdown
5. **Choose the branch** (usually `main` or `master`)
6. **Set Main file path**: `app_openai.py`
7. **Click "Deploy"**

### Step 3: Add Environment Variables

1. In your Streamlit Cloud app dashboard, click **"Settings"** (⚙️ icon)
2. Click **"Secrets"** tab
3. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Click **"Save"**

### Step 4: Your App is Live!

Your app will be available at:
```
https://your-app-name.streamlit.app
```

## Alternative Free Hosting Options

### Option 2: Render (Free Tier)

**Limitations**: 
- Apps sleep after 15 minutes of inactivity
- 15-minute timeout limit
- Slower cold starts

**Steps**:
1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: reel-transcript
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app_openai.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: OPENAI_API_KEY
        sync: false
```

2. Push to GitHub
3. Connect GitHub repo to Render
4. Deploy

### Option 3: Railway (Free $5 Credit)

**Steps**:
1. Create `Procfile`:
```
web: streamlit run app_openai.py --server.port=$PORT --server.address=0.0.0.0
```

2. Sign up at [railway.app](https://railway.app)
3. Connect GitHub repo
4. Add environment variable: `OPENAI_API_KEY`
5. Deploy

## Recommended: Streamlit Cloud

**Why Streamlit Cloud is Best:**
- ✅ 100% free forever
- ✅ No credit card required
- ✅ Automatic deployments on git push
- ✅ Custom subdomain
- ✅ HTTPS enabled
- ✅ No sleep/wake delays
- ✅ Perfect for Streamlit apps

## Troubleshooting

### Issue: App won't start
- Check that `app_openai.py` is the correct main file
- Verify all dependencies in `requirements.txt`
- Check Streamlit Cloud logs

### Issue: OpenAI API errors
- Verify `OPENAI_API_KEY` is set in Secrets
- Check your OpenAI account has credits
- Verify API key is correct

### Issue: Video download fails
- This is normal - Instagram may block automated downloads
- Try different Instagram reel URLs
- Check network connectivity

## Cost Breakdown

**Hosting**: FREE (Streamlit Cloud)
**OpenAI API**: ~$0.006 per minute of video transcribed
- 1 minute video = $0.006
- 10 minute video = $0.06
- 100 minutes = $0.60

Much cheaper than Apify ($2/month + usage fees)!

## Next Steps

1. Push your code to GitHub
2. Deploy to Streamlit Cloud
3. Add your OpenAI API key
4. Share your app URL!

Your app will automatically update whenever you push to GitHub.

