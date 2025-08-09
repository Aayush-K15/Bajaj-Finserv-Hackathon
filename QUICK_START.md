# 🚀 Quick Start Guide - HackRx 6.0 API

## ⚡ One-Click Setup

Run the setup script to automatically configure everything:

```bash
./setup_and_deploy.sh
```

## 🎯 Essential Commands

### 1. Activate Virtual Environment
```bash
source venv-vertex/bin/activate
```

### 2. Test Locally
```bash
# Test Groq integration
python test_groq.py

# Run API locally
python run_local.py
```

### 3. Deploy to Heroku
```bash
# Create Heroku app
heroku create your-hackrx-app-name

# Deploy
git add .
git commit -m "Deploy HackRx 6.0 API"
git push heroku main
```

### 4. Get Your Webhook URL
```
https://your-hackrx-app-name.herokuapp.com/hackrx/run
```

## 📋 Submission Checklist

- [ ] Virtual environment activated
- [ ] Local testing successful
- [ ] API deployed to Heroku/Railway/Render
- [ ] Webhook URL obtained
- [ ] Submitted to HackRx 6.0 platform
- [ ] Platform tests passed

## 🔧 Troubleshooting

### If Virtual Environment Issues
```bash
source venv-vertex/bin/activate
pip install -r requirements.txt
```

### If Deployment Issues
```bash
heroku logs --tail
```

### If API Issues
```bash
# Check if API is running
curl https://your-app.herokuapp.com/health
```

## 📞 Need Help?

1. Check `NEXT_STEPS_GUIDE.md` for detailed instructions
2. Review logs: `heroku logs --tail`
3. Test locally first: `python run_local.py`

---

**🎉 You're Ready to Compete!**
