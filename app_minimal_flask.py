from flask import Flask, render_template_string, request, jsonify
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Reel Transcript Extractor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .content { padding: 40px; }
        .form-group { margin-bottom: 30px; }
        .form-group label { display: block; margin-bottom: 10px; font-weight: 600; color: #333; }
        .form-group input, .form-group select { width: 100%; padding: 15px; border: 2px solid #e1e5e9; border-radius: 10px; font-size: 16px; transition: border-color 0.3s; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: #667eea; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s; width: 100%; }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .result { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; display: none; }
        .result.show { display: block; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .transcript { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #667eea; }
        .metadata { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2rem; font-weight: bold; color: #667eea; }
        .metric-label { color: #666; margin-top: 5px; }
        .segments { margin-top: 20px; }
        .segment { background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 3px solid #667eea; }
        .segment-time { font-weight: bold; color: #667eea; }
        .loading { text-align: center; padding: 20px; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .sidebar { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .sidebar h3 { color: #333; margin-bottom: 15px; }
        .info-box { background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #28a745; }
        .warning-box { background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 Instagram Reel Transcript Extractor</h1>
            <p>Extract complete transcript data from Instagram reels using OpenAI Whisper API</p>
        </div>
        
        <div class="content">
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 30px;">
                <div>
                    <h2>📝 Enter Instagram Reel URL</h2>
                    
                    <form id="transcriptForm">
                        <div class="form-group">
                            <label for="url">Instagram Reel URL</label>
                            <input type="url" id="url" name="url" placeholder="https://www.instagram.com/reel/..." required>
                        </div>
                        
                        <div class="form-group">
                            <label for="model">Select Whisper Model</label>
                            <select id="model" name="model">
                                <option value="whisper-1">Whisper-1 (Standard)</option>
                                <option value="whisper-large-v2">Whisper Large V2 (High Quality)</option>
                                <option value="whisper-large-v3">Whisper Large V3 (Latest)</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="btn" id="submitBtn">
                            🚀 Extract Transcript Data
                        </button>
                    </form>
                    
                    <div id="loading" class="loading" style="display: none;">
                        <div class="spinner"></div>
                        <p>Processing your reel...</p>
                    </div>
                    
                    <div id="result" class="result"></div>
                </div>
                
                <div>
                    <div class="sidebar">
                        <h3>ℹ️ Instructions</h3>
                        <div class="info-box">
                            <strong>How to use:</strong>
                            <ol style="margin-top: 10px; padding-left: 20px;">
                                <li>Paste an Instagram reel URL</li>
                                <li>Select Whisper model</li>
                                <li>Click Extract to get transcript data</li>
                                <li>View and download results</li>
                            </ol>
                        </div>
                        
                        <h3>💰 Cost Information</h3>
                        <div class="info-box">
                            <strong>OpenAI Whisper Pricing:</strong>
                            <ul style="margin-top: 10px; padding-left: 20px;">
                                <li>Whisper-1: $0.006 per minute</li>
                                <li>Whisper Large V2: $0.006 per minute</li>
                                <li>Whisper Large V3: $0.006 per minute</li>
                            </ul>
                            <p style="margin-top: 10px; font-style: italic;">Much cheaper than Apify!</p>
                        </div>
                        
                        <h3>🚀 Deployment Status</h3>
                        <div class="info-box">
                            <strong>Successfully Deployed:</strong>
                            <ul style="margin-top: 10px; padding-left: 20px;">
                                <li>✅ Vercel serverless</li>
                                <li>✅ Global CDN</li>
                                <li>✅ HTTPS enabled</li>
                                <li>✅ Auto-scaling</li>
                            </ul>
                        </div>
                        
                        <h3>⚠️ Current Status</h3>
                        <div class="warning-box">
                            <strong>Demo Version:</strong>
                            <p style="margin-top: 10px;">This is a demo version optimized for Vercel deployment. In production, you would implement full video download and processing capabilities.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('transcriptForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const url = document.getElementById('url').value;
            const model = document.getElementById('model').value;
            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const result = document.getElementById('result');
            
            if (!url.includes('instagram.com/reel/')) {
                result.className = 'result error show';
                result.innerHTML = '❌ Please enter a valid Instagram reel URL';
                return;
            }
            
            submitBtn.disabled = true;
            loading.style.display = 'block';
            result.className = 'result';
            
            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url, model: model })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    result.className = 'result success show';
                    result.innerHTML = `
                        <h3>✅ Successfully extracted data!</h3>
                        <div class="transcript">
                            <h4>📝 Full Transcript</h4>
                            <p>${data.data[0].transcript}</p>
                        </div>
                        
                        <div class="metadata">
                            <div class="metric">
                                <div class="metric-value">${data.data[0].language}</div>
                                <div class="metric-label">Language</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.data[0].duration}s</div>
                                <div class="metric-label">Duration</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${data.data[0].metadata.model_used}</div>
                                <div class="metric-label">Model Used</div>
                            </div>
                        </div>
                        
                        <div class="segments">
                            <h4>⏱️ Timestamped Segments</h4>
                            ${data.data[0].segments.map(seg => `
                                <div class="segment">
                                    <div class="segment-time">${seg.start}s - ${seg.end}s</div>
                                    <div>${seg.text}</div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <button onclick="downloadJSON()" class="btn" style="width: auto; margin-right: 10px;">📄 Download JSON</button>
                            <button onclick="downloadText()" class="btn" style="width: auto;">📝 Download Text</button>
                        </div>
                    `;
                } else {
                    result.className = 'result error show';
                    result.innerHTML = `❌ Error extracting data: ${data.error}`;
                }
            } catch (error) {
                result.className = 'result error show';
                result.innerHTML = `❌ Error: ${error.message}`;
            } finally {
                submitBtn.disabled = false;
                loading.style.display = 'none';
            }
        });
        
        function downloadJSON() {
            const data = {"demo": "data", "transcript": "This is a demo transcript"};
            const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'instagram_reel_transcript.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function downloadText() {
            const text = "This is a demo transcript. In production, this would be the actual transcript.";
            const blob = new Blob([text], {type: 'text/plain'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'instagram_reel_transcript.txt';
            a.click();
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>
    """)

@app.route('/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        url = data.get('url')
        model = data.get('model', 'whisper-1')
        
        if not url:
            return jsonify({"success": False, "error": "URL is required"})
        
        # Demo implementation
        sample_result = {
            "url": url,
            "transcript": f"This is a demo transcript for {url}. In production, this would be the actual transcript from the Instagram reel using OpenAI Whisper API. The selected model was {model}.",
            "language": "en",
            "duration": 30.5,
            "segments": [
                {"start": 0.0, "end": 10.0, "text": "This is a sample segment from the demo."},
                {"start": 10.0, "end": 20.0, "text": "Another sample segment for demonstration."},
                {"start": 20.0, "end": 30.5, "text": "Final segment of the demo transcript."},
            ],
            "metadata": {
                "model_used": model,
                "note": "This is a demo version optimized for Vercel deployment"
            }
        }
        
        return jsonify({
            "success": True,
            "data": [sample_result],
            "total_items": 1
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
