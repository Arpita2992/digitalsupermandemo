"""
AI Agent 1: Architecture Analyzer
Analyzes Azure architecture diagrams and extracts components, relationships, and configurations
"""

import json
import re
from typing import Dict, List, Any
import openai
import os
from dotenv import load_dotenv
import hashlib

load_dotenv()

class ArchitectureAnalyzer:
    def __init__(self):
        # Check if Azure AI Foundry configuration is available
        self.azure_endpoint = os.getenv('AZURE_AI_AGENT1_ENDPOINT')
        self.azure_key = os.getenv('AZURE_AI_AGENT1_KEY')
        self.azure_deployment = os.getenv('AZURE_AI_AGENT1_DEPLOYMENT', 'gpt-4')
        
        if self.azure_endpoint and self.azure_key:
            # Use Azure AI Foundry endpoint
            self.openai_client = openai.AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.azure_key,
                api_version="2024-02-01"
            )
            self.model_name = self.azure_deployment
            print(f"✅ Architecture Analyzer: Using Azure AI Foundry endpoint")
        else:
            # Fallback to OpenAI
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
            self.model_name = "gpt-4"
            print(f"⚠️ Architecture Analyzer: Using OpenAI fallback (configure Azure AI Foundry for production)")
        
        # Simple cache for repeated content
        self._cache = {}
        self._max_cache_size = 100  # Limit cache size
    
    def _get_cache_key(self, content):
        """Generate cache key from content"""
        return hashlib.md5(str(content).encode()).hexdigest()
    
    def _get_from_cache(self, cache_key):
        """Get cached result if available"""
        return self._cache.get(cache_key)
    
    def _save_to_cache(self, cache_key, result):
        """Save result to cache"""
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[cache_key] = result

    def analyze_architecture(self, extracted_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the extracted architecture diagram content with performance optimizations
        """
        
        # Handle both string and dictionary input
        if isinstance(extracted_content, str):
            # Convert string to expected dictionary format
            extracted_content = {
                'type': 'text',
                'text': extracted_content,
                'metadata': {
                    'filename': 'uploaded_file.txt'
                }
            }
        
        # Check cache first
        cache_key = self._get_cache_key(extracted_content)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            print("📋 Architecture Analyzer: Using cached result")
            return cached_result
        
        try:
            # First, validate if this is an Azure architecture (with performance optimization)
            validation_result = self._validate_azure_architecture(extracted_content)
            
            if not validation_result['is_azure_architecture']:
                error_result = {
                    'error': 'non_azure_architecture',
                    'error_message': validation_result['error_message'],
                    'detected_platforms': validation_result.get('detected_platforms', []),
                    'non_azure_services': validation_result.get('non_azure_services_found', []),
                    'suggestion': validation_result.get('suggestion', 'Please upload an Azure architecture diagram.'),
                    'tokens_used': 0  # No tokens used for validation errors
                }
                
                # Cache the error result
                self._save_to_cache(cache_key, error_result)
                return error_result
            
            # Prepare the optimized prompt for OpenAI
            analysis_prompt = self._create_optimized_analysis_prompt(extracted_content)
            
            # Use faster model for simpler diagrams, GPT-4 for complex ones
            model_to_use = self._select_optimal_model(extracted_content)
            
            # Call OpenAI API with optimized settings
            response = self.openai_client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Azure architect. Analyze architecture diagrams quickly and accurately. Focus on identifying Azure services, their configurations, and key relationships. Provide structured JSON output."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2500,  # Increased slightly for better accuracy
                timeout=90  # Reduced timeout to 90 seconds
            )
            
            # Parse the response
            analysis_result = self._parse_analysis_response(response.choices[0].message.content)
            
            # Add token usage information
            if hasattr(response, 'usage') and response.usage:
                analysis_result['tokens_used'] = response.usage.total_tokens
            else:
                analysis_result['tokens_used'] = len(analysis_prompt.split()) * 2  # Rough estimate
            
            # Save to cache
            self._save_to_cache(cache_key, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            return {
                'error': f'Architecture analysis failed: {str(e)}',
                'components': [],
                'relationships': [],
                'configurations': {},
                'tokens_used': 0
            }
    
    def _create_optimized_analysis_prompt(self, content: Dict[str, Any]) -> str:
        """Create an optimized prompt for faster and more accurate architecture analysis"""
        
        # Truncate content for faster processing
        text_content = content.get('text', 'No text found')
        if len(text_content) > 4000:
            text_content = text_content[:4000] + "... [truncated for performance]"
        
        prompt = f"""
        You are an expert Azure architect. Analyze this architecture diagram and extract Azure services with high accuracy.

        ARCHITECTURE CONTENT:
        {text_content}

        IMPORTANT: Focus on identifying these Azure services precisely:
        - Virtual Machines (VM) -> "virtual machine"
        - App Service (Web Apps) -> "app service"
        - Azure SQL Database -> "sql database"
        - Storage Account (Blob, Files) -> "storage account"
        - Virtual Network (VNet) -> "virtual network"
        - Application Gateway -> "application gateway"
        - Load Balancer -> "load balancer"
        - Azure Kubernetes Service (AKS) -> "kubernetes service"
        - Container Registry (ACR) -> "container registry"
        - Key Vault -> "key vault"
        - Cosmos DB -> "cosmos db"
        - Redis Cache -> "redis cache"
        - Functions -> "functions"
        - Logic Apps -> "logic apps"
        - Service Bus -> "service bus"
        - Event Hubs -> "event hubs"
        - API Management -> "api management"
        - CDN -> "cdn"
        - Monitor/Application Insights -> "monitor"
        - Active Directory -> "active directory"
        - Security Center -> "security center"
        - Data Factory -> "data factory"
        - Synapse Analytics -> "synapse analytics"
        - Machine Learning -> "machine learning"
        - Cognitive Services -> "cognitive services"
        - IoT Hub -> "iot hub"
        - Stream Analytics -> "stream analytics"
        - Power BI -> "power bi"
        - Network Security Group -> "network security group"
        - Firewall -> "firewall"
        - VPN Gateway -> "vpn gateway"
        - ExpressRoute -> "expressroute"
        - Backup -> "backup"
        - Site Recovery -> "site recovery"

        Respond with ONLY this JSON structure (no additional text):
        {{
            "components": [
                {{
                    "name": "specific_service_name",
                    "type": "exact_service_type_from_above_list",
                    "configuration": {{"region": "region_if_mentioned", "sku": "tier_if_mentioned"}},
                    "dependencies": ["other_service_names"]
                }}
            ],
            "relationships": [
                {{
                    "source": "source_service_name",
                    "target": "target_service_name",
                    "type": "connection_type"
                }}
            ],
            "network_topology": {{
                "vnets": ["vnet_names_if_mentioned"],
                "subnets": ["subnet_names_if_mentioned"]
            }},
            "summary": "One sentence summary of the architecture"
        }}

        CRITICAL: Use exact service type names from the list above. Be precise and comprehensive.
        """
        
        return prompt
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the OpenAI response into structured format with enhanced accuracy"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # Post-process to improve accuracy
                return self._post_process_analysis(result)
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse(response)
        except json.JSONDecodeError:
            return self._fallback_parse(response)
    
    def _select_optimal_model(self, content: Dict[str, Any]) -> str:
        """Select the optimal model based on content complexity"""
        
        text_content = content.get('text', '')
        content_length = len(text_content)
        
        # Count complexity indicators
        complexity_keywords = [
            'microservices', 'kubernetes', 'aks', 'container', 'docker',
            'machine learning', 'ai', 'cognitive', 'data factory', 'synapse',
            'iot', 'stream analytics', 'event hubs', 'service bus',
            'expressroute', 'vpn', 'firewall', 'security center',
            'active directory', 'rbac', 'policy', 'compliance',
            'hybrid', 'multi-region', 'disaster recovery', 'backup'
        ]
        
        complexity_score = sum(1 for keyword in complexity_keywords if keyword.lower() in text_content.lower())
        
        # Simple heuristic: Use GPT-3.5-turbo for simple diagrams
        if content_length < 2000 and complexity_score < 3:
            return "gpt-3.5-turbo"
        
        # Use GPT-4 for complex diagrams
        return self.model_name
    
    def _post_process_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process analysis results to improve accuracy"""
        
        # Normalize service types
        components = result.get('components', [])
        normalized_components = []
        
        service_type_mappings = {
            # Common variations to standard names
            'web app': 'app service',
            'webapp': 'app service',
            'azure app service': 'app service',
            'web application': 'app service',
            
            'sql db': 'sql database',
            'database': 'sql database',
            'azure sql': 'sql database',
            'sql server': 'sql database',
            
            'storage': 'storage account',
            'blob storage': 'storage account',
            'azure storage': 'storage account',
            'blob': 'storage account',
            
            'vnet': 'virtual network',
            'network': 'virtual network',
            'azure virtual network': 'virtual network',
            
            'app gateway': 'application gateway',
            'gateway': 'application gateway',
            'azure application gateway': 'application gateway',
            
            'lb': 'load balancer',
            'balancer': 'load balancer',
            'azure load balancer': 'load balancer',
            
            'aks': 'kubernetes service',
            'kubernetes': 'kubernetes service',
            'azure kubernetes service': 'kubernetes service',
            'k8s': 'kubernetes service',
            
            'acr': 'container registry',
            'registry': 'container registry',
            'azure container registry': 'container registry',
            
            'vault': 'key vault',
            'keyvault': 'key vault',
            'azure key vault': 'key vault',
            
            'cosmosdb': 'cosmos db',
            'cosmos': 'cosmos db',
            'azure cosmos db': 'cosmos db',
            
            'redis': 'redis cache',
            'cache': 'redis cache',
            'azure redis cache': 'redis cache',
            
            'function app': 'functions',
            'azure functions': 'functions',
            'serverless': 'functions',
            
            'logic app': 'logic apps',
            'workflow': 'logic apps',
            'azure logic apps': 'logic apps',
            
            'servicebus': 'service bus',
            'messaging': 'service bus',
            'azure service bus': 'service bus',
            
            'event hub': 'event hubs',
            'events': 'event hubs',
            'azure event hubs': 'event hubs',
            
            'apim': 'api management',
            'api gateway': 'api management',
            'azure api management': 'api management',
            
            'content delivery network': 'cdn',
            'azure cdn': 'cdn',
            
            'monitoring': 'monitor',
            'application insights': 'monitor',
            'azure monitor': 'monitor',
            
            'aad': 'active directory',
            'ad': 'active directory',
            'azure active directory': 'active directory',
            'azure ad': 'active directory',
            
            'asc': 'security center',
            'azure security center': 'security center',
            
            'adf': 'data factory',
            'azure data factory': 'data factory',
            
            'synapse': 'synapse analytics',
            'sql dw': 'synapse analytics',
            'data warehouse': 'synapse analytics',
            'azure synapse analytics': 'synapse analytics',
            
            'ml': 'machine learning',
            'azure ml': 'machine learning',
            'azure machine learning': 'machine learning',
            
            'cognitive': 'cognitive services',
            'ai services': 'cognitive services',
            'azure cognitive services': 'cognitive services',
            
            'azure iot hub': 'iot hub',
            'iot': 'iot hub',
            
            'stream': 'stream analytics',
            'analytics': 'stream analytics',
            'azure stream analytics': 'stream analytics',
            
            'powerbi': 'power bi',
            'power bi premium': 'power bi',
            'pbi': 'power bi',
            
            'nsg': 'network security group',
            'security group': 'network security group',
            'azure network security group': 'network security group',
            
            'azure firewall': 'firewall',
            'fw': 'firewall',
            
            'vpn': 'vpn gateway',
            'azure vpn gateway': 'vpn gateway',
            
            'express route': 'expressroute',
            'azure expressroute': 'expressroute',
            
            'azure backup': 'backup',
            'backup service': 'backup',
            
            'asr': 'site recovery',
            'disaster recovery': 'site recovery',
            'azure site recovery': 'site recovery'
        }
        
        for component in components:
            service_type = component.get('type', '').lower().strip()
            
            # Normalize service type
            if service_type in service_type_mappings:
                component['type'] = service_type_mappings[service_type]
            elif service_type:
                # Keep original if not in mappings
                component['type'] = service_type
            
            # Clean up component name
            component['name'] = component.get('name', '').strip()
            
            normalized_components.append(component)
        
        result['components'] = normalized_components
        
        # Remove duplicates based on service type
        seen_types = set()
        unique_components = []
        for component in normalized_components:
            component_type = component.get('type', '')
            if component_type not in seen_types:
                seen_types.add(component_type)
                unique_components.append(component)
        
        result['components'] = unique_components
        
        return result
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        return {
            'components': [],
            'relationships': [],
            'network_topology': {},
            'security_configuration': {},
            'estimated_costs': {},
            'raw_analysis': response,
            'parsing_note': 'Used fallback parsing due to JSON parsing error'
        }
    
    def get_component_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of analyzed components"""
        components = analysis.get('components', [])
        
        summary = {
            'total_components': len(components),
            'service_types': {},
            'regions': set(),
            'dependencies_count': 0
        }
        
        for component in components:
            service_type = component.get('type', 'unknown')
            if service_type in summary['service_types']:
                summary['service_types'][service_type] += 1
            else:
                summary['service_types'][service_type] = 1
            
            region = component.get('configuration', {}).get('region')
            if region:
                summary['regions'].add(region)
            
            dependencies = component.get('dependencies', [])
            summary['dependencies_count'] += len(dependencies)
        
        summary['regions'] = list(summary['regions'])
        return summary
    
    def _validate_azure_architecture(self, extracted_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate if the uploaded architecture contains Azure resources
        """
        try:
            # Get the text content for analysis
            content_text = ""
            content_type = extracted_content.get('type', 'unknown')
            
            if 'text' in extracted_content:
                content_text = extracted_content['text']
            elif 'content' in extracted_content:
                content_text = str(extracted_content['content'])
            
            # Special handling for image files
            if content_type == 'image':
                # For images, we have limited text content, so we need to be more permissive
                # but still check for obvious non-Azure indicators
                image_text = content_text.lower()
                
                # Check if image metadata or filename contains clear non-Azure indicators
                metadata = extracted_content.get('metadata', {})
                filename = metadata.get('filename', '').lower()
                
                # Strong indicators of non-Azure platforms (more comprehensive)
                strong_non_azure_indicators = [
                    'aws', 'amazon', 'ec2', 's3', 'lambda', 'rds', 'dynamo',
                    'gcp', 'google cloud', 'compute engine', 'cloud storage', 'big query',
                    'oracle cloud', 'oci', 'heroku', 'digitalocean'
                ]
                
                # Check filename and available text
                all_text = f"{image_text} {filename}".lower()
                
                # Also check if the filename explicitly mentions AWS or other platforms
                detected_platforms = []
                
                for indicator in strong_non_azure_indicators:
                    if indicator in all_text:
                        platform_name = {
                            'aws': 'AWS',
                            'amazon': 'AWS',
                            'ec2': 'AWS',
                            's3': 'AWS',
                            'lambda': 'AWS',
                            'rds': 'AWS',
                            'dynamo': 'AWS',
                            'gcp': 'Google Cloud',
                            'google cloud': 'Google Cloud',
                            'compute engine': 'Google Cloud',
                            'cloud storage': 'Google Cloud',
                            'big query': 'Google Cloud',
                            'oracle cloud': 'Oracle Cloud',
                            'oci': 'Oracle Cloud'
                        }.get(indicator, 'Non-Azure')
                        
                        if platform_name not in detected_platforms:
                            detected_platforms.append(platform_name)
                
                # If we found strong non-Azure indicators, reject the file
                if detected_platforms:
                    return {
                        'is_azure_architecture': False,
                        'error_message': "❌ Non-Azure architecture detected. We only support Azure-related diagrams. Please upload Azure architecture diagrams.",
                        'detected_platforms': detected_platforms,
                        'confidence_score': 0.9,  # High confidence it's not Azure
                        'suggestion': "Upload Azure architecture diagrams with services like Virtual Machines, App Service, Storage Accounts, SQL Database, etc."
                    }
                
                # Check if filename contains Azure indicators
                azure_indicators = ['azure', 'microsoft', 'az-', 'azure-']
                azure_found = any(indicator in all_text for indicator in azure_indicators)
                
                if azure_found:
                    print(f"✅ Image file with Azure indicators detected. Proceeding with analysis...")
                    return {
                        'is_azure_architecture': True,
                        'confidence_score': 0.7,
                        'note': f'Image file with Azure indicators in filename: {filename}'
                    }
                
                # For images without clear indicators, we need to be more strict
                # Ask user to use more descriptive filename or text-based format
                return {
                    'is_azure_architecture': False,
                    'error_message': "❌ Non-Azure architecture detected. We only support Azure-related diagrams. Please upload Azure architecture diagrams.",
                    'detected_platforms': ['Unknown'],
                    'confidence_score': 0.0,
                    'suggestion': "Use text-based formats like .drawio, .svg, or .xml for better validation or include 'azure' in the filename."
                }
            
            # Regular text-based validation for non-image files
            if not content_text.strip():
                # Empty content - let it proceed but with low confidence
                return {
                    'is_azure_architecture': True,
                    'confidence_score': 0.3,
                    'note': 'Empty content detected - validation skipped'
                }
            
            # Create validation prompt
            validation_prompt = f"""
Analyze the following architecture diagram content and determine:
1. Is this primarily an Azure cloud architecture? 
2. What cloud platforms/services are mentioned?
3. Are there any non-Azure cloud services (AWS, GCP, Oracle, etc.)?

Pay special attention to:
- AWS services like EC2, S3, Lambda, RDS, DynamoDB, CloudFront, Route53, ELB, VPC, API Gateway
- Google Cloud services like Compute Engine, Cloud Storage, BigQuery, Cloud Functions, GKE
- Oracle Cloud services
- Azure services like Virtual Machines, App Service, Storage Accounts, SQL Database, Cosmos DB, Key Vault

Content to analyze:
{content_text[:2000]}  # Limit for faster analysis

Respond in JSON format:
{{
    "is_azure_architecture": true/false,
    "confidence_score": 0.0-1.0,
    "azure_services_found": ["list of Azure services found"],
    "non_azure_services_found": ["list of non-Azure services found"],
    "detected_platforms": ["Azure", "AWS", "GCP", etc.],
    "primary_platform": "dominant platform name",
    "reasoning": "brief explanation of the decision"
}}
"""
            
            # Call OpenAI for validation
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for validation
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cloud architecture expert. Identify cloud platforms and services in architecture diagrams."
                    },
                    {
                        "role": "user", 
                        "content": validation_prompt
                    }
                ],
                temperature=0.1,
                max_tokens=500,
                timeout=60  # 1 minute timeout for validation
            )
            
            # Parse validation response
            validation_result = self._parse_validation_response(response.choices[0].message.content)
            
            # Determine if this is acceptable Azure architecture
            is_azure = validation_result.get('is_azure_architecture', False)
            confidence = validation_result.get('confidence_score', 0.0)
            non_azure_services = validation_result.get('non_azure_services_found', [])
            detected_platforms = validation_result.get('detected_platforms', [])
            primary_platform = validation_result.get('primary_platform', 'Unknown')
            reasoning = validation_result.get('reasoning', '')
            
            # Stricter validation - require higher confidence for Azure or explicitly reject non-Azure
            if not is_azure or confidence < 0.5 or (non_azure_services and len(non_azure_services) > 0):
                error_message = "❌ Non-Azure architecture detected. We only support Azure-related diagrams. Please upload Azure architecture diagrams."
                
                return {
                    'is_azure_architecture': False,
                    'error_message': error_message,
                    'detected_platforms': detected_platforms,
                    'confidence_score': confidence,
                    'non_azure_services': non_azure_services,
                    'suggestion': "Upload Azure architecture diagrams with services like Virtual Machines, App Service, Storage Accounts, SQL Database, etc."
                }
            
            return {
                'is_azure_architecture': True,
                'confidence_score': confidence,
                'azure_services_found': validation_result.get('azure_services_found', []),
                'note': f'Validated as Azure architecture with {confidence:.1%} confidence'
            }
            
        except Exception as e:
            print(f"⚠️ Validation error: {str(e)}")
            
            # Check if this was an image file that failed validation
            content_type = extracted_content.get('type', 'unknown')
            if content_type == 'image':
                return {
                    'is_azure_architecture': False,
                    'error_message': "❌ Unable to validate image content. For image files, please ensure the filename clearly indicates it's an Azure architecture (e.g., 'azure-architecture.png') or use text-based formats like .drawio, .svg, or .xml for better validation.",
                    'detected_platforms': ['Unknown'],
                    'confidence_score': 0.0,
                    'suggestion': "Consider using Draw.io (.drawio), SVG, or other text-based diagram formats for better validation, or ensure your image filename contains 'azure' to indicate it's an Azure architecture."
                }
            
            # For non-image files, use fallback method
            fallback_result = self._fallback_validation(content_text if 'content_text' in locals() else str(extracted_content))
            return fallback_result
    
    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse the validation response from OpenAI"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback: analyze text content for cloud services
                return self._fallback_validation(response)
        except json.JSONDecodeError:
            return self._fallback_validation(response)
    
    def _fallback_validation(self, response: str) -> Dict[str, Any]:
        """Fallback validation using keyword matching"""
        response_lower = response.lower()
        
        # Azure service keywords (more comprehensive)
        azure_keywords = [
            'azure', 'microsoft', 'app service', 'virtual machine', 'vm', 'storage account',
            'sql database', 'cosmos db', 'key vault', 'application gateway', 'load balancer',
            'virtual network', 'subnet', 'resource group', 'subscription', 'tenant',
            'azure functions', 'service bus', 'event hubs', 'azure active directory',
            'azure sql', 'azure storage', 'azure blob', 'azure table', 'azure queue',
            'azure kubernetes service', 'aks', 'azure container', 'azure app service',
            'azure web app', 'azure logic apps', 'azure data factory', 'azure synapse',
            'azure devops', 'azure pipelines', 'azure boards', 'azure repos',
            'azure monitor', 'azure security center', 'azure sentinel', 'azure firewall',
            'azure front door', 'azure cdn', 'azure traffic manager', 'azure dns',
            'azure backup', 'azure site recovery', 'azure migrate', 'azure arc'
        ]
        
        # Non-Azure cloud keywords (more comprehensive)
        non_azure_keywords = [
            'aws', 'amazon', 'ec2', 's3', 'lambda', 'rds', 'dynamo', 'cloudfront',
            'route53', 'elb', 'alb', 'nlb', 'vpc', 'api gateway', 'cloudwatch',
            'cloudtrail', 'cloudformation', 'elastic beanstalk', 'ecs', 'eks',
            'fargate', 'sqs', 'sns', 'kinesis', 'redshift', 'athena', 'glue',
            'google cloud', 'gcp', 'compute engine', 'cloud storage', 'big query',
            'cloud functions', 'cloud run', 'gke', 'cloud sql', 'firebase',
            'oracle cloud', 'oci', 'heroku', 'digitalocean', 'alibaba cloud',
            'linode', 'vultr', 'ibm cloud', 'salesforce', 'snowflake'
        ]
        
        # AWS-specific patterns that are strong indicators
        aws_strong_indicators = ['ec2', 's3', 'lambda', 'rds', 'dynamo', 'cloudfront', 'route53']
        gcp_strong_indicators = ['compute engine', 'cloud storage', 'big query', 'cloud functions']
        
        azure_count = sum(1 for keyword in azure_keywords if keyword in response_lower)
        non_azure_count = sum(1 for keyword in non_azure_keywords if keyword in response_lower)
        
        # Check for strong AWS indicators
        aws_strong_count = sum(1 for keyword in aws_strong_indicators if keyword in response_lower)
        gcp_strong_count = sum(1 for keyword in gcp_strong_indicators if keyword in response_lower)
        
        # If we find strong AWS/GCP indicators, it's definitely not Azure
        if aws_strong_count > 0 or gcp_strong_count > 0:
            is_azure = False
            confidence = 0.9  # High confidence it's not Azure
        else:
            is_azure = azure_count > non_azure_count and azure_count > 0
            confidence = min(azure_count / max(azure_count + non_azure_count, 1), 1.0)
        
        detected_platforms = []
        non_azure_services = []
        
        if azure_count > 0:
            detected_platforms.append('Azure')
        if 'aws' in response_lower or any(keyword in response_lower for keyword in aws_strong_indicators):
            detected_platforms.append('AWS')
            non_azure_services.extend([kw for kw in aws_strong_indicators if kw in response_lower])
        if 'google cloud' in response_lower or 'gcp' in response_lower or gcp_strong_count > 0:
            detected_platforms.append('Google Cloud')
            non_azure_services.extend([kw for kw in gcp_strong_indicators if kw in response_lower])
        
        return {
            'is_azure_architecture': is_azure,
            'confidence_score': confidence,
            'azure_services_found': [kw for kw in azure_keywords if kw in response_lower],
            'non_azure_services_found': non_azure_services,
            'detected_platforms': detected_platforms,
            'primary_platform': 'Azure' if is_azure else (detected_platforms[0] if detected_platforms else 'Unknown')
        }
