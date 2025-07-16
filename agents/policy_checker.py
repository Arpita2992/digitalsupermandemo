"""
AI Agent 2: Policy Checker
Checks the analyzed architecture against Microsoft Azure policies for compliance
"""

import json
import os
from typing import Dict, List, Any, Optional
import hashlib

try:
    from openai import OpenAI
except ImportError:
    print("⚠️ OpenAI package not installed. Install with: pip install openai")
    OpenAI = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv package not installed. Install with: pip install python-dotenv")

class PolicyChecker:
    def __init__(self):
        # Check if Azure AI Foundry configuration is available
        self.azure_endpoint = os.getenv('AZURE_AI_AGENT2_ENDPOINT')
        self.azure_key = os.getenv('AZURE_AI_AGENT2_KEY')
        self.azure_deployment = os.getenv('AZURE_AI_AGENT2_DEPLOYMENT', 'gpt-4')
        
        if OpenAI and self.azure_endpoint and self.azure_key:
            # Use Azure AI Foundry endpoint
            from openai import AzureOpenAI
            self.openai_client = AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.azure_key,
                api_version="2024-02-01"
            )
            self.model_name = self.azure_deployment
            print(f"✅ Policy Checker: Using Azure AI Foundry endpoint")
        elif OpenAI:
            # Fallback to OpenAI
            self.openai_client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.model_name = "gpt-4"
            print(f"⚠️ Policy Checker: Using OpenAI fallback (configure Azure AI Foundry for production)")
        else:
            print("❌ Policy Checker: OpenAI package not available")
            self.openai_client = None
            self.model_name = None
        
        # Load policy templates
        self.policy_templates = self._load_policy_templates()
        
        # Load custom policies from policies folder
        self.custom_policies = self._load_custom_policies()
        
        # Simple cache for policy checks
        self._cache = {}
        self._max_cache_size = 50

    def check_compliance(self, architecture_analysis: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        Check architecture compliance against Azure policies
        """
        
        # Check cache first
        cache_key = self._get_cache_key(architecture_analysis, environment)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            print("🔍 Policy Checker: Using cached result")
            return cached_result
        
        try:
            # Get environment-specific policies
            applicable_policies = self._get_environment_policies(environment)
            
            # Create compliance check prompt
            compliance_prompt = self._create_compliance_prompt(
                architecture_analysis, 
                applicable_policies, 
                environment
            )
            
            # Call OpenAI API for compliance analysis
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an Azure compliance expert specializing in policy compliance. Analyze the architecture against Microsoft Azure policies and provide detailed compliance recommendations."
                    },
                    {
                        "role": "user",
                        "content": compliance_prompt
                    }
                ],
                temperature=0.1,
                timeout=300  # 5 minutes timeout for OpenAI API
            )
            
            # Parse compliance results
            compliance_result = self._parse_compliance_response(
                response.choices[0].message.content,
                environment
            )
            
            # Add custom policy validation
            custom_policy_results = self._validate_custom_policies(architecture_analysis)
            
            # Merge custom policy results with main compliance results
            if custom_policy_results['policy_checks']:
                compliance_result['custom_policy_validation'] = custom_policy_results
                
                # Update overall compliance status
                if not custom_policy_results['compliant']:
                    compliance_result['compliant'] = False
                    
                # Add custom policy violations to main violations list
                if 'violations' not in compliance_result:
                    compliance_result['violations'] = []
                compliance_result['violations'].extend(custom_policy_results['violations'])
                
                # Add custom policy warnings
                if 'warnings' not in compliance_result:
                    compliance_result['warnings'] = []
                compliance_result['warnings'].extend(custom_policy_results['warnings'])
                
                # Update compliance score based on custom policies
                if 'overall_compliance' in compliance_result:
                    total_policies = len(custom_policy_results['policy_checks'])
                    compliant_policies = sum(1 for check in custom_policy_results['policy_checks'] if check['compliant'])
                    if total_policies > 0:
                        custom_score = (compliant_policies / total_policies) * 100
                        current_score = float(compliance_result['overall_compliance'].get('compliance_score', '0').replace('%', ''))
                        # Average the scores (you might want to adjust this weighting)
                        combined_score = (current_score + custom_score) / 2
                        compliance_result['overall_compliance']['compliance_score'] = f"{combined_score:.1f}%"
            
            # Save to cache
            self._save_to_cache(cache_key, compliance_result)
            
            return compliance_result
            
        except Exception as e:
            return {
                'error': f'Policy compliance check failed: {str(e)}',
                'compliant': False,
                'violations': [],
                'recommendations': []
            }
    
    def _load_policy_templates(self) -> Dict[str, Any]:
        """Load Azure policy templates with environment-specific compliance levels"""
        return {
            'development': {
                'compliance_level': 'relaxed',
                'required_policies': 5,  # Minimum policies to enforce
                'security': {
                    'level': 'basic',
                    'policies': [
                        'Enable encryption at rest for storage accounts',
                        'Use managed identities where possible',
                        'Implement basic network security groups (NSGs)',
                        'Enable Azure Security Center free tier'
                    ]
                },
                'networking': {
                    'level': 'basic',
                    'policies': [
                        'Implement basic subnet segmentation',
                        'Configure NSGs for traffic filtering'
                    ]
                },
                'governance': {
                    'level': 'basic',
                    'policies': [
                        'Apply basic resource tagging (Environment, CreatedBy)',
                        'Use resource locks for critical resources only'
                    ]
                }
            },
            'staging': {
                'compliance_level': 'moderate',
                'required_policies': 8,  # More policies required
                'security': {
                    'level': 'moderate',
                    'policies': [
                        'Enable encryption at rest and in transit',
                        'Use Azure Key Vault for secrets management',
                        'Use managed identities exclusively',
                        'Enable Azure Security Center Standard tier',
                        'Implement basic audit logging'
                    ]
                },
                'networking': {
                    'level': 'moderate',
                    'policies': [
                        'Use private endpoints for PaaS services',
                        'Implement proper subnet segmentation',
                        'Configure Azure Firewall or advanced NSGs',
                        'Consider DDoS protection'
                    ]
                },
                'governance': {
                    'level': 'moderate',
                    'policies': [
                        'Apply comprehensive resource tagging',
                        'Use Azure Policy for governance enforcement',
                        'Implement resource locks for all important resources',
                        'Implement proper RBAC'
                    ]
                },
                'availability': {
                    'level': 'moderate',
                    'policies': [
                        'Consider availability zones',
                        'Implement backup strategies'
                    ]
                }
            },
            'production': {
                'compliance_level': 'strict',
                'required_policies': 15,  # Maximum compliance required
                'security': {
                    'level': 'strict',
                    'policies': [
                        'Enable encryption at rest and in transit (MANDATORY)',
                        'Use Azure Key Vault for ALL secrets management (MANDATORY)',
                        'Implement multi-factor authentication (MANDATORY)',
                        'Enable Azure Security Center Standard tier (MANDATORY)',
                        'Use managed identities exclusively (MANDATORY)',
                        'Implement Azure Sentinel for SIEM (MANDATORY)',
                        'Enable comprehensive audit logging (MANDATORY)',
                        'Implement security monitoring and alerting (MANDATORY)'
                    ]
                },
                'networking': {
                    'level': 'strict',
                    'policies': [
                        'Use private endpoints for ALL PaaS services (MANDATORY)',
                        'Implement strict network segmentation with NSGs (MANDATORY)',
                        'Use Azure Firewall for centralized traffic filtering (MANDATORY)',
                        'Implement DDoS protection (MANDATORY)',
                        'Use Application Gateway with WAF (MANDATORY)'
                    ]
                },
                'governance': {
                    'level': 'strict',
                    'policies': [
                        'Apply comprehensive resource tagging strategy (MANDATORY)',
                        'Use Azure Policy for strict governance enforcement (MANDATORY)',
                        'Implement resource locks for ALL critical resources (MANDATORY)',
                        'Use Azure Blueprints for consistent deployments (MANDATORY)',
                        'Implement proper RBAC with least privilege (MANDATORY)'
                    ]
                },
                'availability': {
                    'level': 'strict',
                    'policies': [
                        'Implement multi-region deployment (MANDATORY)',
                        'Use availability zones where supported (MANDATORY)',
                        'Implement backup and disaster recovery (MANDATORY)',
                        'Use Azure Site Recovery for business continuity (MANDATORY)'
                    ]
                }
            }
        }
    
    def _get_environment_policies(self, environment: str) -> Dict[str, Any]:
        """Get policies specific to the environment, including custom policies"""
        base_policies = self.policy_templates.get(environment.lower(), self.policy_templates['development'])
        
        # Add custom policies to the base policies
        if self.custom_policies:
            # Create a copy to avoid modifying the original
            enhanced_policies = base_policies.copy()
            enhanced_policies['custom_policies'] = self.custom_policies
            
            # Add custom policy descriptions to environment-specific sections
            for category, policy_data in self.custom_policies.items():
                if category not in enhanced_policies:
                    enhanced_policies[category] = {
                        'level': 'custom',
                        'policies': []
                    }
                
                # Add policy names and descriptions
                custom_policy_descriptions = []
                for policy in policy_data['policies']:
                    severity_label = {
                        'critical': '[CRITICAL]',
                        'high': '[HIGH]',
                        'medium': '[MEDIUM]',
                        'low': '[LOW]',
                        'info': '[INFO]'
                    }.get(policy['severity'], '[MEDIUM]')
                    
                    custom_policy_descriptions.append(
                        f"{severity_label} {policy['name']}: {policy['description']}"
                    )
                
                enhanced_policies[category]['policies'].extend(custom_policy_descriptions)
            
            return enhanced_policies
        
        return base_policies
    
    def _create_compliance_prompt(self, analysis: Dict[str, Any], policies: Dict[str, Any], environment: str) -> str:
        """Create compliance check prompt"""
        
        compliance_level = policies.get('compliance_level', 'basic')
        required_policies = policies.get('required_policies', 5)
        
        # Extract custom policies summary
        custom_policies_summary = ""
        if 'custom_policies' in policies:
            custom_policies_summary = "\n\nCUSTOM AZURE POLICIES TO VALIDATE:\n"
            for category, policy_data in policies['custom_policies'].items():
                custom_policies_summary += f"\n{policy_data['category']} Policies:\n"
                for policy in policy_data['policies']:
                    custom_policies_summary += f"  - {policy['name']} (Effect: {policy['effect']}, Severity: {policy['severity']})\n"
                    custom_policies_summary += f"    Description: {policy['description']}\n"
        
        prompt = f"""
        Please analyze the following Azure architecture for compliance with Microsoft Azure policies.
        
        ENVIRONMENT: {environment.upper()}
        COMPLIANCE LEVEL: {compliance_level.upper()}
        REQUIRED POLICIES TO PASS: {required_policies}
        
        IMPORTANT: Apply {compliance_level} compliance standards for {environment} environment:
        - DEVELOPMENT: Relaxed standards, focus on basic security and functionality
        - STAGING: Moderate standards, balance between security and development needs  
        - PRODUCTION: STRICT standards, maximum security and compliance required
        
        Architecture Analysis:
        {json.dumps(analysis, indent=2)}
        
        Environment-Specific Policy Requirements:
        {json.dumps({k: v for k, v in policies.items() if k != 'custom_policies'}, indent=2)}
        {custom_policies_summary}
        
        CRITICAL: When analyzing compliance, pay special attention to the custom Azure policies listed above. 
        These are organization-specific policies that must be evaluated alongside standard Azure policies.
        For each custom policy, check if the architecture components comply with the policy rule and effect.
        
        Please provide a detailed compliance analysis in the following JSON structure:
        {{
            "overall_compliance": {{
                "compliant": boolean,
                "compliance_score": "percentage (0-100)",
                "compliance_level": "{compliance_level}",
                "environment": "{environment}",
                "critical_violations": number,
                "warnings": number,
                "required_policies_met": number,
                "total_required_policies": {required_policies}
            }},
                "compliance_score": "percentage",
                "critical_violations": number,
                "warnings": number
            }},
            "category_compliance": {{
                "security": {{
                    "compliant": boolean,
                    "violations": [],
                    "recommendations": []
                }},
                "networking": {{
                    "compliant": boolean,
                    "violations": [],
                    "recommendations": []
                }},
                "governance": {{
                    "compliant": boolean,
                    "violations": [],
                    "recommendations": []
                }},
                "availability": {{
                    "compliant": boolean,
                    "violations": [],
                    "recommendations": []
                }}
            }},
            "violations": [
                {{
                    "severity": "critical|warning|info",
                    "category": "security|networking|governance|availability",
                    "component": "affected_component_name",
                    "description": "violation_description",
                    "recommendation": "how_to_fix",
                    "policy_reference": "azure_policy_reference"
                }}
            ],
            "recommendations": [
                {{
                    "priority": "high|medium|low",
                    "category": "security|networking|governance|availability",
                    "component": "affected_component_name",
                    "description": "recommendation_description",
                    "implementation": "how_to_implement",
                    "benefits": "expected_benefits"
                }}
            ]
        }}
        
        Focus on:
        1. Security best practices and compliance
        2. Network security and segmentation
        3. Governance and resource management
        4. High availability and disaster recovery
        5. Specific {environment} environment requirements
        6. Environment-appropriate SKU and service tier recommendations
        """
        
        return prompt
    
    def _validate_custom_policies(self, architecture_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate architecture against custom policies"""
        validation_results = {
            'compliant': True,
            'violations': [],
            'warnings': [],
            'policy_checks': []
        }
        
        if not self.custom_policies:
            return validation_results
            
        resources = architecture_analysis.get('resources', [])
        
        for category, policy_data in self.custom_policies.items():
            for policy in policy_data['policies']:
                policy_name = policy['name']
                policy_rule = policy['policy_rule']
                effect = policy['effect']
                severity = policy['severity']
                
                # Basic policy validation logic
                violation_found = False
                affected_resources = []
                
                # Check each resource against the policy rule
                for resource in resources:
                    resource_type = resource.get('type', '')
                    
                    # Simple policy rule evaluation (this could be enhanced)
                    if self._evaluate_policy_rule(resource, policy_rule):
                        violation_found = True
                        affected_resources.append(resource.get('name', 'Unknown'))
                
                policy_check = {
                    'policy_name': policy_name,
                    'category': category,
                    'effect': effect,
                    'severity': severity,
                    'compliant': not violation_found,
                    'affected_resources': affected_resources
                }
                
                validation_results['policy_checks'].append(policy_check)
                
                if violation_found:
                    validation_results['compliant'] = False
                    
                    violation = {
                        'policy': policy_name,
                        'category': category,
                        'severity': severity,
                        'effect': effect,
                        'description': policy.get('description', ''),
                        'affected_resources': affected_resources,
                        'recommendation': f"Review and modify resources to comply with {policy_name}"
                    }
                    
                    if severity in ['critical', 'high']:
                        validation_results['violations'].append(violation)
                    else:
                        validation_results['warnings'].append(violation)
        
        return validation_results
    
    def _evaluate_policy_rule(self, resource: Dict[str, Any], policy_rule: Dict[str, Any]) -> bool:
        """Evaluate a single policy rule against a resource"""
        # This is a simplified policy rule evaluation
        # In a production environment, this would need more sophisticated rule evaluation
        
        if not policy_rule or 'if' not in policy_rule:
            return False
            
        condition = policy_rule['if']
        
        # Handle allOf conditions
        if 'allOf' in condition:
            for sub_condition in condition['allOf']:
                if not self._evaluate_condition(resource, sub_condition):
                    return False
            return True
            
        # Handle anyOf conditions  
        if 'anyOf' in condition:
            for sub_condition in condition['anyOf']:
                if self._evaluate_condition(resource, sub_condition):
                    return True
            return False
            
        # Handle single condition
        return self._evaluate_condition(resource, condition)
    
    def _evaluate_condition(self, resource: Dict[str, Any], condition: Dict[str, Any]) -> bool:
        """Evaluate a single condition against a resource"""
        if 'field' in condition:
            field_path = condition['field']
            resource_value = self._get_resource_field_value(resource, field_path)
            
            # Handle different condition types
            if 'equals' in condition:
                return resource_value == condition['equals']
            elif 'in' in condition:
                return resource_value in condition['in']
            elif 'notIn' in condition:
                return resource_value not in condition['notIn']
            elif 'like' in condition:
                import re
                pattern = condition['like'].replace('*', '.*')
                return bool(re.match(pattern, str(resource_value), re.IGNORECASE))
            elif 'exists' in condition:
                return (resource_value is not None) == condition['exists']
                
        return False
    
    def _get_resource_field_value(self, resource: Dict[str, Any], field_path: str):
        """Get the value of a field from a resource using dot notation"""
        # Handle Azure resource field paths like "Microsoft.Compute/virtualMachines/sku.name"
        if '/' in field_path:
            # For Azure resource types, extract the relevant part
            parts = field_path.split('/')
            if len(parts) >= 2:
                resource_type = '/'.join(parts[:2])
                if resource.get('type') == resource_type:
                    if len(parts) > 2:
                        field_name = parts[2]
                        return resource.get(field_name)
                    else:
                        return resource.get('type')
        
        # Handle simple field names
        field_parts = field_path.split('.')
        value = resource
        for part in field_parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value
    
    def _parse_compliance_response(self, response: str, environment: str) -> Dict[str, Any]:
        """Parse the compliance response"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                compliance_data = json.loads(json_match.group())
                compliance_data['environment'] = environment
                compliance_data['check_timestamp'] = self._get_timestamp()
                return compliance_data
            else:
                return self._fallback_compliance_parse(response, environment)
        except json.JSONDecodeError:
            return self._fallback_compliance_parse(response, environment)
    
    def _fallback_compliance_parse(self, response: str, environment: str) -> Dict[str, Any]:
        """Fallback parsing for compliance response"""
        return {
            'overall_compliance': {
                'compliant': False,
                'compliance_score': 'Unknown',
                'critical_violations': 0,
                'warnings': 0
            },
            'category_compliance': {},
            'violations': [],
            'recommendations': [],
            'environment': environment,
            'check_timestamp': self._get_timestamp(),
            'raw_response': response,
            'parsing_note': 'Used fallback parsing due to JSON parsing error'
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def generate_compliance_report(self, compliance_result: Dict[str, Any]) -> str:
        """Generate a human-readable compliance report"""
        
        # Generate custom policies table
        custom_policies_table = self._generate_custom_policies_table(compliance_result)
        
        report = f"""
