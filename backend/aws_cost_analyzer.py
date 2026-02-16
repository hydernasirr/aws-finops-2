"""
AWS Cost Analyzer - Core module for fetching and analyzing AWS costs
"""
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
from decimal import Decimal


class AWSCostAnalyzer:
    """Main class for AWS cost analysis and optimization"""
    
    def __init__(self, aws_access_key: str = None, aws_secret_key: str = None, region: str = 'us-east-1'):
        """
        Initialize AWS Cost Explorer client
        
        Args:
            aws_access_key: AWS Access Key ID (if None, uses default credentials)
            aws_secret_key: AWS Secret Access Key (if None, uses default credentials)
            region: AWS region for Cost Explorer (default: us-east-1)
        """
        if aws_access_key and aws_secret_key:
            self.ce_client = boto3.client(
                'ce',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            self.ec2_client = boto3.client(
                'ec2',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
            self.rds_client = boto3.client(
                'rds',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region
            )
        else:
            # Use default credential chain
            self.ce_client = boto3.client('ce', region_name=region)
            self.ec2_client = boto3.client('ec2', region_name=region)
            self.rds_client = boto3.client('rds', region_name=region)
    
    def get_cost_and_usage(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get cost and usage data for the specified time period
        
        Args:
            days_back: Number of days to look back (default: 30)
            
        Returns:
            Dictionary containing cost and usage data
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            return response
        except Exception as e:
            print(f"Error fetching cost data: {e}")
            return {}
    
    def get_cost_by_service(self, days_back: int = 30) -> Dict[str, float]:
        """
        Get total cost breakdown by AWS service
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary mapping service names to total costs
        """
        data = self.get_cost_and_usage(days_back)
        service_costs = {}
        
        if 'ResultsByTime' in data:
            for result in data['ResultsByTime']:
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    service_costs[service] = service_costs.get(service, 0) + cost
        
        return dict(sorted(service_costs.items(), key=lambda x: x[1], reverse=True))
    
    def get_daily_costs(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily cost breakdown
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            List of dictionaries with date and cost information
        """
        data = self.get_cost_and_usage(days_back)
        daily_costs = []
        
        if 'ResultsByTime' in data:
            for result in data['ResultsByTime']:
                date = result['TimePeriod']['Start']
                total_cost = sum(
                    float(group['Metrics']['UnblendedCost']['Amount'])
                    for group in result.get('Groups', [])
                )
                daily_costs.append({
                    'date': date,
                    'cost': round(total_cost, 2)
                })
        
        return daily_costs
    
    def forecast_costs(self, days_forward: int = 30) -> Dict[str, Any]:
        """
        Forecast future costs using AWS Cost Explorer forecast
        
        Args:
            days_forward: Number of days to forecast
            
        Returns:
            Dictionary containing forecast data
        """
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_forward)
        
        try:
            response = self.ce_client.get_cost_forecast(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Metric='UNBLENDED_COST',
                Granularity='DAILY'
            )
            return response
        except Exception as e:
            print(f"Error forecasting costs: {e}")
            return {}
    
    def get_forecast_summary(self, days_forward: int = 30) -> Dict[str, float]:
        """
        Get summarized forecast information
        
        Args:
            days_forward: Number of days to forecast
            
        Returns:
            Dictionary with forecast summary
        """
        forecast_data = self.forecast_costs(days_forward)
        
        if 'ForecastResultsByTime' not in forecast_data:
            return {}
        
        total_forecast = sum(
            float(result['MeanValue'])
            for result in forecast_data['ForecastResultsByTime']
        )
        
        return {
            'total_forecast': round(total_forecast, 2),
            'days': days_forward,
            'daily_average': round(total_forecast / days_forward, 2)
        }
    
    def identify_unused_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify potentially unused AWS resources
        
        Returns:
            Dictionary of unused resources by type
        """
        unused = {
            'ec2_instances': [],
            'ebs_volumes': [],
            'elastic_ips': [],
            'rds_instances': []
        }
        
        try:
            # Check for stopped EC2 instances
            ec2_response = self.ec2_client.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
            )
            
            for reservation in ec2_response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    unused['ec2_instances'].append({
                        'id': instance['InstanceId'],
                        'type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'].isoformat()
                    })
            
            # Check for unattached EBS volumes
            volumes = self.ec2_client.describe_volumes(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )
            
            for volume in volumes.get('Volumes', []):
                unused['ebs_volumes'].append({
                    'id': volume['VolumeId'],
                    'size': volume['Size'],
                    'type': volume['VolumeType'],
                    'created': volume['CreateTime'].isoformat()
                })
            
            # Check for unassociated Elastic IPs
            addresses = self.ec2_client.describe_addresses()
            
            for address in addresses.get('Addresses', []):
                if 'AssociationId' not in address:
                    unused['elastic_ips'].append({
                        'ip': address['PublicIp'],
                        'allocation_id': address.get('AllocationId', 'N/A')
                    })
            
            # Check for stopped RDS instances
            rds_response = self.rds_client.describe_db_instances()
            
            for db in rds_response.get('DBInstances', []):
                if db['DBInstanceStatus'] == 'stopped':
                    unused['rds_instances'].append({
                        'id': db['DBInstanceIdentifier'],
                        'class': db['DBInstanceClass'],
                        'engine': db['Engine'],
                        'status': db['DBInstanceStatus']
                    })
        
        except Exception as e:
            print(f"Error identifying unused resources: {e}")
        
        return unused
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate cost optimization recommendations
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        unused = self.identify_unused_resources()
        
        # Recommendations for unused EC2 instances
        if unused['ec2_instances']:
            total_stopped = len(unused['ec2_instances'])
            recommendations.append({
                'category': 'EC2',
                'severity': 'HIGH',
                'title': f'{total_stopped} Stopped EC2 Instance(s)',
                'description': f'You have {total_stopped} stopped EC2 instances that are still incurring EBS costs.',
                'action': 'Terminate unused instances or create AMIs and terminate.',
                'potential_savings': 'Varies by instance type',
                'resources': [inst['id'] for inst in unused['ec2_instances']]
            })
        
        # Recommendations for unattached volumes
        if unused['ebs_volumes']:
            total_volumes = len(unused['ebs_volumes'])
            total_size = sum(vol['size'] for vol in unused['ebs_volumes'])
            # EBS gp3 costs ~$0.08/GB-month
            estimated_savings = round(total_size * 0.08, 2)
            
            recommendations.append({
                'category': 'EBS',
                'severity': 'MEDIUM',
                'title': f'{total_volumes} Unattached EBS Volume(s)',
                'description': f'{total_volumes} EBS volumes ({total_size} GB total) are not attached to any instance.',
                'action': 'Delete unused volumes after creating snapshots if needed.',
                'potential_savings': f'~${estimated_savings}/month',
                'resources': [vol['id'] for vol in unused['ebs_volumes']]
            })
        
        # Recommendations for unassociated Elastic IPs
        if unused['elastic_ips']:
            total_ips = len(unused['elastic_ips'])
            # Elastic IPs cost $0.005/hour when not associated (~$3.60/month)
            estimated_savings = round(total_ips * 3.60, 2)
            
            recommendations.append({
                'category': 'Network',
                'severity': 'LOW',
                'title': f'{total_ips} Unassociated Elastic IP(s)',
                'description': f'{total_ips} Elastic IPs are not associated with any resource.',
                'action': 'Release unused Elastic IPs.',
                'potential_savings': f'~${estimated_savings}/month',
                'resources': [ip['ip'] for ip in unused['elastic_ips']]
            })
        
        # Recommendations for stopped RDS instances
        if unused['rds_instances']:
            total_stopped_rds = len(unused['rds_instances'])
            recommendations.append({
                'category': 'RDS',
                'severity': 'HIGH',
                'title': f'{total_stopped_rds} Stopped RDS Instance(s)',
                'description': f'{total_stopped_rds} RDS instances are stopped but still incurring storage costs.',
                'action': 'Take snapshots and terminate if not needed, or start if actively used.',
                'potential_savings': 'Varies by instance class',
                'resources': [db['id'] for db in unused['rds_instances']]
            })
        
        return recommendations
    
    def get_monthly_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive monthly cost summary
        
        Returns:
            Dictionary with complete monthly analysis
        """
        # Current month costs
        current_month_costs = self.get_cost_by_service(30)
        daily_costs = self.get_daily_costs(30)
        
        # Calculate totals
        total_current = sum(current_month_costs.values())
        avg_daily = total_current / 30 if len(daily_costs) > 0 else 0
        
        # Forecast
        forecast = self.get_forecast_summary(30)
        
        # Optimization opportunities
        recommendations = self.get_optimization_recommendations()
        total_potential_savings = sum(
            float(rec['potential_savings'].replace('~$', '').replace('/month', ''))
            for rec in recommendations
            if '/month' in rec.get('potential_savings', '')
        )
        
        return {
            'current_month': {
                'total_cost': round(total_current, 2),
                'avg_daily_cost': round(avg_daily, 2),
                'top_services': dict(list(current_month_costs.items())[:5])
            },
            'forecast': forecast,
            'optimization': {
                'total_recommendations': len(recommendations),
                'potential_monthly_savings': round(total_potential_savings, 2),
                'recommendations': recommendations
            },
            'daily_trend': daily_costs[-7:]  # Last 7 days
        }


def main():
    """Example usage"""
    analyzer = AWSCostAnalyzer()
    
    print("Fetching AWS cost data...")
    summary = analyzer.get_monthly_summary()
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
