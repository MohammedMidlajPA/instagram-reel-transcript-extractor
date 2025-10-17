# Vercel Deployment Configuration

## Environment Variables Required

Add these environment variables in your Vercel dashboard:

```
OPENAI_API_KEY=your_openai_api_key_here
```

## Important Notes

⚠️ **Limitations for Vercel Deployment:**

1. **Video Download**: Vercel serverless functions have a 10-second execution limit for hobby plans, which may not be enough for video downloading and processing
2. **File System**: Temporary files may not persist between function calls
3. **Memory Limits**: Video processing requires significant memory
4. **ffmpeg**: Not available in Vercel's serverless environment

## Alternative Deployment Options

For better performance, consider:

1. **Railway**: Better for long-running processes
2. **Render**: Supports background tasks
3. **Google Cloud Run**: More flexible resource allocation
4. **AWS Lambda**: With longer timeout settings
5. **DigitalOcean App Platform**: Full container support

## Quick Vercel Deploy

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Add environment variables in Vercel dashboard
4. Deploy: `vercel --prod`

## Recommended Architecture

For production use, consider:
- Frontend: Vercel (React/Next.js)
- Backend: Railway/Render for video processing
- API communication between services
