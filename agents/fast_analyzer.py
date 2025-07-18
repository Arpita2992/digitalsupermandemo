"""
Fast Mode Architecture Analyzer
Optimized for speed with cached patterns and simplified analysis
"""

import re
import time
from typing import Dict, List, Any
import openai
import os
from dotenv import load_dotenv

load_dotenv()


class FastArchitectureAnalyzer:
    """
    Lightweight version of Architecture Analyzer optimized for speed
    Uses pattern matching and minimal AI calls for fast analysis
    """

    def __init__(self):
        # Initialize with same OpenAI config as main analyzer
        self.azure_endpoint = os.getenv('AZURE_AI_AGENT1_ENDPOINT')
        self.azure_key = os.getenv('AZURE_AI_AGENT1_KEY')
        deployment_env = 'AZURE_AI_AGENT1_DEPLOYMENT'
        self.azure_deployment = os.getenv(deployment_env, 'gpt-4')

        # Optimized for speed
        self.api_timeout = 15  # Reduced timeout
        self.max_retries = 1   # Single retry only

        if self.azure_endpoint and self.azure_key:
            base_endpoint = self.azure_endpoint.split('/openai/deployments')[0]
            deployment_name = self.azure_deployment
            if '/openai/deployments/' in self.azure_endpoint:
                parts = self.azure_endpoint.split('/openai/deployments/')
                deployment_name = parts[1].split('/')[0]

            self.openai_client = openai.AzureOpenAI(
                azure_endpoint=base_endpoint,
                api_key=self.azure_key,
                api_version="2024-10-21",
                timeout=self.api_timeout,
                max_retries=self.max_retries
            )
            self.model_name = deployment_name
        else:
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                timeout=self.api_timeout,
                max_retries=self.max_retries
            )
            self.model_name = "gpt-4"

        # Lightweight cache
        self._cache = {}
        self._max_cache_size = 50

        # Pre-compiled patterns for instant matching
        self._service_patterns = self._compile_service_patterns()
        self._region_patterns = self._compile_region_patterns()

        timeout_msg = f"⚡ Fast Architecture Analyzer initialized "
        timeout_msg += f"(timeout: {self.api_timeout}s)"
        print(timeout_msg)
    
    def _compile_service_patterns(self):
        """Pre-compile common Azure service patterns for instant detection"""
        patterns = {}
        
        # Core compute services
        patterns['compute'] = [
            (re.compile(r'\b(azure\s+)?app\s+service\b', re.IGNORECASE), 'Microsoft.Web/sites'),
            (re.compile(r'\b(azure\s+)?virtual\s+(machine|vm)\b', re.IGNORECASE), 'Microsoft.Compute/virtualMachines'),
            (re.compile(r'\b(azure\s+)?functions?\b', re.IGNORECASE), 'Microsoft.Web/sites'),
            (re.compile(r'\b(azure\s+)?kubernetes\s+service|aks\b', re.IGNORECASE), 'Microsoft.ContainerService/managedClusters'),
            (re.compile(r'\b(azure\s+)?container\s+instances\b', re.IGNORECASE), 'Microsoft.ContainerInstance/containerGroups'),
        ]
        
        # Storage services
        patterns['storage'] = [
            (re.compile(r'\b(azure\s+)?storage\s+account\b', re.IGNORECASE), 'Microsoft.Storage/storageAccounts'),
            (re.compile(r'\b(azure\s+)?blob\s+storage\b', re.IGNORECASE), 'Microsoft.Storage/storageAccounts'),
            (re.compile(r'\b(azure\s+)?file\s+storage\b', re.IGNORECASE), 'Microsoft.Storage/storageAccounts'),
        ]
        
        # Database services
        patterns['database'] = [
            (re.compile(r'\b(azure\s+)?sql\s+(database|db)\b', re.IGNORECASE), 'Microsoft.Sql/servers/databases'),
            (re.compile(r'\b(azure\s+)?cosmos\s+db\b', re.IGNORECASE), 'Microsoft.DocumentDB/databaseAccounts'),
            (re.compile(r'\b(azure\s+)?mysql\b', re.IGNORECASE), 'Microsoft.DBforMySQL/servers'),
            (re.compile(r'\b(azure\s+)?postgresql\b', re.IGNORECASE), 'Microsoft.DBforPostgreSQL/servers'),
        ]
        
        # Networking services
        patterns['networking'] = [
            (re.compile(r'\b(azure\s+)?virtual\s+network|vnet\b', re.IGNORECASE), 'Microsoft.Network/virtualNetworks'),
            (re.compile(r'\b(azure\s+)?load\s+balancer\b', re.IGNORECASE), 'Microsoft.Network/loadBalancers'),
            (re.compile(r'\b(azure\s+)?application\s+gateway\b', re.IGNORECASE), 'Microsoft.Network/applicationGateways'),
            (re.compile(r'\b(azure\s+)?network\s+security\s+group|nsg\b', re.IGNORECASE), 'Microsoft.Network/networkSecurityGroups'),
        ]
        
        # Security and management
        patterns['security'] = [
            (re.compile(r'\b(azure\s+)?key\s+vault\b', re.IGNORECASE), 'Microsoft.KeyVault/vaults'),
            (re.compile(r'\b(azure\s+)?monitor\b', re.IGNORECASE), 'Microsoft.Insights/components'),
        ]
        
        return patterns
    
    def _compile_region_patterns(self):
        """Pre-compile Azure region patterns"""
        return [
            (re.compile(r'\beast\s*us\b', re.IGNORECASE), 'eastus'),
            (re.compile(r'\bwest\s*us\b', re.IGNORECASE), 'westus'),
            (re.compile(r'\bcentral\s*us\b', re.IGNORECASE), 'centralus'),
            (re.compile(r'\bnorth\s*europe\b', re.IGNORECASE), 'northeurope'),
            (re.compile(r'\bwest\s*europe\b', re.IGNORECASE), 'westeurope'),
            (re.compile(r'\bsoutheast\s*asia\b', re.IGNORECASE), 'southeastasia'),
            (re.compile(r'\beast\s*asia\b', re.IGNORECASE), 'eastasia'),
        ]
    
    def analyze_file_fast(self, file_content: str, file_type: str) -> Dict[str, Any]:
        """
        Fast analysis using pattern matching and minimal AI
        Target: < 1 second processing time
        """
        start_time = time.time()
        
        try:
            # Step 1: Quick pattern-based service detection
            detected_services = self._detect_services_fast(file_content)
            
            # Step 2: Quick region detection
            detected_region = self._detect_region_fast(file_content)
            
            # Step 3: Minimal AI call for basic template
            basic_template = self._generate_basic_template(detected_services, detected_region)
            
            processing_time = time.time() - start_time
            
            result = {
                "success": True,
                "processing_time": round(processing_time, 2),
                "analysis_mode": "fast",
                "azure_services": detected_services,
                "region": detected_region,
                "bicep_template": basic_template,
                "confidence_score": 0.85,  # Default for fast mode
                "recommendations": [
                    "Consider adding monitoring and logging",
                    "Review security configurations",
                    "Validate resource naming conventions"
                ],
                "complexity_score": len(detected_services) * 0.2,
                "estimated_cost": {
                    "monthly_estimate": "$100-500",
                    "note": "Rough estimate - use Azure Calculator for accuracy"
                }
            }
            
            print(f"⚡ Fast analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"❌ Fast analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "analysis_mode": "fast"
            }
    
    def _detect_services_fast(self, content: str) -> List[Dict[str, Any]]:
        """Fast service detection using pre-compiled patterns"""
        detected = []
        seen_services = set()
        
        # Quick text processing
        content_lower = content.lower()
        
        for category, patterns in self._service_patterns.items():
            for pattern, resource_type in patterns:
                matches = pattern.findall(content)
                if matches and resource_type not in seen_services:
                    service_name = resource_type.split('/')[-1]
                    detected.append({
                        "name": service_name.replace('_', ' ').title(),
                        "type": resource_type,
                        "category": category,
                        "confidence": 0.9,
                        "detected_text": matches[0] if isinstance(matches[0], str) else matches[0][0]
                    })
                    seen_services.add(resource_type)
        
        # Add default services if none detected
        if not detected:
            detected = [
                {
                    "name": "App Service",
                    "type": "Microsoft.Web/sites",
                    "category": "compute",
                    "confidence": 0.5,
                    "detected_text": "default"
                },
                {
                    "name": "Storage Account", 
                    "type": "Microsoft.Storage/storageAccounts",
                    "category": "storage",
                    "confidence": 0.5,
                    "detected_text": "default"
                }
            ]
        
        return detected[:10]  # Limit to 10 services for speed
    
    def _detect_region_fast(self, content: str) -> str:
        """Fast region detection"""
        for pattern, region in self._region_patterns:
            if pattern.search(content):
                return region
        
        return "eastus"  # Default region
    
    def _generate_basic_template(self, services: List[Dict], region: str) -> str:
        """Generate a basic Bicep template without AI"""
        
        # Quick template generation using string formatting
        template_header = f"""// Basic Bicep Template - Generated by Digital Superman Fast Mode
targetScope = 'resourceGroup'

param location string = '{region}'
param environment string = 'dev'
param projectName string = 'myproject'

"""
        
        template_body = ""
        for i, service in enumerate(services):
            resource_name = f"resource{i+1}"
            service_type = service['type']
            
            if 'Web/sites' in service_type:
                template_body += f"""
// App Service
resource {resource_name} 'Microsoft.Web/sites@2022-03-01' = {{
  name: '${{projectName}}-${{environment}}-app'
  location: location
  properties: {{
    serverFarmId: appServicePlan.id
  }}
}}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {{
  name: '${{projectName}}-${{environment}}-plan'
  location: location
  sku: {{
    name: 'B1'
    tier: 'Basic'
  }}
}}
"""
            elif 'Storage/storageAccounts' in service_type:
                template_body += f"""
// Storage Account
resource {resource_name} 'Microsoft.Storage/storageAccounts@2023-01-01' = {{
  name: '${{projectName}}${{environment}}storage'
  location: location
  kind: 'StorageV2'
  sku: {{
    name: 'Standard_LRS'
  }}
}}
"""
            elif 'Sql/servers' in service_type:
                template_body += f"""
// SQL Database
resource {resource_name}Server 'Microsoft.Sql/servers@2022-05-01-preview' = {{
  name: '${{projectName}}-${{environment}}-sql'
  location: location
  properties: {{
    administratorLogin: 'sqladmin'
    administratorLoginPassword: 'TempPassword123!'
  }}
}}

resource {resource_name} 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {{
  parent: {resource_name}Server
  name: '${{projectName}}-${{environment}}-db'
  location: location
  sku: {{
    name: 'Basic'
  }}
}}
"""
        
        return template_header + template_body
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self._max_cache_size
        }


# Export for use in main application
__all__ = ['FastArchitectureAnalyzer']