# Azure Architecture Compliance Report

## Environment: {compliance_result.get('environment', 'Unknown').upper()}
## Generated: {compliance_result.get('check_timestamp', 'Unknown')}

{custom_policies_table}

## Overall Compliance Summary
- **Compliant**: {compliance_result.get('overall_compliance', {}).get('compliant', 'Unknown')}
- **Compliance Score**: {compliance_result.get('overall_compliance', {}).get('compliance_score', 'Unknown')}
- **Critical Violations**: {compliance_result.get('overall_compliance', {}).get('critical_violations', 0)}
- **Warnings**: {compliance_result.get('overall_compliance', {}).get('warnings', 0)}

## Violations Found
"""
        
        violations = compliance_result.get('violations', [])
        for i, violation in enumerate(violations, 1):
            report += f"""
### {i}. {violation.get('severity', 'Unknown').upper()} - {violation.get('category', 'Unknown').title()}
- **Component**: {violation.get('component', 'Unknown')}
- **Description**: {violation.get('description', 'No description')}
- **Recommendation**: {violation.get('recommendation', 'No recommendation')}
- **Policy Reference**: {violation.get('policy_reference', 'Not specified')}
"""
        
        report += "\n## Recommendations\n"
        recommendations = compliance_result.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            report += f"""
### {i}. {rec.get('priority', 'Unknown').upper()} Priority - {rec.get('category', 'Unknown').title()}
- **Component**: {rec.get('component', 'Unknown')}
- **Description**: {rec.get('description', 'No description')}
- **Implementation**: {rec.get('implementation', 'No implementation details')}
- **Benefits**: {rec.get('benefits', 'No benefits listed')}
"""
        
        return report
    
    def _generate_custom_policies_table(self, compliance_result: Dict[str, Any]) -> str:
        """Generate a table of custom policies that were evaluated"""
        
        # Check if we have custom policy validation results
        custom_validation = compliance_result.get('custom_policy_validation', {})
        policy_checks = custom_validation.get('policy_checks', [])
        
        if not policy_checks:
            # If no custom policy results, show loaded policies
            return self._generate_loaded_policies_table()
        
        # Generate table with policy check results
        table = """
