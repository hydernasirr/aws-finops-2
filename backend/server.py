"""
FastAPI Server for AWS FinOps Agent
Provides REST API endpoints for cost analysis and optimization
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from aws_cost_analyzer import AWSCostAnalyzer
import os

app = FastAPI(title="AWS FinOps Agent", version="1.0.0")

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analyzer instance
analyzer = None


class AWSCredentials(BaseModel):
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    region: str = "us-east-1"


@app.post("/api/configure")
async def configure_credentials(credentials: AWSCredentials):
    """Configure AWS credentials"""
    global analyzer
    try:
        analyzer = AWSCostAnalyzer(
            aws_access_key=credentials.aws_access_key,
            aws_secret_key=credentials.aws_secret_key,
            region=credentials.region
        )
        return {"status": "success", "message": "AWS credentials configured"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "configured": analyzer is not None
    }


@app.get("/api/costs/summary")
async def get_cost_summary(days: int = 30):
    """Get comprehensive cost summary"""
    if not analyzer:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    
    try:
        summary = analyzer.get_monthly_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/costs/by-service")
async def get_costs_by_service(days: int = 30):
    """Get cost breakdown by AWS service"""
    if not analyzer:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    
    try:
        costs = analyzer.get_cost_by_service(days)
        return {"services": costs, "total": sum(costs.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/costs/daily")
async def get_daily_costs(days: int = 30):
    """Get daily cost trend"""
    if not analyzer:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    
    try:
        daily = analyzer.get_daily_costs(days)
        return {"daily_costs": daily}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/forecast")
async def get_forecast(days: int = 30):
    """Get cost forecast"""
    if not analyzer:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    
    try:
        forecast = analyzer.get_forecast_summary(days)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/optimization/unused-resources")
async def get_unused_resources():
    """Get list of unused AWS resources"""
    if not analyzer:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    
    try:
        unused = analyzer.identify_unused_resources()
        return unused
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/optimization/recommendations")
async def get_recommendations():
    """Get cost optimization recommendations"""
    if not analyzer:
        raise HTTPException(status_code=400, detail="AWS credentials not configured")
    
    try:
        recommendations = analyzer.get_optimization_recommendations()
        return {"recommendations": recommendations, "count": len(recommendations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def init_from_env():
    """Initialize analyzer from environment variables if available"""
    global analyzer
    
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if aws_key and aws_secret:
        try:
            analyzer = AWSCostAnalyzer(
                aws_access_key=aws_key,
                aws_secret_key=aws_secret,
                region=region
            )
            print("✓ AWS credentials loaded from environment")
        except Exception as e:
            print(f"✗ Failed to initialize from environment: {e}")
    else:
        print("ℹ No AWS credentials in environment. Use /api/configure endpoint.")


if __name__ == "__main__":
    init_from_env()
    uvicorn.run(app, host="0.0.0.0", port=8000)
