"""
AI Agent 3: Bicep Generator
Generates Azure Bicep templates and YAML pipelines based on architecture analysis and compliance checks
"""

import json
import os
from typing import Dict, List, Any, Optional
import openai
from dotenv import load_dotenv
import hashlib
from utils.trace_decorator import trace_agent

load_dotenv()

class BicepGenerator:
    def __init__(self):
        # Check if Azure AI Foundry configuration is available
        self.azure_endpoint = os.getenv('AZURE_AI_AGENT4_ENDPOINT')
        self.azure_key = os.getenv('AZURE_AI_AGENT4_KEY')
        self.azure_deployment = os.getenv('AZURE_AI_AGENT4_DEPLOYMENT', 'gpt-4')
        
        if self.azure_endpoint and self.azure_key:
            # Use Azure AI Foundry endpoint
            self.openai_client = openai.AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.azure_key,
                api_version="2024-02-01"
            )
            self.model_name = self.azure_deployment
            print(f"✅ Bicep Generator: Using Azure AI Foundry endpoint")
        else:
            # Fallback to OpenAI
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.model_name = "gpt-4"
            print(f"⚠️ Bicep Generator: Using OpenAI fallback (configure Azure AI Foundry for production)")
        
        # Load Bicep templates
        self.bicep_templates = self._load_bicep_templates()
        
        # Template cache for faster generation
        self._template_cache = {}
        self._max_cache_size = 30
        
        # Trace ID for performance tracking
        self.current_trace_id = None
    
    @trace_agent("bicep_generator")
    def generate_bicep_templates(self, architecture_analysis: Dict[str, Any], policy_compliance: Dict[str, Any], cost_optimization: Dict[str, Any] = None, environment: str = 'dev', trace_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate Bicep templates with cost optimization considerations
        """
        # Set trace context
        if trace_id:
            self.current_trace_id = trace_id
        
        # Check cache first
        cache_key = self._get_cache_key(architecture_analysis, policy_compliance, cost_optimization, environment)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            print("🏗️ Bicep Generator: Using cached templates")
            return cached_result
        
        try:
            # Create generation prompt with cost optimization
            generation_prompt = self._create_generation_prompt(
                architecture_analysis,
                policy_compliance,
                cost_optimization,
                environment
            )
            
            # Call OpenAI API for Bicep generation
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Azure DevOps engineer and Bicep template specialist. Generate production-ready Bicep templates and Azure DevOps YAML pipelines."
                    },
                    {
                        "role": "user",
                        "content": generation_prompt
                    }
                ],
                temperature=0.1,
                timeout=300  # 5 minutes timeout for OpenAI API
            )
            
            # Parse generation results
            generation_result = self._parse_generation_response(
                response.choices[0].message.content,
                architecture_analysis,
                policy_compliance,
                cost_optimization,
                environment
            )
            
            # Save to cache
            self._save_to_cache(cache_key, generation_result)
            
            return generation_result
            
        except Exception as e:
            return {
                'error': f'Bicep generation failed: {str(e)}',
                'bicep_templates': {},
                'yaml_pipelines': {},
                'documentation': {}
            }
    
    def _load_bicep_templates(self) -> Dict[str, str]:
        """Load Bicep template snippets"""
        return {
            'resource_group': """
@description('Name of the resource group')
param resourceGroupName string = 'rg-${uniqueString(subscription().id)}'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment (dev, staging, prod)')
param environment string = 'dev'

@description('Common tags for all resources')
param tags object = {
  Environment: environment
  CreatedBy: 'DigitalSuperman'
  Project: 'Infrastructure'
}
""",
            'storage_account': """
@description('Storage account name')
param storageAccountName string = 'st${uniqueString(resourceGroup().id)}'

@description('Storage account type')
param storageAccountType string = 'Standard_LRS'

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  sku: {
    name: storageAccountType
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    encryption: {
      services: {
        file: {
          enabled: true
        }
        blob: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
  }
}
""",
            'app_service': """
@description('App Service plan name')
param appServicePlanName string = 'asp-${uniqueString(resourceGroup().id)}'

@description('App Service name')
param appServiceName string = 'app-${uniqueString(resourceGroup().id)}'

@description('App Service plan SKU')
param appServicePlanSku string = 'B1'

resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: appServicePlanSku
  }
  kind: 'app'
}

resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: appServiceName
  location: location
  tags: tags
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
    }
  }
}
"""
        }
    
    def generate_deployment_guide(self, templates: Dict[str, Any]) -> str:
        """Generate deployment guide"""
        guide = """
# Azure Infrastructure Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the generated Azure infrastructure.

## Prerequisites
- Azure CLI 2.0 or later
- Azure subscription with Contributor permissions
- PowerShell 5.1 or later (for Windows users)

## Deployment Steps

### 1. Prepare Environment
```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Install Bicep CLI
az bicep install
```

### 2. Validate Templates
```bash
# Validate main template
az bicep build --file main.bicep

# Validate deployment (dry run)
az deployment group validate \\
    --resource-group your-rg-name \\
    --template-file main.bicep \\
    --parameters @parameters/dev.parameters.json
```

### 3. Deploy Infrastructure
```bash
# Create resource group
az group create --name your-rg-name --location "East US"

# Deploy template
az deployment group create \\
    --resource-group your-rg-name \\
    --template-file main.bicep \\
    --parameters @parameters/dev.parameters.json
```

### 4. Verify Deployment
```bash
# Check deployment status
az deployment group show \\
    --resource-group your-rg-name \\
    --name main

# List created resources
az resource list --resource-group your-rg-name --output table
```

## Troubleshooting

### Common Issues
1. **Permission Denied**: Ensure you have Contributor role on the subscription
2. **Resource Already Exists**: Use unique names or update existing resources
3. **Quota Exceeded**: Check your Azure quotas and limits

### Validation Commands
```bash
# Check resource health
az resource list --resource-group your-rg-name --query "[].{Name:name,Type:type,Status:properties.provisioningState}" --output table

# View deployment logs
az deployment group show --resource-group your-rg-name --name main --query "properties.error"
```

## Clean Up
```bash
# Delete resource group and all resources
az group delete --name your-rg-name --yes --no-wait
```
"""
        return guide
    
    def _create_generation_prompt(self, analysis: Dict[str, Any], compliance: Dict[str, Any], cost_optimization: Dict[str, Any] = None, environment: str = 'dev') -> str:
        """Create concise Bicep generation prompt with cost optimization considerations"""
        
        # Get environment-specific requirements
        env_requirements = self._get_environment_requirements(environment)
        
        # Include cost optimization if available
        cost_context = ""
        if cost_optimization:
            bicep_hints = cost_optimization.get('bicep_generation_hints', {})
            optimization_summary = cost_optimization.get('optimization_summary', {})
            
            cost_context = f"""
Cost Optimization Applied:
- Framework: Microsoft Well-Architected Cost Optimization
- Estimated Savings: {optimization_summary.get('estimated_monthly_savings', 'N/A')}
- Bicep Hints: {json.dumps(bicep_hints, indent=1)}
- Key Optimizations: {optimization_summary.get('key_optimization_areas', [])}
"""
        
        prompt = f"""Generate Azure Bicep templates and DevOps pipeline for {environment.upper()} with cost optimization.

Environment: {environment}
Requirements: {json.dumps(env_requirements, indent=1)}

{cost_context}

Architecture: {json.dumps(analysis, indent=1)}

IMPORTANT: Implement cost optimizations from bicep_generation_hints in the templates.
Include conditional deployments, environment-specific SKUs, and auto-shutdown for dev environments.

Return JSON:
{{
    "bicep_templates": {{
        "main.bicep": "template content with cost optimizations",
        "parameters/": {{"{environment}.parameters.json": "optimized params"}}
    }},
    "yaml_pipelines": {{
        "azure-pipelines-{environment}.yml": "pipeline content"
    }},
    "scripts": {{
        "deploy-{environment}.ps1": "deploy script"
    }}
}}

