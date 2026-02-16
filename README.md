# AWS FinOps Agent

**Production-ready AWS cost optimization and forecasting agent**

Automatically analyzes your AWS spending, forecasts future costs, identifies waste, and provides actionable optimization recommendations.

---

## 🚀 Features

✅ **Real-time Cost Analysis** - Live AWS billing data via Cost Explorer API  
✅ **Cost Forecasting** - ML-powered 30-day cost predictions  
✅ **Waste Detection** - Identifies unused EC2, EBS, RDS, and Elastic IPs  
✅ **Optimization Recommendations** - Actionable savings opportunities  
✅ **Interactive Dashboard** - Clean, responsive UI with real-time data  
✅ **Plug & Play** - Enter AWS credentials and it works immediately  

---

## 📋 Prerequisites

1. **AWS Account** with Cost Explorer enabled
2. **IAM User/Role** with required permissions (see below)
3. **Python 3.9+** and **Node.js 18+** (if running without Docker)
4. **Docker** (optional, for containerized deployment)

---

## 🔐 AWS IAM Permissions Required

Create an IAM user or role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ec2:DescribeInstances",
        "ec2:DescribeVolumes",
        "ec2:DescribeAddresses",
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

**To create the IAM user:**

1. Go to AWS Console → IAM → Users → Create User
2. Name: `finops-agent`
3. Create a custom policy with the JSON above
4. Attach policy to user
5. Create access keys (save the Access Key ID and Secret Access Key)

---

## 🏃 Quick Start (3 Methods)

### Method 1: Docker Compose (Easiest)

```bash
# 1. Clone or download this repository
cd finops-agent

# 2. Set environment variables (optional)
cp config/.env.example .env
# Edit .env with your AWS credentials (or configure via dashboard)

# 3. Start everything
docker-compose up -d

# 4. Open dashboard
open http://localhost:3000
```

### Method 2: Manual Setup

**Backend:**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Optional: Set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# Start server
python server.py
# Server runs on http://localhost:8000
```

**Dashboard:**
```bash
cd dashboard

# Install dependencies
npm install

# Start dashboard
npm start
# Dashboard opens at http://localhost:3000
```

### Method 3: Production Deployment

```bash
# Build for production
cd dashboard
npm run build

# Serve with any static host (nginx, S3, Vercel, etc.)
# Point API calls to your backend server
```

---

## 💻 Usage

### Step 1: Configure AWS Credentials

**Option A: Via Dashboard (Recommended)**
1. Open http://localhost:3000
2. Enter your AWS Access Key ID and Secret Access Key
3. Select AWS Region
4. Click "Connect to AWS"

**Option B: Via Environment Variables**
```bash
# Set these before starting the backend
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_REGION=us-east-1
```

**Option C: Use AWS Default Credentials**
- Leave credentials blank in dashboard
- Backend will use: IAM roles → ~/.aws/credentials → environment variables

### Step 2: View Dashboard

Once connected, the dashboard automatically displays:

- **Current Month Spending** - Total costs and daily average
- **30-Day Forecast** - Predicted future costs
- **Cost by Service** - Breakdown of AWS service spending
- **7-Day Trend** - Recent daily spending chart
- **Optimization Recommendations** - Actionable cost-saving opportunities
- **Potential Savings** - Estimated monthly savings from recommendations

### Step 3: Act on Recommendations

The agent identifies:

- 🔴 **HIGH Priority**: Stopped EC2/RDS instances still incurring costs
- 🟡 **MEDIUM Priority**: Unattached EBS volumes
- 🟢 **LOW Priority**: Unassociated Elastic IPs

Each recommendation includes:
- Specific resource IDs
- Potential savings amount
- Recommended action
- Severity level

---

## 🛠️ API Endpoints

The backend provides a REST API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check and configuration status |
| `/api/configure` | POST | Configure AWS credentials |
| `/api/costs/summary` | GET | Complete cost summary and analysis |
| `/api/costs/by-service` | GET | Cost breakdown by AWS service |
| `/api/costs/daily` | GET | Daily cost trend |
| `/api/forecast` | GET | 30-day cost forecast |
| `/api/optimization/unused-resources` | GET | List of unused resources |
| `/api/optimization/recommendations` | GET | Cost optimization recommendations |

**Example:**
```bash
# Get cost summary
curl http://localhost:8000/api/costs/summary

# Configure credentials
curl -X POST http://localhost:8000/api/configure \
  -H "Content-Type: application/json" \
  -d '{"aws_access_key":"YOUR_KEY","aws_secret_key":"YOUR_SECRET","region":"us-east-1"}'
```

---

## 📊 How It Works

1. **Connects to AWS Cost Explorer API** - Fetches real billing data
2. **Analyzes Spending Patterns** - Daily, service-level breakdown
3. **Forecasts Costs** - Uses AWS ML forecasting (same as AWS Console)
4. **Scans Resources** - Identifies stopped/unused EC2, EBS, RDS, Elastic IPs
5. **Calculates Savings** - Estimates potential monthly savings
6. **Displays Results** - Clean dashboard with actionable insights

---

## 🔒 Security Notes

- **Never commit credentials** - Use environment variables or IAM roles
- **Use least-privilege IAM** - Only grant required permissions
- **Rotate keys regularly** - Best practice for access keys
- **Consider IAM roles** - Better than access keys for EC2/ECS/Lambda
- **Enable MFA** - On IAM users with console access

---

## 🐛 Troubleshooting

**"AWS credentials not configured"**
- Enter credentials via dashboard, or
- Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables

**"Failed to load data"**
- Check IAM permissions (see permissions section above)
- Verify Cost Explorer is enabled (AWS Console → Billing → Cost Explorer)
- Ensure credentials are for the correct AWS account

**"No optimization opportunities found"**
- This is good! Your AWS resources are well-managed
- Try again after running resources for a few days

**Backend won't start**
- Check port 8000 is not in use: `lsof -i :8000`
- Verify Python version: `python --version` (need 3.9+)
- Install dependencies: `pip install -r requirements.txt`

**Dashboard won't start**
- Check port 3000 is not in use: `lsof -i :3000`
- Verify Node version: `node --version` (need 18+)
- Install dependencies: `npm install`

---

## 📈 Cost Optimization Tips

Based on analysis of AWS spending patterns:

1. **Right-size instances** - Use recommendations to downsize overprovisioned resources
2. **Stop unused dev/test** - Schedule or terminate non-production resources
3. **Delete old snapshots** - Remove EBS snapshots older than retention policy
4. **Use Reserved Instances** - 1-3 year commitments for stable workloads
5. **Enable Savings Plans** - Flexible discounts across compute services
6. **Spot Instances** - Save up to 90% on fault-tolerant workloads
7. **S3 Lifecycle Policies** - Move old data to cheaper storage classes

---

## 🤝 Support & Feedback

For issues or questions:
- Check the troubleshooting section above
- Review AWS IAM permissions
- Verify Cost Explorer is enabled in AWS Console

---

## 📝 License

This project is provided as-is for AWS cost optimization purposes.

---

## 🎯 Roadmap

Future enhancements:
- [ ] Multi-region support
- [ ] Reserved Instance recommendations
- [ ] Savings Plans analysis
- [ ] S3 storage optimization
- [ ] Lambda cost analysis
- [ ] Email/Slack alerts
- [ ] Historical trend analysis
- [ ] Budget tracking

---

**Built for AWS FinOps Excellence** 🚀
