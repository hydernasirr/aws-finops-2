# Project Structure

```
finops-agent/
├── backend/                          # Python FastAPI backend
│   ├── aws_cost_analyzer.py         # Core AWS Cost Explorer integration
│   ├── server.py                    # FastAPI REST API server
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile                   # Backend container config
│
├── dashboard/                        # React frontend
│   ├── src/
│   │   ├── App.js                   # Main React application
│   │   ├── App.css                  # Dashboard styling
│   │   └── index.js                 # React entry point
│   ├── public/
│   │   └── index.html               # HTML template
│   ├── package.json                 # Node dependencies
│   └── Dockerfile                   # Dashboard container config
│
├── config/                           # Configuration files
│   ├── .env.example                 # Environment variables template
│   └── iam-policy.json              # AWS IAM policy for import
│
├── docker-compose.yml               # Docker orchestration
├── start.sh                         # Quick start script
├── test_agent.py                    # Validation/test script
├── README.md                        # Comprehensive documentation
├── QUICKSTART.md                    # 60-second setup guide
├── .gitignore                       # Git ignore rules
└── PROJECT_STRUCTURE.md            # This file

```

## Component Details

### Backend (`/backend`)

**aws_cost_analyzer.py**
- Core business logic for AWS cost analysis
- AWS SDK (boto3) integration
- Classes:
  - `AWSCostAnalyzer`: Main analyzer class
- Key methods:
  - `get_cost_and_usage()`: Fetch raw cost data
  - `get_cost_by_service()`: Service-level breakdown
  - `get_daily_costs()`: Daily spending trend
  - `forecast_costs()`: ML-powered cost forecasting
  - `identify_unused_resources()`: Waste detection
  - `get_optimization_recommendations()`: Actionable insights
  - `get_monthly_summary()`: Complete analysis

**server.py**
- FastAPI REST API server
- CORS-enabled for dashboard communication
- Endpoints:
  - `GET /api/health`: Health check
  - `POST /api/configure`: Set AWS credentials
  - `GET /api/costs/summary`: Full cost analysis
  - `GET /api/costs/by-service`: Service breakdown
  - `GET /api/costs/daily`: Daily trend
  - `GET /api/forecast`: Cost forecast
  - `GET /api/optimization/unused-resources`: Unused resources
  - `GET /api/optimization/recommendations`: Savings opportunities

### Dashboard (`/dashboard`)

**App.js**
- Main React component
- State management for all data
- API integration
- UI logic for:
  - Credential configuration
  - Data loading and refresh
  - Error handling
  - Rendering all sections

**App.css**
- Complete styling for dashboard
- Responsive design (mobile-friendly)
- Color-coded severity levels
- Professional card-based layout

### Configuration (`/config`)

**.env.example**
- Template for environment variables
- AWS credential configuration
- Region settings

**iam-policy.json**
- IAM policy for AWS permissions
- Ready for direct import to AWS Console
- Follows principle of least privilege

### Scripts

**start.sh**
- Automated startup script
- Detects Docker availability
- Falls back to manual setup if needed
- Cross-platform compatible

**test_agent.py**
- Validates AWS connectivity
- Tests all core functions
- Provides detailed diagnostics
- Helps troubleshoot setup issues

## Data Flow

```
User → Dashboard (React)
         ↓
    REST API (FastAPI)
         ↓
    AWS Cost Analyzer (boto3)
         ↓
    AWS APIs (Cost Explorer, EC2, RDS)
```

## Key Technologies

- **Backend**: Python 3.11, FastAPI, boto3, uvicorn
- **Frontend**: React 18, JavaScript ES6+
- **Deployment**: Docker, Docker Compose
- **Cloud**: AWS Cost Explorer, EC2, RDS APIs

## Security Architecture

1. **Credentials**: Never stored permanently
2. **API**: CORS-enabled but configurable
3. **IAM**: Least-privilege permissions
4. **Environment**: Credentials via env vars or dashboard

## Extensibility

Easy to extend with:
- Additional AWS services (Lambda, S3, etc.)
- Multi-cloud support (Azure, GCP)
- Custom reporting
- Alert integrations (Slack, email)
- Budget tracking
- Historical analysis

## Performance

- **Caching**: Not implemented (can add Redis)
- **Rate Limits**: AWS API limits apply
- **Scalability**: Stateless design, horizontally scalable
- **Response Time**: 1-5 seconds typical (AWS API dependent)

## Deployment Patterns

1. **Local Development**: Manual start (backend + dashboard)
2. **Docker Local**: docker-compose up
3. **Cloud VM**: Deploy to EC2, use IAM roles
4. **Kubernetes**: Scale backend pods
5. **Serverless**: API on Lambda, frontend on S3/CloudFront

## Monitoring & Logs

- Backend: stdout/stderr (JSON logging recommended)
- Dashboard: Browser console
- Docker: `docker-compose logs -f`
- Production: Consider CloudWatch, DataDog, etc.