Make it {env_requirements.get('pipeline_complexity', 'simple')} for {environment} with cost optimization focus."""
        
        return prompt
    
    def _parse_generation_response(self, response: str, analysis: Dict[str, Any], compliance: Dict[str, Any], cost_optimization: Dict[str, Any] = None, environment: str = 'dev') -> Dict[str, Any]:
        """Parse the generation response with cost optimization metadata"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                generation_data = json.loads(json_match.group())
                generation_data['metadata'] = {
                    'generated_timestamp': self._get_timestamp(),
                    'target_environment': environment,
                    'source_analysis': analysis,
                    'compliance_check': compliance,
                    'cost_optimization_applied': bool(cost_optimization),
                    'estimated_monthly_savings': cost_optimization.get('optimization_summary', {}).get('estimated_monthly_savings', 'N/A') if cost_optimization else 'N/A'
                }
                return generation_data
            else:
                return self._fallback_generation_parse(response, analysis, compliance, cost_optimization, environment)
        except json.JSONDecodeError:
            return self._fallback_generation_parse(response, analysis, compliance, cost_optimization, environment)
    
    def _fallback_generation_parse(self, response: str, analysis: Dict[str, Any], compliance: Dict[str, Any], cost_optimization: Dict[str, Any] = None, environment: str = 'dev') -> Dict[str, Any]:
        """Fallback parsing for generation response with cost optimization"""
        return {
            'bicep_templates': {
                'main.bicep': self._generate_fallback_bicep(analysis, environment, cost_optimization)
            },
            'yaml_pipelines': {
                f'azure-pipelines-{environment}.yml': self._generate_fallback_pipeline(environment)
            },
            'documentation': {
                'README.md': self._generate_fallback_readme(environment, cost_optimization)
            },
            'scripts': {
                f'deploy-{environment}.ps1': self._generate_fallback_deploy_script(environment)
            },
            'metadata': {
                'generated_timestamp': self._get_timestamp(),
                'target_environment': environment,
                'source_analysis': analysis,
                'compliance_check': compliance,
                'cost_optimization_applied': bool(cost_optimization),
                'estimated_monthly_savings': cost_optimization.get('optimization_summary', {}).get('estimated_monthly_savings', 'N/A') if cost_optimization else 'N/A',
                'parsing_note': 'Used fallback templates due to JSON parsing error'
            },
            'raw_response': response
        }
    
    def _generate_fallback_bicep(self, analysis: Dict[str, Any], environment: str, cost_optimization: Dict[str, Any] = None) -> str:
        """Generate fallback Bicep template with cost optimization"""
        components = analysis.get('components', [])
        
        # Get cost optimization hints if available
        bicep_hints = {}
        if cost_optimization:
            bicep_hints = cost_optimization.get('bicep_generation_hints', {})
        
        env_configs = bicep_hints.get('environment_configurations', {})
        cost_optimized = env_configs.get('cost_optimized', False)
        
        bicep_content = f"""
@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment ({environment})')
param environment string = '{environment}'

@description('Cost optimization enabled')
param costOptimized bool = {str(cost_optimized).lower()}

@description('Common tags for all resources')
param tags object = {{
  Environment: environment
  CreatedBy: 'DigitalSuperman'
  Project: 'Infrastructure'
  GeneratedFor: '{environment.title()}'
  CostOptimized: string(costOptimized)
}}
"""
        
        # Add environment-specific parameters from cost optimization
        template_params = bicep_hints.get('template_parameters', {})
        for param_name, param_config in template_params.items():
            if param_config.get('environment_specific'):
                bicep_content += f"\n@description('Cost optimized parameter for {param_name}')"
                bicep_content += f"\nparam {param_name} string = '{param_config.get('default', 'Standard')}'"
        
        # Add auto-shutdown for development VMs
        if environment == 'development' and env_configs.get('auto_shutdown_enabled'):
            bicep_content += """

@description('Auto-shutdown time for development VMs')
param autoShutdownTime string = '19:00'

@description('Auto-shutdown timezone')
param autoShutdownTimeZone string = 'UTC'
"""
        
        # Add basic resources based on detected components with cost optimization
        for component in components:
            component_type = component.get('type', '').lower()
            if 'storage' in component_type:
                bicep_content += "\n// Storage Account with cost optimization\n" + self.bicep_templates['storage_account']
            elif 'app' in component_type or 'web' in component_type:
                bicep_content += "\n// App Service with cost optimization\n" + self.bicep_templates['app_service']
        
        # Add conditional deployments from cost optimization
        conditional_deployments = bicep_hints.get('conditional_deployments', [])
        if conditional_deployments:
            bicep_content += "\n\n// Conditional deployments for cost optimization"
            for deployment in conditional_deployments:
                condition = deployment.get('condition', '')
                feature = deployment.get('feature', '')
                bicep_content += f"\n// {feature} - {condition}"
        
        return bicep_content
    
    def _generate_fallback_pipeline(self, environment: str) -> str:
        """Generate fallback Azure DevOps pipeline"""
        
        # Environment-specific pipeline configuration
        env_config = self._get_environment_requirements(environment)
        
        if environment.lower() == 'production':
            return f"""
name: Azure-Infrastructure-{environment.title()}-$(Date:yyyyMMdd)$(Rev:.r)

trigger:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  azureSubscription: 'Azure-{environment.title()}-Service-Connection'
  resourceGroupName: 'rg-digitalsuperman-{environment}'
  location: 'East US'
  templatePath: 'bicep/main.bicep'
  parametersPath: 'bicep/parameters/{environment}.parameters.json'

stages:
- stage: Validate
  displayName: 'Validate Bicep Templates'
  jobs:
  - job: ValidateJob
    displayName: 'Validate Templates'
    steps:
    - task: AzureCLI@2
      displayName: 'Validate Bicep Template'
      inputs:
        azureSubscription: $(azureSubscription)
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az bicep build --file $(templatePath)
          az deployment group validate \\
            --resource-group $(resourceGroupName) \\
            --template-file $(templatePath) \\
            --parameters @$(parametersPath)

- stage: SecurityScan
  displayName: 'Security Scanning'
  dependsOn: Validate
  jobs:
  - job: SecurityJob
    displayName: 'Security Scan'
    steps:
    - task: AzureCLI@2
      displayName: 'Security Scan Templates'
      inputs:
        azureSubscription: $(azureSubscription)
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          echo "Running security scans..."
          # Add your security scanning tools here

- stage: ProductionApproval
  displayName: 'Production Deployment Approval'
  dependsOn: SecurityScan
  jobs:
  - deployment: ApprovalJob
    displayName: 'Approve Production Deployment'
    environment: 'production-approval'
    strategy:
      runOnce:
        deploy:
          steps:
          - script: echo "Approved for production deployment"

- stage: Deploy
  displayName: 'Deploy to {environment.title()}'
  dependsOn: ProductionApproval
  jobs:
  - deployment: DeployJob
    displayName: 'Deploy Infrastructure'
    environment: '{environment}'
    strategy:
      runOnce:
        deploy:
          steps:
          - checkout: self
          - task: AzureCLI@2
            displayName: 'Deploy Infrastructure'
            inputs:
              azureSubscription: $(azureSubscription)
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az group create --name $(resourceGroupName) --location "$(location)"
                az deployment group create \\
                  --resource-group $(resourceGroupName) \\
                  --template-file $(templatePath) \\
                  --parameters @$(parametersPath) \\
                  --verbose

- stage: SmokeTest
  displayName: 'Smoke Tests'
  dependsOn: Deploy
  jobs:
  - job: SmokeTestJob
    displayName: 'Run Smoke Tests'
    steps:
    - task: AzureCLI@2
      displayName: 'Validate Deployment'
      inputs:
        azureSubscription: $(azureSubscription)
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          echo "Running smoke tests..."
          az resource list --resource-group $(resourceGroupName) --output table
"""
        else:
            # Development/Staging pipeline - simplified
            return f"""
name: Azure-Infrastructure-{environment.title()}-$(Date:yyyyMMdd)$(Rev:.r)

trigger:
  branches:
    include:
    - main
    - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  azureSubscription: 'Azure-{environment.title()}-Service-Connection'
  resourceGroupName: 'rg-digitalsuperman-{environment}'
  location: 'East US'
  templatePath: 'bicep/main.bicep'
  parametersPath: 'bicep/parameters/{environment}.parameters.json'

stages:
- stage: Validate
  displayName: 'Validate Bicep Templates'
  jobs:
  - job: ValidateJob
    displayName: 'Validate Templates'
    steps:
    - task: AzureCLI@2
      displayName: 'Validate Bicep Template'
      inputs:
        azureSubscription: $(azureSubscription)
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az bicep build --file $(templatePath)
          az deployment group validate \\
            --resource-group $(resourceGroupName) \\
            --template-file $(templatePath) \\
            --parameters @$(parametersPath)

- stage: Deploy
  displayName: 'Deploy to {environment.title()}'
  dependsOn: Validate
  jobs:
  - deployment: DeployJob
    displayName: 'Deploy Infrastructure'
    environment: '{environment}'
    strategy:
      runOnce:
        deploy:
          steps:
          - checkout: self
          - task: AzureCLI@2
            displayName: 'Deploy Infrastructure'
            inputs:
              azureSubscription: $(azureSubscription)
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                az group create --name $(resourceGroupName) --location "$(location)"
                az deployment group create \\
                  --resource-group $(resourceGroupName) \\
                  --template-file $(templatePath) \\
                  --parameters @$(parametersPath) \\
                  --verbose
"""
    
    def _generate_fallback_readme(self, environment: str, cost_optimization: Dict[str, Any] = None) -> str:
        """Generate fallback README with cost optimization information"""
        
        cost_info = ""
        if cost_optimization:
            optimization_summary = cost_optimization.get('optimization_summary', {})
            estimated_savings = optimization_summary.get('estimated_monthly_savings', 'N/A')
            key_areas = optimization_summary.get('key_optimization_areas', [])
            
            cost_info = f"""
## Cost Optimization

This infrastructure has been optimized for cost efficiency using Microsoft's Well-Architected Framework:

- **Estimated Monthly Savings**: {estimated_savings}
- **Framework Applied**: Microsoft Well-Architected Framework - Cost Optimization
- **Key Optimization Areas**: {', '.join(key_areas) if key_areas else 'Resource right-sizing, environment-specific configurations'}

### Cost Optimization Features

- Environment-specific resource SKUs
- Auto-shutdown for development resources (if applicable)
- Right-sized compute and storage resources
- Optimized networking configurations
"""
        
        return f"""
# Digital Superman - Azure Infrastructure ({environment.title()})

This repository contains the Azure infrastructure templates generated by Digital Superman for the **{environment.upper()}** environment.

## Overview

This infrastructure was automatically generated based on your Azure architecture diagram analysis and optimized for {environment} deployment with cost optimization applied.
{cost_info}
## Structure

- `bicep/main.bicep` - Main Bicep template for {environment} with cost optimizations
- `bicep/parameters/{environment}.parameters.json` - Environment-specific parameters
- `azure-pipelines-{environment}.yml` - Azure DevOps CI/CD pipeline for {environment}
- `deploy-{environment}.ps1` - PowerShell deployment script for {environment}

## Environment: {environment.upper()}

This configuration is specifically tailored for {environment} with appropriate:
- Resource SKUs and configurations (cost optimized)
- Security and compliance settings
- Pipeline complexity and approval gates
- Monitoring and backup requirements
- Cost optimization features

## Deployment

### Prerequisites

- Azure CLI installed and configured
- Azure subscription with appropriate permissions
- Azure DevOps project (for CI/CD)

### Manual Deployment

1. Login to Azure:
   ```bash
   az login
   ```

2. Create resource group:
   ```bash
   az group create --name rg-digitalsuperman --location "East US"
   ```

3. Deploy template:
   ```bash
   az deployment group create --resource-group rg-digitalsuperman --template-file main.bicep
   ```

### CI/CD Deployment

1. Set up Azure DevOps service connection
2. Import the pipeline from `azure-pipelines.yml`
3. Configure pipeline variables
4. Run the pipeline

## Security

This infrastructure follows Azure security best practices and compliance requirements.

## Support

For issues or questions, please refer to the compliance documentation.
"""
    
    def _generate_fallback_deploy_script(self, environment: str) -> str:
        """Generate fallback deployment script"""
        return f"""
param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-digitalsuperman-{environment}",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "{environment}",
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = "bicep/main.bicep",
    
    [Parameter(Mandatory=$false)]
    [string]$ParametersFile = "bicep/parameters/{environment}.parameters.json"
)

Write-Host "🚀 Digital Superman - Deploying Infrastructure for {environment.upper()}" -ForegroundColor Green
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "Location: $Location" -ForegroundColor Cyan

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {{
    Write-Error "❌ Azure CLI is not installed. Please install Azure CLI first."
    exit 1
}}

# Check if logged in to Azure
$account = az account show --query "id" -o tsv 2>$null
if (-not $account) {{
    Write-Host "⚠️ Not logged in to Azure. Please login first." -ForegroundColor Yellow
    az login
}}

# Validate template files exist
if (-not (Test-Path $TemplateFile)) {{
    Write-Error "❌ Template file not found: $TemplateFile"
    exit 1
}}

if (-not (Test-Path $ParametersFile)) {{
    Write-Error "❌ Parameters file not found: $ParametersFile"
    exit 1
}}

# Install Bicep CLI if not already installed
Write-Host "🔧 Installing/Updating Bicep CLI..." -ForegroundColor Yellow
az bicep install

# Create resource group if it doesn't exist
Write-Host "📦 Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Validate template
Write-Host "✅ Validating Bicep template..." -ForegroundColor Yellow
az deployment group validate `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters @$ParametersFile

if ($LASTEXITCODE -ne 0) {{
    Write-Error "❌ Template validation failed!"
    exit 1
}}

Write-Host "✅ Template validation successful!" -ForegroundColor Green

# Deploy template
Write-Host "🚀 Deploying infrastructure to {environment.upper()}..." -ForegroundColor Yellow
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters @$ParametersFile `
    --verbose

if ($LASTEXITCODE -eq 0) {{
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "📋 Listing deployed resources:" -ForegroundColor Cyan
    az resource list --resource-group $ResourceGroupName --output table
}} else {{
    Write-Error "❌ Deployment failed!"
    exit 1
}}

Write-Host "🎉 Infrastructure deployment for {environment.upper()} completed!" -ForegroundColor Green
"""
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_environment_requirements(self, environment: str) -> Dict[str, Any]:
        """Get environment-specific requirements for template generation"""
        requirements = {
            'development': {
                'pipeline_complexity': 'simple',
                'approval_gates': False,
                'security_scans': 'basic',
                'deployment_stages': ['validate', 'deploy'],
                'sku_tier': 'basic',
                'monitoring': 'basic',
                'backup_required': False,
                'multi_region': False
            },
            'staging': {
                'pipeline_complexity': 'moderate',
                'approval_gates': True,
                'security_scans': 'standard',
                'deployment_stages': ['validate', 'security-scan', 'deploy', 'test'],
                'sku_tier': 'standard',
                'monitoring': 'standard',
                'backup_required': True,
                'multi_region': False
            },
            'production': {
                'pipeline_complexity': 'advanced',
                'approval_gates': True,
                'security_scans': 'comprehensive',
                'deployment_stages': ['validate', 'security-scan', 'approval', 'deploy-staging', 'approval', 'deploy-production', 'smoke-test'],
                'sku_tier': 'premium',
                'monitoring': 'comprehensive',
                'backup_required': True,
                'multi_region': True
            }
        }
        
        return requirements.get(environment.lower(), requirements['development'])
    
    def _get_cache_key(self, architecture_analysis, policy_compliance, cost_optimization, environment):
        """Generate cache key including cost optimization"""
        key_data = f"{str(architecture_analysis)}{str(policy_compliance)}{str(cost_optimization)}{environment}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key):
        """Get cached templates if available"""
        return self._template_cache.get(cache_key)
    
    def _save_to_cache(self, cache_key, result):
        """Save templates to cache"""
        if len(self._template_cache) >= self._max_cache_size:
            oldest_key = next(iter(self._template_cache))
            del self._template_cache[oldest_key]
        self._template_cache[cache_key] = result
    
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
