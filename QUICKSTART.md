# 🚀 Quick Start (60 seconds)

## Prerequisites
- AWS account with Cost Explorer enabled
- AWS IAM credentials (Access Key + Secret Key)

## Steps

### 1. Setup AWS IAM User (2 minutes)

```bash
# In AWS Console:
1. Go to IAM → Users → Create User
2. Name: finops-agent
3. Attach the policy from config/iam-policy.json
4. Create access keys
5. Save Access Key ID and Secret Access Key
```

### 2. Start the Agent (30 seconds)

**Option A: With Docker (easiest)**
```bash
docker-compose up -d
open http://localhost:3000
```

**Option B: Without Docker**
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python server.py

# Terminal 2 - Dashboard
cd dashboard
npm install
npm start
```

### 3. Configure & Go (30 seconds)

1. Open http://localhost:3000
2. Enter your AWS Access Key ID
3. Enter your AWS Secret Access Key  
4. Select your AWS Region
5. Click "Connect to AWS"

**Done!** The dashboard will automatically load your AWS costs, forecast, and optimization recommendations.

---

## What You'll See

✅ Current month spending  
✅ 30-day cost forecast  
✅ Cost breakdown by AWS service  
✅ Daily spending trend  
✅ Unused resources (stopped EC2, unattached EBS, etc.)  
✅ Optimization recommendations with estimated savings  

---

## Troubleshooting

**"AWS credentials not configured"**  
→ Make sure you entered the credentials in the dashboard

**"Failed to load data"**  
→ Check IAM permissions and ensure Cost Explorer is enabled

**Port already in use**  
→ Change ports in docker-compose.yml or close conflicting apps

---

## Next Steps

- Review optimization recommendations
- Set up scheduled reports (coming soon)
- Enable alerts for cost anomalies (coming soon)

For detailed documentation, see [README.md](README.md)