## Custom Azure Policies Evaluated

The following organization-specific Azure policies were evaluated against the architecture:

| Policy Name | Category | Effect | Severity | Status | Affected Resources |
|-------------|----------|--------|----------|--------|--------------------|"""
        
        for check in policy_checks:
            policy_name = check.get('policy_name', 'Unknown')
            category = check.get('category', 'Unknown').title()
            effect = check.get('effect', 'Unknown')
            severity = check.get('severity', 'Unknown').upper()
            status = '✅ COMPLIANT' if check.get('compliant', False) else '❌ NON-COMPLIANT'
            affected_resources = ', '.join(check.get('affected_resources', [])) or 'None'
            
            # Truncate long resource lists
            if len(affected_resources) > 50:
                affected_resources = affected_resources[:47] + '...'
            
            table += f"\n| {policy_name} | {category} | {effect} | {severity} | {status} | {affected_resources} |"
        
        # Add summary statistics
        total_policies = len(policy_checks)
        compliant_policies = sum(1 for check in policy_checks if check.get('compliant', False))
        non_compliant_policies = total_policies - compliant_policies
        
        table += f"""

### Custom Policy Compliance Summary
- **Total Custom Policies Evaluated**: {total_policies}
- **Compliant**: {compliant_policies} (✅)
- **Non-Compliant**: {non_compliant_policies} (❌)
- **Compliance Rate**: {(compliant_policies/total_policies*100) if total_policies > 0 else 0:.1f}%
"""
        
        return table
    
    def _generate_loaded_policies_table(self) -> str:
        """Generate a table of loaded policies when no validation results are available"""
        
        if not self.custom_policies:
            return """
