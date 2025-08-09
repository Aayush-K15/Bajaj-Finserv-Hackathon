# 🚀 Deployment Options for HackRx 6.0 API

## 🎯 Current Status

✅ **Ready for Deployment!**
- All files committed to Git
- Groq API integration complete
- FastAPI application ready
- Dependencies configured

## 🌐 Deployment Options

### Option 1: Railway (Recommended - Free)

**Steps:**
1. Go to [Railway](https://railway.app/)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Connect your repository: `https://github.com/Aayush-K15/Bajaj-Finserv-Hackathon`
6. Railway will automatically detect Python and deploy

**Benefits:**
- Free tier available
- Automatic deployment
- No credit card required
- Easy setup

### Option 2: Render (Free Tier)

**Steps:**
1. Go to [Render](https://render.com/)
2. Sign up/Login with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Configure:
   - **Name:** `bajaj-bugfinders-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host=0.0.0.0 --port=$PORT`

### Option 3: Heroku (Requires Verification)

**Steps:**
1. Verify your Heroku account at https://heroku.com/verify
2. Add payment information (required for verification)
3. Then run:
   ```bash
   heroku create bajaj-bugfinders
   git push heroku main
   ```

### Option 4: Vercel (Free)

**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel`
3. Follow the prompts

## 🎯 Quick Deployment (Railway)

### Step 1: Deploy to Railway

1. **Visit Railway:** https://railway.app/
2. **Sign up** with GitHub
3. **Create New Project** → "Deploy from GitHub repo"
4. **Select Repository:** `Aayush-K15/Bajaj-Finserv-Hackathon`
5. **Wait for deployment** (2-3 minutes)

### Step 2: Get Your Webhook URL

After deployment, Railway will give you a URL like:
```
https://your-app-name.railway.app
```

Your webhook URL will be:
```
https://your-app-name.railway.app/hackrx/run
```

### Step 3: Test Your API

```bash
# Test health endpoint
curl https://your-app-name.railway.app/health

# Test main endpoint
curl -X POST "https://your-app-name.railway.app/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-api-key" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": ["What is the grace period for premium payment?"]
  }'
```

## 📋 Submission to HackRx 6.0

### Step 1: Get Your Webhook URL
After deployment, your webhook URL will be:
```
https://your-app-name.railway.app/hackrx/run
```

### Step 2: Submit to Platform
1. Go to HackRx 6.0 platform
2. Navigate to "Submissions"
3. Click "Submit"
4. Enter your webhook URL
5. Add description: `FastAPI + Groq API (Llama 3 70B) + FAISS Vector Search + RAG Architecture`
6. Click "Run" to test

## 🔍 Monitoring

### Check Logs
- **Railway:** Dashboard → Your app → Logs
- **Render:** Dashboard → Your service → Logs
- **Heroku:** `heroku logs --tail`

### Monitor Performance
- Response times should be < 30 seconds
- Check for any errors in logs
- Monitor API usage

## 🆘 Troubleshooting

### If Deployment Fails
1. Check if all dependencies are in `requirements.txt`
2. Verify `Procfile` and `runtime.txt` are present
3. Check platform logs for errors

### If API Doesn't Work
1. Test locally first: `python run_local.py`
2. Check if Groq API key is valid
3. Verify all environment variables

## 🎉 Success Criteria

- [ ] API deployed successfully
- [ ] Webhook URL working
- [ ] Platform tests passed
- [ ] Response time < 30 seconds
- [ ] Accuracy > 80%

---

## 🚀 Ready to Deploy!

**Recommended Path:**
1. **Deploy to Railway** (easiest, free)
2. **Get webhook URL**
3. **Submit to HackRx 6.0 platform**
4. **Monitor performance**

Your API is ready for deployment! Choose your preferred platform and follow the steps above.
