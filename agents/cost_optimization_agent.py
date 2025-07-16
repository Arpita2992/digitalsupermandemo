"""
AI Agent 3: Cost Optimization Agent
Analyzes Azure architecture and applies Microsoft's cost optimization framework
Optimizes resources based on environment (development/production) before Bicep generation
"""

import json
import os
from typing import Dict, List, Any, Tuple
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
            return {
                'error': f'Cost optimization failed: {str(e)}',
                'optimized_architecture': architecture_analysis,
                'optimization_recommendations': [],
                'cost_savings': []
            }
    
    def _optimize_resource(self, resource: Dict[str, Any], environment: str, policy_compliance: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], Dict[str, Any]]:
        """Optimize a single resource based on environment and framework"""
        resource_type = resource.get('type', '')
        resource_name = resource.get('name', 'Unknown')
        
        # Create optimized copy of resource
        optimized_resource = resource.copy()
        recommendations = []
        savings = {}
        
        # Apply resource-specific optimizations
        if resource_type in self.cost_optimization_framework['resource_optimizations']:
            optimization_rules = self.cost_optimization_framework['resource_optimizations'][resource_type]
            env_rules = optimization_rules.get(environment, {})
            
            # Apply environment-specific optimizations
            for rule_key, rule_value in env_rules.items():
                if rule_key == 'recommended_sizes' and resource_type == 'Microsoft.Compute/virtualMachines':
                    current_size = resource.get('properties', {}).get('hardwareProfile', {}).get('vmSize', 'Standard_D2s_v3')
                    if current_size not in rule_value:
                        recommended_size = rule_value[0]  # Use first recommended size
                        optimized_resource.setdefault('properties', {}).setdefault('hardwareProfile', {})['vmSize'] = recommended_size
                        recommendations.append(f"VM {resource_name}: Changed size from {current_size} to {recommended_size} for {environment} environment")
                        savings[resource_name] = {'type': 'vm_rightsizing', 'estimated_monthly_savings': '€50-150'}
                
                elif rule_key == 'recommended_tiers' and 'serverfarms' in resource_type:
                    current_tier = resource.get('sku', {}).get('name', 'S1')
                    if current_tier not in rule_value:
                        recommended_tier = rule_value[0]
                        optimized_resource.setdefault('sku', {})['name'] = recommended_tier
                        recommendations.append(f"App Service Plan {resource_name}: Changed from {current_tier} to {recommended_tier} for {environment} environment")
                        savings[resource_name] = {'type': 'app_service_optimization', 'estimated_monthly_savings': '€30-100'}
                
                elif rule_key == 'recommended_tiers' and 'databases' in resource_type:
                    current_tier = resource.get('sku', {}).get('name', 'S1')
                    if current_tier not in rule_value:
                        recommended_tier = rule_value[0]
                        optimized_resource.setdefault('sku', {})['name'] = recommended_tier
                        recommendations.append(f"SQL Database {resource_name}: Changed from {current_tier} to {recommended_tier} for {environment} environment")
                        savings[resource_name] = {'type': 'database_optimization', 'estimated_monthly_savings': '€25-75'}
                
                elif rule_key == 'auto_shutdown' and environment == 'development':
                    # Add auto-shutdown configuration
                    optimized_resource.setdefault('properties', {})['autoShutdown'] = {
                        'enabled': True,
                        'time': rule_value,
                        'timeZone': 'UTC'
                    }
                    recommendations.append(f"VM {resource_name}: Enabled auto-shutdown ({rule_value}) for development environment")
                    savings[resource_name] = {'type': 'auto_shutdown', 'estimated_monthly_savings': '€100-300'}
        
        # Apply general environment-specific optimizations
        env_strategies = self.cost_optimization_framework['environment_strategies'].get(environment, {})
        
        # Add environment-specific features
        features = env_strategies.get('features', {})
        for feature_key, feature_value in features.items():
            if feature_key == 'dev_test_pricing' and feature_value and environment == 'development':
                optimized_resource.setdefault('properties', {})['devTestPricing'] = True
                recommendations.append(f"Resource {resource_name}: Applied dev/test pricing (up to 55% savings)")
                savings[resource_name + '_devtest'] = {'type': 'dev_test_pricing', 'estimated_monthly_savings': '€50-200'}
            
            elif feature_key == 'reserved_instances' and feature_value and environment == 'production':
                if resource_type == 'Microsoft.Compute/virtualMachines':
                    recommendations.append(f"VM {resource_name}: Consider Reserved Instance (up to 72% savings for 3-year term)")
                    savings[resource_name + '_reserved'] = {'type': 'reserved_instance_recommendation', 'estimated_monthly_savings': '€200-500'}
        
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
                max_tokens=1500
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