## Custom Azure Policies

No custom Azure policies were found in the policies folder.
"""
        
        table = """
## Custom Azure Policies Available

The following organization-specific Azure policies are available for evaluation:

| Policy Name | Category | Effect | Severity | Description |
|-------------|----------|--------|----------|-------------|"""
        
        policy_count = 0
        for category, policy_data in self.custom_policies.items():
            for policy in policy_data['policies']:
                policy_name = policy.get('name', 'Unknown')
                category_name = policy_data.get('category', 'Unknown')
                effect = policy.get('effect', 'Unknown')
                severity = policy.get('severity', 'Unknown').upper()
                description = policy.get('description', 'No description')
                
                # Truncate long descriptions
                if len(description) > 80:
                    description = description[:77] + '...'
                
                table += f"\n| {policy_name} | {category_name} | {effect} | {severity} | {description} |"
                policy_count += 1
        
        # Add summary
        table += f"""

### Policy Summary
- **Total Policies Loaded**: {policy_count}
- **Categories**: {len(self.custom_policies)}
- **Policy Distribution by Severity**:"""
        
        # Count policies by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for category, policy_data in self.custom_policies.items():
            for policy in policy_data['policies']:
                severity = policy.get('severity', 'medium')
                if severity in severity_counts:
                    severity_counts[severity] += 1
        
        for severity, count in severity_counts.items():
            if count > 0:
                table += f"\n  - **{severity.upper()}**: {count} policies"
        
        return table
    
    def _get_cache_key(self, architecture_analysis, environment):
        """Generate cache key from analysis and environment"""
        key_data = f"{str(architecture_analysis)}{environment}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key):
        """Get cached result if available"""
        return self._cache.get(cache_key)
    
    def _save_to_cache(self, cache_key, result):
        """Save result to cache"""
        if len(self._cache) >= self._max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[cache_key] = result

    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of loaded policies"""
        summary = {
            'total_policies': 0,
            'categories': {},
            'severity_distribution': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'info': 0
            },
            'effect_distribution': {
                'Deny': 0,
                'Audit': 0,
                'DeployIfNotExists': 0,
                'Modify': 0,
                'AuditIfNotExists': 0,
                'Disabled': 0
            }
        }
        
        for category, policy_data in self.custom_policies.items():
            policy_count = len(policy_data['policies'])
            summary['categories'][category] = {
                'category_name': policy_data['category'],
                'policy_count': policy_count,
                'policies': []
            }
            
            for policy in policy_data['policies']:
                summary['total_policies'] += 1
                summary['severity_distribution'][policy['severity']] += 1
                
                # Handle effect distribution safely
                effect = policy['effect']
                if effect in summary['effect_distribution']:
                    summary['effect_distribution'][effect] += 1
                else:
                    summary['effect_distribution']['Audit'] += 1  # Default fallback
                
                summary['categories'][category]['policies'].append({
                    'name': policy['name'],
                    'effect': policy['effect'],
                    'severity': policy['severity'],
                    'description': policy['description'][:100] + '...' if len(policy['description']) > 100 else policy['description']
                })
        
        return summary
    
    def reload_policies(self):
        """Reload policies from the policies folder"""
        print("🔄 Policy Checker: Reloading policies...")
        self.custom_policies = self._load_custom_policies()
        # Clear cache to force re-evaluation
        self._cache.clear()
        print("✅ Policy Checker: Policies reloaded")

    def fix_policy_violations(self, architecture_analysis: Dict[str, Any], policy_compliance: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        Auto-fix policy violations in the architecture analysis
        """
        print(f"🔧 Policy Checker: Auto-fixing violations for {environment}")
        
        try:
            violations = policy_compliance.get('violations', [])
            if not violations:
                print("✅ No violations to fix")
                return architecture_analysis
            
            fixed_analysis = architecture_analysis.copy()
            fixed_violations = []
            
            for violation in violations:
                fix_result = self._apply_policy_fix(fixed_analysis, violation, environment)
                if fix_result['fixed']:
                    fixed_violations.append({
                        'violation': violation,
                        'fix_applied': fix_result['description'],
                        'component': fix_result.get('component', 'unknown')
                    })
            
            # Update metadata
            fixed_analysis['metadata'] = fixed_analysis.get('metadata', {})
            fixed_analysis['metadata']['policy_fixes_applied'] = fixed_violations
            fixed_analysis['metadata']['auto_fix_timestamp'] = self._get_timestamp()
            
            print(f"🔧 Applied {len(fixed_violations)} policy fixes")
            return fixed_analysis
            
        except Exception as e:
            print(f"❌ Error during policy fixing: {str(e)}")
            return architecture_analysis
    
    def _apply_policy_fix(self, analysis: Dict[str, Any], violation: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Apply specific policy fix based on violation type"""
        
        violation_type = violation.get('type', '').lower()
        component_name = violation.get('component', '')
        
        # Storage Account Fixes
        if 'storage' in violation_type and 'encryption' in violation.get('description', '').lower():
            return self._fix_storage_encryption(analysis, component_name)
        
        # Network Security Group Fixes
        elif 'network' in violation_type or 'nsg' in violation_type:
            return self._fix_network_security(analysis, component_name, environment)
        
        # Key Vault Fixes
        elif 'key vault' in violation.get('description', '').lower() or 'secret' in violation_type:
            return self._fix_key_vault_security(analysis, component_name)
        
        # App Service Fixes
        elif 'app service' in violation_type or 'web app' in violation_type:
            return self._fix_app_service_security(analysis, component_name)
        
        # RBAC and Identity Fixes
        elif 'rbac' in violation_type or 'identity' in violation_type:
            return self._fix_identity_security(analysis, component_name)
        
        # General Security Fixes
        elif 'security' in violation_type:
            return self._fix_general_security(analysis, component_name, environment)
        
        else:
            return {'fixed': False, 'description': f'No automated fix available for: {violation_type}'}
    
    def _fix_storage_encryption(self, analysis: Dict[str, Any], component_name: str) -> Dict[str, Any]:
        """Fix storage account encryption issues"""
        components = analysis.get('components', [])
        
        for component in components:
            if component.get('name') == component_name and 'storage' in component.get('type', '').lower():
                # Ensure encryption is enabled
                if 'properties' not in component:
                    component['properties'] = {}
                
                component['properties'].update({
                    'supportsHttpsTrafficOnly': True,
                    'encryption': {
                        'services': {
                            'file': {'enabled': True},
                            'blob': {'enabled': True}
                        },
                        'keySource': 'Microsoft.Storage'
                    },
                    'minimumTlsVersion': 'TLS1_2'
                })
                
                return {
                    'fixed': True,
                    'description': 'Enabled encryption at rest and HTTPS-only traffic',
                    'component': component_name
                }
        
        return {'fixed': False, 'description': 'Storage component not found'}
    
    def _fix_network_security(self, analysis: Dict[str, Any], component_name: str, environment: str) -> Dict[str, Any]:
        """Fix network security group issues"""
        components = analysis.get('components', [])
        
        # Add NSG if missing
        nsg_exists = any('nsg' in comp.get('type', '').lower() or 'network security' in comp.get('type', '').lower() 
                        for comp in components)
        
        if not nsg_exists:
            nsg_component = {
                'name': f'nsg-{environment}',
                'type': 'Microsoft.Network/networkSecurityGroups',
                'properties': {
                    'securityRules': [
                        {
                            'name': 'AllowHTTPS',
                            'properties': {
                                'protocol': 'Tcp',
                                'sourcePortRange': '*',
                                'destinationPortRange': '443',
                                'sourceAddressPrefix': '*',
                                'destinationAddressPrefix': '*',
                                'access': 'Allow',
                                'priority': 1000,
                                'direction': 'Inbound'
                            }
                        },
                        {
                            'name': 'DenyAllInbound',
                            'properties': {
                                'protocol': '*',
                                'sourcePortRange': '*',
                                'destinationPortRange': '*',
                                'sourceAddressPrefix': '*',
                                'destinationAddressPrefix': '*',
                                'access': 'Deny',
                                'priority': 4096,
                                'direction': 'Inbound'
                            }
                        }
                    ]
                },
                'auto_generated': True
            }
            components.append(nsg_component)
            
            return {
                'fixed': True,
                'description': 'Added Network Security Group with secure rules',
                'component': f'nsg-{environment}'
            }
        
        return {'fixed': False, 'description': 'NSG already exists or cannot be auto-fixed'}
    
    def _fix_key_vault_security(self, analysis: Dict[str, Any], component_name: str) -> Dict[str, Any]:
        """Fix Key Vault security issues"""
        components = analysis.get('components', [])
        
        # Add Key Vault if missing
        kv_exists = any('key vault' in comp.get('type', '').lower() or 'keyvault' in comp.get('type', '').lower() 
                       for comp in components)
        
        if not kv_exists:
            kv_component = {
                'name': 'kv-digitalsuperman',
                'type': 'Microsoft.KeyVault/vaults',
                'properties': {
                    'enabledForDeployment': True,
                    'enabledForTemplateDeployment': True,
                    'enabledForDiskEncryption': True,
                    'enableSoftDelete': True,
                    'softDeleteRetentionInDays': 90,
                    'enablePurgeProtection': True,
                    'sku': {
                        'family': 'A',
                        'name': 'standard'
                    },
                    'accessPolicies': [],
                    'networkAcls': {
                        'defaultAction': 'Deny',
                        'bypass': 'AzureServices'
                    }
                },
                'auto_generated': True
            }
            components.append(kv_component)
            
            return {
                'fixed': True,
                'description': 'Added Key Vault with security best practices',
                'component': 'kv-digitalsuperman'
            }
        
        return {'fixed': False, 'description': 'Key Vault already exists'}
    
    def _fix_app_service_security(self, analysis: Dict[str, Any], component_name: str) -> Dict[str, Any]:
        """Fix App Service security issues"""
        components = analysis.get('components', [])
        
        for component in components:
            if 'app service' in component.get('type', '').lower() or 'web' in component.get('type', '').lower():
                if 'properties' not in component:
                    component['properties'] = {}
                
                component['properties'].update({
                    'httpsOnly': True,
                    'clientAffinityEnabled': False,
                    'siteConfig': {
                        'minTlsVersion': '1.2',
                        'ftpsState': 'Disabled',
                        'alwaysOn': True,
                        'http20Enabled': True
                    }
                })
                
                return {
                    'fixed': True,
                    'description': 'Applied App Service security configurations',
                    'component': component_name
                }
        
        return {'fixed': False, 'description': 'App Service component not found'}
    
    def _fix_identity_security(self, analysis: Dict[str, Any], component_name: str) -> Dict[str, Any]:
        """Fix identity and RBAC issues"""
        components = analysis.get('components', [])
        
        # Add managed identity to applicable components
        fixed_components = []
        for component in components:
            comp_type = component.get('type', '').lower()
            if any(service in comp_type for service in ['app service', 'function', 'vm', 'web']):
                if 'identity' not in component:
                    component['identity'] = {
                        'type': 'SystemAssigned'
                    }
                    fixed_components.append(component.get('name', 'unknown'))
        
        if fixed_components:
            return {
                'fixed': True,
                'description': f'Added managed identity to: {", ".join(fixed_components)}',
                'component': ', '.join(fixed_components)
            }
        
        return {'fixed': False, 'description': 'No components require managed identity fixes'}
    
    def _fix_general_security(self, analysis: Dict[str, Any], component_name: str, environment: str) -> Dict[str, Any]:
        """Apply general security fixes"""
        components = analysis.get('components', [])
        
        security_fixes = []
        
        for component in components:
            if 'tags' not in component:
                component['tags'] = {}
            
            # Ensure proper tagging
            component['tags'].update({
                'Environment': environment,
                'CreatedBy': 'DigitalSuperman',
                'Compliance': 'AutoFixed',
                'SecurityLevel': 'Enhanced'
            })
            
            security_fixes.append(f"Enhanced tagging for {component.get('name', 'unknown')}")
        
        if security_fixes:
            return {
                'fixed': True,
                'description': f'Applied general security fixes: {"; ".join(security_fixes)}',
                'component': 'multiple'
            }
        
        return {'fixed': False, 'description': 'No general security fixes needed'}
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def optimize_architecture_costs(self, architecture_analysis: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """
        (DISABLED) Stub for cost optimization. Returns empty result.
        """
        return {
            'applied_optimizations': [],
            'cost_savings_estimate': 0,
            'optimized_components': [],
            'recommendations': []
        }
    
    def _load_custom_policies(self) -> Dict[str, Any]:
        """Load custom Azure policies from the policies folder"""
        policies = {}
        policies_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'policies')
        
        if not os.path.exists(policies_dir):
            print(f"⚠️ Policy Checker: Policies directory not found at {policies_dir}")
            return policies
            
        policy_files = [f for f in os.listdir(policies_dir) if f.endswith('.json')]
        print(f"📋 Policy Checker: Found {len(policy_files)} policy files")
        
        for policy_file in policy_files:
            try:
                policy_path = os.path.join(policies_dir, policy_file)
                with open(policy_path, 'r', encoding='utf-8') as f:
                    policy_content = json.load(f)
                
                # Handle both single policy and array of policies
                policies_to_process = []
                if isinstance(policy_content, list):
                    policies_to_process = policy_content
                elif isinstance(policy_content, dict):
                    policies_to_process = [policy_content]
                else:
                    print(f"⚠️ Policy Checker: Invalid policy format in {policy_file}")
                    continue
                
                # Process each policy
                for idx, single_policy in enumerate(policies_to_process):
                    if not isinstance(single_policy, dict):
                        continue
                        
                    # Extract key information from policy
                    policy_name = single_policy.get('displayName', f"{policy_file.replace('.json', '')}_{idx}")
                    policy_category = single_policy.get('metadata', {}).get('category', 'General')
                    policy_description = single_policy.get('description', '')
                    
                    # Categorize policies by their category and severity
                    category_key = policy_category.lower().replace(' ', '_')
                    if category_key not in policies:
                        policies[category_key] = {
                            'category': policy_category,
                            'policies': []
                        }
                    
                    # Determine policy severity based on effect
                    policy_rule = single_policy.get('policyRule', {})
                    effect = policy_rule.get('then', {}).get('effect', 'Audit')
                    
                    # Handle parameter references in effect
                    if isinstance(effect, str) and effect.startswith('[parameters('):
                        # Extract default value from parameters
                        parameters = single_policy.get('parameters', {})
                        effect_param = effect.replace('[parameters(', '').replace(')]', '').strip("'\"")
                        if effect_param in parameters:
                            effect = parameters[effect_param].get('defaultValue', 'Audit')
                        else:
                            effect = 'Audit'  # Default fallback
                    
                    # Map effect to severity
                    severity_mapping = {
                        'Deny': 'critical',
                        'DeployIfNotExists': 'high',
                        'Modify': 'medium',
                        'Audit': 'low',
                        'AuditIfNotExists': 'low',
                        'Disabled': 'info'
                    }
                    
                    severity = severity_mapping.get(effect, 'medium')
                    
                    policies[category_key]['policies'].append({
                        'name': policy_name,
                        'file': policy_file,
                        'description': policy_description,
                        'effect': effect,
                        'severity': severity,
                        'policy_rule': policy_rule,
                        'parameters': single_policy.get('parameters', {}),
                        'full_policy': single_policy
                    })
                    
            except Exception as e:
                print(f"⚠️ Policy Checker: Error loading policy {policy_file}: {str(e)}")
                continue
        
        print(f"✅ Policy Checker: Loaded {sum(len(cat['policies']) for cat in policies.values())} policies across {len(policies)} categories")
        return policies
