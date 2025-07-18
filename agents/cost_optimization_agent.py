"""
AI Agent 3: Cost Optimization Agent
Analyzes Azure architecture and applies Microsoft's cost optimization framework
Optimizes resources based on environment (development/production) before Bicep generation
"""

import json
import os
from typing import Dict, List, Any, Tuple, Optional
import openai
from dotenv import load_dotenv
import hashlib

load_dotenv()

class CostOptimizationAgent:
    def __init__(self):
        # Check if Azure AI Foundry configuration is available
        self.azure_endpoint = os.getenv('AZURE_AI_AGENT3_ENDPOINT')
        self.azure_key = os.getenv('AZURE_AI_AGENT3_KEY')
        self.azure_deployment = os.getenv('AZURE_AI_AGENT3_DEPLOYMENT', 'gpt-4')
        
        if self.azure_endpoint and self.azure_key:
            # Use Azure AI Foundry endpoint
            self.openai_client = openai.AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.azure_key,
                api_version="2024-02-01"
            )
            self.model_name = self.azure_deployment
            print(f"✅ Cost Optimization Agent: Using Azure AI Foundry endpoint")
        else:
            # Fallback to OpenAI
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.model_name = "gpt-4"
            print(f"⚠️ Cost Optimization Agent: Using OpenAI fallback (configure Azure AI Foundry for production)")
        
        # Load Microsoft Cost Optimization Framework
        self.cost_optimization_framework = self._load_cost_optimization_framework()
        
        # Cache for optimization recommendations
        self._optimization_cache = {}
        self._max_cache_size = 50

    def _load_cost_optimization_framework(self) -> Dict[str, Any]:
        """Load Microsoft's Well-Architected Framework cost optimization principles"""
        return {
            "principles": {
                "right_sizing": {
                    "description": "Choose the right resources for your workload",
                    "strategies": [
                        "Start small and scale up based on actual usage",
                        "Use monitoring data to right-size resources",
                        "Consider burstable instances for variable workloads",
                        "Use appropriate storage tiers"
                    ]
                },
                "reserved_capacity": {
                    "description": "Use reserved instances and capacity for predictable workloads",
                    "strategies": [
                        "Purchase reserved instances for production workloads",
                        "Use Azure Hybrid Benefit for Windows/SQL licensing",
                        "Consider savings plans for flexible workloads"
                    ]
                },
                "spot_instances": {
                    "description": "Use spot instances for fault-tolerant workloads",
                    "strategies": [
                        "Use spot VMs for development/testing",
                        "Use spot instances for batch processing",
                        "Implement proper handling for interruptions"
                    ]
                },
                "automation": {
                    "description": "Automate resource management and scaling",
                    "strategies": [
                        "Auto-shutdown dev/test resources",
                        "Use auto-scaling for production workloads",
                        "Implement lifecycle management for storage"
                    ]
                },
                "monitoring": {
                    "description": "Monitor and optimize continuously",
                    "strategies": [
                        "Use Azure Cost Management and Billing",
                        "Set up cost alerts and budgets",
                        "Regular cost reviews and optimization"
                    ]
                }
            },
            "environment_strategies": {
                "development": {
                    "vm_sizes": ["Standard_B1s", "Standard_B2s", "Standard_D2s_v3"],
                    "app_service_tiers": ["F1", "D1", "B1"],
                    "sql_tiers": ["Basic", "S0"],
                    "storage_tiers": ["Standard_LRS"],
                    "features": {
                        "auto_shutdown": True,
                        "dev_test_pricing": True,
                        "minimal_redundancy": True,
                        "shared_resources": True
                    }
                },
                "staging": {
                    "vm_sizes": ["Standard_B2s", "Standard_D2s_v3", "Standard_D4s_v3"],
                    "app_service_tiers": ["B1", "B2", "S1"],
                    "sql_tiers": ["S0", "S1"],
                    "storage_tiers": ["Standard_LRS", "Standard_ZRS"],
                    "features": {
                        "auto_shutdown": False,
                        "dev_test_pricing": False,
                        "moderate_redundancy": True,
                        "shared_resources": False
                    }
                },
                "production": {
                    "vm_sizes": ["Standard_D2s_v3", "Standard_D4s_v3", "Standard_F4s_v2"],
                    "app_service_tiers": ["S1", "S2", "P1V2", "P2V2"],
                    "sql_tiers": ["S1", "S2", "P1", "P2"],
                    "storage_tiers": ["Standard_ZRS", "Standard_GRS", "Premium_LRS"],
                    "features": {
                        "auto_shutdown": False,
                        "dev_test_pricing": False,
                        "high_availability": True,
                        "reserved_instances": True,
                        "geo_redundancy": True
                    }
                }
            },
            "resource_optimizations": {
                "Microsoft.Compute/virtualMachines": {
                    "development": {
                        "recommended_sizes": ["Standard_B1s", "Standard_B2s"],
                        "auto_shutdown": "19:00-08:00",
                        "disk_type": "Standard_LRS"
                    },
                    "production": {
                        "recommended_sizes": ["Standard_D2s_v3", "Standard_D4s_v3"],
                        "availability_set": True,
                        "disk_type": "Premium_LRS",
                        "backup": True
                    }
                },
                "Microsoft.Web/serverfarms": {
                    "development": {
                        "recommended_tiers": ["F1", "D1", "B1"],
                        "auto_scale": False,
                        "instance_count": 1
                    },
                    "production": {
                        "recommended_tiers": ["S1", "S2", "P1V2"],
                        "auto_scale": True,
                        "min_instances": 2,
                        "max_instances": 10
                    }
                },
                "Microsoft.Sql/servers/databases": {
                    "development": {
                        "recommended_tiers": ["Basic", "S0"],
                        "backup_retention": 7,
                        "geo_replication": False
                    },
                    "production": {
                        "recommended_tiers": ["S2", "P1", "P2"],
                        "backup_retention": 35,
                        "geo_replication": True,
                        "threat_detection": True
                    }
                },
                "Microsoft.Storage/storageAccounts": {
                    "development": {
                        "recommended_tiers": ["Standard_LRS"],
                        "access_tier": "Hot",
                        "lifecycle_management": False
                    },
                    "production": {
                        "recommended_tiers": ["Standard_ZRS", "Standard_GRS"],
                        "access_tier": "Hot",
                        "lifecycle_management": True,
                        "soft_delete": True
                    }
                }
            }
        }
    
    def optimize_architecture(self, architecture_analysis: Dict[str, Any], policy_compliance: Dict[str, Any], environment: str = 'development') -> Dict[str, Any]:
        """
        Main method to optimize architecture for cost based on Microsoft's framework
        """
        try:
            print(f"🔧 Cost Optimization Agent: Starting optimization for {environment} environment")
            
            # Generate cache key
            cache_key = self._get_cache_key(architecture_analysis, environment)
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                print("📋 Cost Optimization Agent: Using cached optimization results")
                return cached_result
            
            # Extract components and resources
            components = architecture_analysis.get('components', [])
            resources = architecture_analysis.get('resources', [])
            all_resources = components + resources
            
            # If no resources detected, provide generic optimization recommendations
            if not all_resources:
                print("⚠️ Cost Optimizer: No resources detected, providing generic Azure cost optimization")
                return self._generate_generic_optimization_recommendations(environment)
            
            # Apply cost optimization strategies
            optimized_resources = []
            optimization_recommendations = []
            cost_savings = []
            
            for resource in all_resources:
                optimized_resource, recommendations, savings = self._optimize_resource(resource, environment, policy_compliance)
                optimized_resources.append(optimized_resource)
                optimization_recommendations.extend(recommendations)
                if savings:
                    cost_savings.append(savings)
            
            # Generate AI-powered optimization insights
            ai_insights = self._generate_ai_optimization_insights(architecture_analysis, environment, optimization_recommendations)
            
            # Create optimization summary
            optimization_summary = self._create_optimization_summary(
                environment, 
                optimization_recommendations, 
                cost_savings, 
                ai_insights
            )
            
            result = {
                'optimized_architecture': {
                    'components': optimized_resources,
                    'metadata': architecture_analysis.get('metadata', {}),
                    'relationships': architecture_analysis.get('relationships', [])
                },
                'optimization_recommendations': optimization_recommendations,
                'cost_savings': cost_savings,
                'ai_insights': ai_insights,
                'optimization_summary': optimization_summary,
                'environment': environment,
                'framework_applied': 'Microsoft Well-Architected Framework - Cost Optimization',
                'bicep_generation_hints': self._generate_bicep_hints(optimized_resources, environment)
            }
            
            # Cache the result
            self._add_to_cache(cache_key, result)
            
            print(f"✅ Cost Optimization Agent: Optimization completed with {len(optimization_recommendations)} recommendations")
            return result
            
        except Exception as e:
            print(f"❌ Cost Optimization Agent: Error during optimization: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._generate_generic_optimization_recommendations(environment)
    
    def _generate_generic_optimization_recommendations(self, environment: str) -> Dict[str, Any]:
        """Generate generic Azure cost optimization recommendations when no specific resources are detected"""
        
        # Generic recommendations based on environment
        if environment == 'development':
            recommendations = [
                "Enable auto-shutdown for development VMs (18:00 UTC daily)",
                "Use B-Series burstable VMs for variable development workloads",
                "Implement Azure Dev/Test pricing for eligible resources",
                "Use Standard_LRS storage for non-critical development data",
                "Configure F1/D1 tier App Service plans for development applications",
                "Use Basic tier SQL databases for development environments",
                "Implement resource tagging for cost tracking and management"
            ]
            estimated_savings = "€200-500"
            annual_savings = "€2,400-6,000"
        elif environment == 'staging':
            recommendations = [
                "Use Standard_B2s VMs for staging workloads",
                "Implement auto-scaling for App Service plans",
                "Use Standard_S1 SQL database tier for staging",
                "Configure automated backup retention policies",
                "Implement Azure Hybrid Benefit where applicable",
                "Use Standard_GRS storage for important staging data",
                "Set up cost alerts and budgets for staging resources"
            ]
            estimated_savings = "€300-700"
            annual_savings = "€3,600-8,400"
        else:  # production
            recommendations = [
                "Implement Reserved Instances for production VMs (1-3 year terms)",
                "Use Premium SSD with appropriate IOPS for production workloads",
                "Configure auto-scaling for production App Service plans",
                "Implement SQL Database elastic pools for multiple databases",
                "Use Azure Hybrid Benefit for Windows Server and SQL licenses",
                "Set up monitoring and alerting for cost optimization",
                "Regular right-sizing analysis based on actual usage metrics"
            ]
            estimated_savings = "€500-1,500"
            annual_savings = "€6,000-18,000"
        
        # Generic cost savings structure
        cost_savings = [{
            "generic_optimization": {
                "type": "azure_best_practices",
                "estimated_monthly_savings": estimated_savings
            }
        }]
        
        # AI insights for generic recommendations
        ai_insights = {
            "strategic_recommendations": [
                f"Implement Microsoft Well-Architected Framework cost optimization principles for {environment} environment",
                "Set up Azure Cost Management and Billing for continuous monitoring",
                "Establish cost governance policies and regular review processes",
                "Consider Azure Advisor recommendations for ongoing optimization"
            ],
            "implementation_priority": "High" if environment == "production" else "Medium",
            "monitoring_setup": [
                "Configure cost alerts at 80% and 100% of budget",
                "Set up monthly cost review meetings",
                "Implement resource tagging strategy for cost allocation"
            ]
        }
        
        # Create optimization summary
        optimization_summary = {
            'environment': environment,
            'optimization_framework': 'Microsoft Well-Architected Framework',
            'total_recommendations': len(recommendations),
            'estimated_monthly_savings': estimated_savings,
            'estimated_annual_savings': annual_savings,
            'key_optimization_areas': [
                'Resource right-sizing',
                'Environment-specific configurations',
                'Auto-scaling and automation',
                'Reserved capacity planning'
            ],
            'implementation_priority': 'High' if environment == 'production' else 'Medium',
            'ai_insights_available': True,
            'framework_compliance': 'High',
            'next_steps': [
                'Review and approve optimization recommendations',
                'Implement cost optimization best practices',
                'Set up cost monitoring and alerts',
                'Schedule regular cost optimization reviews'
            ]
        }
        
        return {
            'optimized_architecture': {
                'components': [],
                'metadata': {'cost_optimized': True, 'generic_recommendations': True},
                'relationships': []
            },
            'optimization_recommendations': recommendations,
            'cost_savings': cost_savings,
            'ai_insights': ai_insights,
            'optimization_summary': optimization_summary,
            'environment': environment,
            'framework_applied': 'Microsoft Well-Architected Framework - Cost Optimization',
            'bicep_generation_hints': {
                'environment_configurations': {
                    'environment': environment,
                    'cost_optimized': True,
                    'generic_optimization': True
                }
            }
        }
    
    def _normalize_service_type(self, service_type: str) -> str:
        """Normalize service type names for consistent matching"""
        # Handle both old and new naming conventions
        service_mapping = {
            'app service': 'app_service',
            'sql database': 'sql_database', 
            'storage account': 'storage_account',
            'virtual machine': 'virtual_machine',
            'kubernetes service': 'kubernetes_service',
            'container registry': 'container_registry',
            'key vault': 'key_vault',
            'cosmos db': 'cosmos_db',
            'application gateway': 'application_gateway',
            'load balancer': 'load_balancer',
            'virtual network': 'virtual_network',
            'network security group': 'network_security_group',
            'active directory': 'active_directory',
            'security center': 'security_center',
            'data factory': 'data_factory',
            'synapse analytics': 'synapse_analytics',
            'machine learning': 'machine_learning',
            'cognitive services': 'cognitive_services',
            'iot hub': 'iot_hub',
            'stream analytics': 'stream_analytics',
            'power bi': 'power_bi',
            'redis cache': 'redis_cache',
            'service bus': 'service_bus',
            'event hubs': 'event_hubs',
            'api management': 'api_management',
            'logic apps': 'logic_apps',
            'monitor': 'azure_monitor',
            'log analytics': 'log_analytics',
            'azure devops': 'azure_devops',
            'backup': 'azure_backup',
            'site recovery': 'site_recovery',
            'vpn gateway': 'vpn_gateway',
            'firewall': 'azure_firewall',
            'cdn': 'azure_cdn',
            'functions': 'azure_functions'
        }
        
        # Normalize to lowercase and handle spaces/underscores
        normalized = service_type.lower().strip()
        
        # Apply mapping if exists
        if normalized in service_mapping:
            return service_mapping[normalized]
        
        # Convert spaces to underscores if not in mapping
        return normalized.replace(' ', '_')

    def _optimize_resource(self, resource: Dict[str, Any], environment: str, policy_compliance: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], Dict[str, Any]]:
        """Optimize a single resource based on environment and framework"""
        resource_type = self._normalize_service_type(resource.get('type', ''))
        resource_name = resource.get('name', 'Unknown')
        
        # Create optimized copy of resource
        optimized_resource = resource.copy()
        optimized_resource['type'] = resource_type  # Update with normalized type
        recommendations = []
        savings = {}
        
        # Apply environment-specific optimizations based on service type
        if resource_type in ['app_service', 'web_app']:
            if environment == 'development':
                recommendations.append(f"App Service {resource_name}: Use F1/D1 tier for development (€0-15/month)")
                savings[resource_name] = {'type': 'app_service_dev_tier', 'estimated_monthly_savings': '€30-80'}
            elif environment == 'staging':
                recommendations.append(f"App Service {resource_name}: Use S1 tier for staging (€50/month)")
                savings[resource_name] = {'type': 'app_service_staging_tier', 'estimated_monthly_savings': '€20-50'}
            else:  # production
                recommendations.append(f"App Service {resource_name}: Consider P1V2 with auto-scaling (€70-200/month)")
                savings[resource_name] = {'type': 'app_service_auto_scaling', 'estimated_monthly_savings': '€50-150'}
        
        elif resource_type in ['virtual_machine', 'vm']:
            if environment == 'development':
                recommendations.append(f"VM {resource_name}: Use B-Series burstable VMs with auto-shutdown")
                savings[resource_name] = {'type': 'vm_dev_optimization', 'estimated_monthly_savings': '€100-300'}
            elif environment == 'staging':
                recommendations.append(f"VM {resource_name}: Use Standard_D2s_v3 with scheduled shutdown")
                savings[resource_name] = {'type': 'vm_staging_optimization', 'estimated_monthly_savings': '€50-150'}
            else:  # production
                recommendations.append(f"VM {resource_name}: Consider Reserved Instances for 1-3 year terms")
                savings[resource_name] = {'type': 'vm_reserved_instances', 'estimated_monthly_savings': '€200-600'}
        
        elif resource_type in ['sql_database', 'azure_sql']:
            if environment == 'development':
                recommendations.append(f"SQL Database {resource_name}: Use Basic tier (€4-15/month)")
                savings[resource_name] = {'type': 'sql_basic_tier', 'estimated_monthly_savings': '€50-150'}
            elif environment == 'staging':
                recommendations.append(f"SQL Database {resource_name}: Use S1 Standard tier (€20/month)")
                savings[resource_name] = {'type': 'sql_standard_tier', 'estimated_monthly_savings': '€30-100'}
            else:  # production
                recommendations.append(f"SQL Database {resource_name}: Consider elastic pools for multiple DBs")
                savings[resource_name] = {'type': 'sql_elastic_pools', 'estimated_monthly_savings': '€100-400'}
        
        elif resource_type in ['storage_account', 'blob_storage']:
            recommendations.append(f"Storage {resource_name}: Use appropriate access tiers (Hot/Cool/Archive)")
            savings[resource_name] = {'type': 'storage_tiering', 'estimated_monthly_savings': '€20-100'}
        
        elif resource_type in ['kubernetes_service', 'aks']:
            if environment == 'development':
                recommendations.append(f"AKS {resource_name}: Use smaller node sizes and auto-scaling")
                savings[resource_name] = {'type': 'aks_dev_optimization', 'estimated_monthly_savings': '€150-500'}
            else:
                recommendations.append(f"AKS {resource_name}: Use spot instances for non-critical workloads")
                savings[resource_name] = {'type': 'aks_spot_instances', 'estimated_monthly_savings': '€200-800'}
        
        else:
            # Generic optimization for other services
            recommendations.append(f"{resource_type.replace('_', ' ').title()} {resource_name}: Review sizing and enable monitoring")
            savings[resource_name] = {'type': 'generic_optimization', 'estimated_monthly_savings': '€10-50'}
        
        return optimized_resource, recommendations, savings
    
    def _generate_ai_optimization_insights(self, architecture_analysis: Dict[str, Any], environment: str, recommendations: List[str]) -> Dict[str, Any]:
        """Generate AI-powered cost optimization insights using OpenAI"""
        try:
            # Prepare context for AI analysis
            context = {
                'environment': environment,
                'resource_count': len(architecture_analysis.get('components', [])),
                'current_recommendations': recommendations[:5],  # Limit to first 5 for AI context
                'architecture_type': architecture_analysis.get('metadata', {}).get('architecture_type', 'Web Application')
            }
            
            prompt = f"""
You are a Microsoft Azure cost optimization expert. Analyze this architecture and provide advanced cost optimization insights.

Architecture Context:
- Environment: {environment}
- Resource Count: {context['resource_count']}
- Architecture Type: {context['architecture_type']}
- Current Optimizations: {', '.join(recommendations[:3])}

Provide JSON response with:
1. "strategic_recommendations": 3-5 high-impact cost optimization strategies
2. "architectural_patterns": Cost-effective architectural patterns to consider
3. "monitoring_strategy": Cost monitoring and alerting recommendations
4. "long_term_savings": Long-term cost optimization roadmap
5. "risk_assessment": Potential risks of proposed optimizations

Focus on Microsoft Well-Architected Framework cost optimization principles.
Ensure recommendations are specific to {environment} environment.
"""

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert Azure cost optimization consultant following Microsoft Well-Architected Framework principles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                timeout=300  # 5 minutes timeout for OpenAI API
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                insights = json.loads(ai_response)
                return insights
            except json.JSONDecodeError:
                # Fallback to structured text parsing
                return {
                    "strategic_recommendations": self._extract_recommendations_from_text(ai_response),
                    "raw_response": ai_response
                }
                
        except Exception as e:
            print(f"⚠️ Cost Optimization Agent: AI insights generation failed: {str(e)}")
            return {
                "strategic_recommendations": [
                    "Review resource utilization patterns",
                    "Implement auto-scaling policies",
                    "Consider reserved capacity for production workloads"
                ],
                "error": str(e)
            }
    
    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """Extract recommendations from AI text response"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('•') or line.startswith('-') or line.startswith('*') or 
                line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                clean_line = line.lstrip('•-*123456789. ').strip()
                if clean_line and len(clean_line) > 10:
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _create_optimization_summary(self, environment: str, recommendations: List[str], cost_savings: List[Dict], ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive optimization summary"""
        
        # Calculate total estimated savings
        total_savings_low = 0
        total_savings_high = 0
        
        for saving in cost_savings:
            for resource_name, saving_info in saving.items():
                if 'estimated_monthly_savings' in saving_info:
                    savings_str = saving_info['estimated_monthly_savings']
                    # Extract numbers from strings like "€50-150"
                    import re
                    numbers = re.findall(r'\d+', savings_str)
                    if len(numbers) >= 2:
                        total_savings_low += int(numbers[0])
                        total_savings_high += int(numbers[1])
                    elif len(numbers) == 1:
                        total_savings_low += int(numbers[0])
                        total_savings_high += int(numbers[0])
        
        return {
            'environment': environment,
            'optimization_framework': 'Microsoft Well-Architected Framework',
            'total_recommendations': len(recommendations),
            'estimated_monthly_savings': f"€{total_savings_low}-{total_savings_high}",
            'estimated_annual_savings': f"€{total_savings_low*12}-{total_savings_high*12}",
            'key_optimization_areas': [
                'Resource right-sizing',
                'Environment-specific configurations',
                'Auto-scaling and automation',
                'Reserved capacity planning'
            ],
            'implementation_priority': 'High' if environment == 'production' else 'Medium',
            'ai_insights_available': bool(ai_insights.get('strategic_recommendations')),
            'framework_compliance': 'High',
            'next_steps': [
                'Review and approve optimization recommendations',
                'Implement Bicep templates with optimizations',
                'Set up cost monitoring and alerts',
                'Schedule regular cost optimization reviews'
            ]
        }
    
    def _generate_bicep_hints(self, optimized_resources: List[Dict[str, Any]], environment: str) -> Dict[str, Any]:
        """Generate hints for Bicep generator to implement optimizations"""
        bicep_hints = {
            'environment_configurations': {
                'environment': environment,
                'cost_optimized': True,
                'auto_shutdown_enabled': environment == 'development',
                'dev_test_pricing': environment == 'development'
            },
            'resource_configurations': {},
            'template_parameters': {},
            'conditional_deployments': []
        }
        
        for resource in optimized_resources:
            resource_name = resource.get('name', 'unknown')
            resource_type = resource.get('type', '')
            
            # Add resource-specific configurations
            bicep_hints['resource_configurations'][resource_name] = {
                'type': resource_type,
                'cost_optimized': True,
                'environment_specific': True
            }
            
            # Add auto-shutdown for development VMs
            if resource_type == 'Microsoft.Compute/virtualMachines' and environment == 'development':
                if resource.get('properties', {}).get('autoShutdown'):
                    bicep_hints['conditional_deployments'].append({
                        'condition': "parameters('environment') == 'development'",
                        'resource': resource_name,
                        'feature': 'autoShutdown'
                    })
            
            # Add scaling configurations
            if 'serverfarms' in resource_type:
                sku = resource.get('sku', {}).get('name', '')
                bicep_hints['template_parameters'][f'{resource_name}_sku'] = {
                    'default': sku,
                    'environment_specific': True
                }
        
        return bicep_hints
    
    def _get_cache_key(self, architecture_analysis: Dict[str, Any], environment: str) -> str:
        """Generate cache key for optimization results"""
        content_str = json.dumps(architecture_analysis, sort_keys=True) + environment
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Dict[str, Any]:
        """Get cached optimization result"""
        return self._optimization_cache.get(cache_key)
    
    def _add_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """Add optimization result to cache"""
        if len(self._optimization_cache) >= self._max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._optimization_cache))
            del self._optimization_cache[oldest_key]
        
        self._optimization_cache[cache_key] = result
    
    def generate_cost_optimization_report(self, optimization_result: Dict[str, Any]) -> str:
        """Generate a detailed cost optimization report"""
        
        if 'error' in optimization_result:
            return f"# Cost Optimization Report\n\n**Error**: {optimization_result['error']}\n"
        
        report = []
        report.append("# Azure Cost Optimization Report")
        report.append("")
        
        # Summary
        summary = optimization_result.get('optimization_summary', {})
        report.append(f"## Executive Summary")
        report.append(f"**Environment**: {summary.get('environment', 'Unknown')}")
        report.append(f"**Framework**: {summary.get('optimization_framework', 'Microsoft Well-Architected Framework')}")
        report.append(f"**Total Recommendations**: {summary.get('total_recommendations', 0)}")
        report.append(f"**Estimated Monthly Savings**: {summary.get('estimated_monthly_savings', '€0')}")
        report.append(f"**Estimated Annual Savings**: {summary.get('estimated_annual_savings', '€0')}")
        report.append(f"**Implementation Priority**: {summary.get('implementation_priority', 'Medium')}")
        report.append("")
        
        # Optimization Recommendations
        recommendations = optimization_result.get('optimization_recommendations', [])
        if recommendations:
            report.append("## Cost Optimization Recommendations")
            report.append("")
            for i, recommendation in enumerate(recommendations[:10], 1):  # Top 10
                report.append(f"{i}. {recommendation}")
            report.append("")
        
        # AI Insights
        ai_insights = optimization_result.get('ai_insights', {})
        if ai_insights.get('strategic_recommendations'):
            report.append("## AI-Powered Strategic Insights")
            report.append("")
            for insight in ai_insights['strategic_recommendations'][:5]:
                report.append(f"• {insight}")
            report.append("")
        
        # Cost Savings Breakdown
        cost_savings = optimization_result.get('cost_savings', [])
        if cost_savings:
            report.append("## Estimated Cost Savings Breakdown")
            report.append("")
            for saving in cost_savings:
                for resource_name, saving_info in saving.items():
                    savings_type = saving_info.get('type', 'optimization')
                    estimated_savings = saving_info.get('estimated_monthly_savings', '€0')
                    report.append(f"• **{resource_name}** ({savings_type}): {estimated_savings}/month")
            report.append("")
        
        # Key Optimization Areas
        key_areas = summary.get('key_optimization_areas', [])
        if key_areas:
            report.append("## Key Optimization Areas")
            report.append("")
            for area in key_areas:
                report.append(f"• {area}")
            report.append("")
        
        # Next Steps
        next_steps = summary.get('next_steps', [])
        if next_steps:
            report.append("## Implementation Next Steps")
            report.append("")
            for i, step in enumerate(next_steps, 1):
                report.append(f"{i}. {step}")
            report.append("")
        
        # Framework Compliance
        report.append("## Microsoft Well-Architected Framework Compliance")
        report.append("")
        report.append("This optimization follows the five key principles of cost optimization:")
        report.append("• **Plan and estimate costs** - Detailed cost analysis and estimation")
        report.append("• **Provision with optimization** - Right-sized resources for environment")
        report.append("• **Use monitoring and analytics** - Recommendations for cost monitoring")
        report.append("• **Maximize efficiency** - Auto-scaling and automation recommendations")
        report.append("• **Optimize over time** - Continuous optimization roadmap")
        report.append("")
        
        # Disclaimers
        report.append("## Important Notes")
        report.append("")
        report.append("• Cost savings estimates are approximate and may vary based on actual usage")
        report.append("• Implement changes in non-production environments first")
        report.append("• Monitor performance impact after implementing optimizations")
        report.append("• Review and update optimizations regularly as usage patterns change")
        
        return "\n".join(report)
