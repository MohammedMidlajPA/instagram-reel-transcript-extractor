# 🚀 Deploy Instagram Reel Transcript Extractor to Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Vercel CLI**: Already installed ✅

## Step-by-Step Deployment

### 1. Initialize Vercel Project

```bash
cd "/Users/mohammedmidlajpa/Desktop/reels transcript"
vercel login
vercel init
```

### 2. Configure Environment Variables

In your Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add: `OPENAI_API_KEY` = `your_openai_api_key_here`

### 3. Deploy to Vercel

```bash
vercel --prod
```

## Alternative: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/instagram-reel-transcript)

## Important Limitations

⚠️ **Vercel Serverless Constraints:**

- **File Size Limit**: 50MB max video size
- **Execution Time**: ~30 seconds max
- **Memory Limit**: 1GB RAM
- **No ffmpeg**: Audio processing may be limited

## Optimizations Made

✅ **Vercel-Specific Optimizations:**

- Reduced video size limit to 50MB
- Optimized file handling for serverless
- Better error handling for timeouts
- Streamlined audio processing

## Testing Your Deployment

1. **Visit your Vercel URL**
2. **Paste an Instagram reel URL**
3. **Test with a short video** (< 1 minute)
4. **Check the transcript results**

## Troubleshooting

### Common Issues:

1. **Timeout Errors**: Try shorter videos
2. **Memory Errors**: Reduce video quality
3. **Download Failures**: Check Instagram URL format

### Solutions:

- Use `whisper-1` model for faster processing
- Test with videos under 30 seconds first
- Ensure Instagram reel is public

## Production Recommendations

For production use with larger videos:

1. **Railway**: Better for long-running processes
2. **Render**: Supports background tasks  
3. **Google Cloud Run**: More flexible resources
4. **AWS Lambda**: With longer timeouts

## Cost Analysis

**Vercel Hobby Plan:**
- Free tier: 100GB bandwidth
- $20/month: Pro features
- Serverless functions: Included

**OpenAI Costs:**
- Whisper-1: $0.006/minute
- Much cheaper than Apify!

## Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables
3. Test with shorter videos first
4. Check OpenAI API quota

---

**Ready to deploy? Run `vercel --prod` in your project directory!** 🚀
