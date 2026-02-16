#!/usr/bin/env python3
"""
Test script to validate AWS FinOps Agent functionality
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from aws_cost_analyzer import AWSCostAnalyzer
import json


def test_analyzer():
    """Test the AWS Cost Analyzer"""
    print("="*50)
    print("AWS FinOps Agent - Validation Test")
    print("="*50)
    print()
    
    # Check for AWS credentials
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not aws_key or not aws_secret:
        print("⚠️  No AWS credentials in environment")
        print("   Will attempt to use default credential chain")
        print()
    
    try:
        # Initialize analyzer
        print("1. Initializing AWS Cost Analyzer...")
        analyzer = AWSCostAnalyzer()
        print("   ✓ Analyzer initialized")
        print()
        
        # Test cost retrieval
        print("2. Testing cost data retrieval...")
        costs = analyzer.get_cost_by_service(7)
        if costs:
            print(f"   ✓ Retrieved costs for {len(costs)} services")
            print(f"   Total spend (last 7 days): ${sum(costs.values()):.2f}")
            if costs:
                top_service = list(costs.items())[0]
                print(f"   Top service: {top_service[0]} (${top_service[1]:.2f})")
        else:
            print("   ⚠️  No cost data retrieved (this may be normal for new accounts)")
        print()
        
        # Test daily costs
        print("3. Testing daily cost trend...")
        daily = analyzer.get_daily_costs(7)
        if daily:
            print(f"   ✓ Retrieved {len(daily)} days of data")
            if daily:
                print(f"   Latest: {daily[-1]['date']} - ${daily[-1]['cost']:.2f}")
        else:
            print("   ⚠️  No daily cost data")
        print()
        
        # Test forecast
        print("4. Testing cost forecast...")
        try:
            forecast = analyzer.get_forecast_summary(7)
            if forecast:
                print(f"   ✓ 7-day forecast: ${forecast.get('total_forecast', 0):.2f}")
            else:
                print("   ⚠️  Forecast not available (requires historical data)")
        except Exception as e:
            print(f"   ⚠️  Forecast unavailable: {str(e)}")
        print()
        
        # Test resource detection
        print("5. Testing unused resource detection...")
        unused = analyzer.identify_unused_resources()
        total_unused = sum(len(v) for v in unused.values())
        print(f"   ✓ Scanned for unused resources")
        print(f"   Found: {unused['ec2_instances'].__len__()} stopped EC2 instances")
        print(f"   Found: {unused['ebs_volumes'].__len__()} unattached EBS volumes")
        print(f"   Found: {unused['elastic_ips'].__len__()} unassociated Elastic IPs")
        print(f"   Found: {unused['rds_instances'].__len__()} stopped RDS instances")
        print()
        
        # Test recommendations
        print("6. Testing optimization recommendations...")
        recommendations = analyzer.get_optimization_recommendations()
        print(f"   ✓ Generated {len(recommendations)} recommendations")
        if recommendations:
            for rec in recommendations[:3]:  # Show first 3
                print(f"   - [{rec['severity']}] {rec['title']}")
        print()
        
        # Test full summary
        print("7. Testing monthly summary...")
        summary = analyzer.get_monthly_summary()
        if summary:
            print("   ✓ Summary generated successfully")
            print(f"   Current month total: ${summary['current_month']['total_cost']:.2f}")
            print(f"   Avg daily cost: ${summary['current_month']['avg_daily_cost']:.2f}")
            print(f"   Optimization opportunities: {summary['optimization']['total_recommendations']}")
            print(f"   Potential savings: ${summary['optimization']['potential_monthly_savings']:.2f}/month")
        print()
        
        print("="*50)
        print("✅ All tests completed successfully!")
        print("="*50)
        print()
        print("Your AWS FinOps Agent is working correctly!")
        print()
        print("Next steps:")
        print("1. Start the backend: cd backend && python server.py")
        print("2. Start the dashboard: cd dashboard && npm start")
        print("3. Open http://localhost:3000")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print()
        print("Common issues:")
        print("- AWS credentials not configured")
        print("- IAM permissions insufficient")
        print("- Cost Explorer not enabled")
        print("- Network/connection issues")
        print()
        print("See README.md for setup instructions")
        return False


if __name__ == "__main__":
    success = test_analyzer()
    sys.exit(0 if success else 1)
