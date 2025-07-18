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
        
        # Timeout configuration for faster responses
        self.api_timeout = 30  # Reduced from default 60 seconds
        self.max_retries = 2   # Reduced retries for faster failure
        
        if self.azure_endpoint and self.azure_key:
            # Extract base endpoint from full URL
            base_endpoint = self.azure_endpoint.split('/openai/deployments')[0]
            
            # Extract deployment name from endpoint URL 
            if '/openai/deployments/' in self.azure_endpoint:
                deployment_name = self.azure_endpoint.split('/openai/deployments/')[1].split('/')[0]
            else:
                deployment_name = self.azure_deployment
            
            # Use Azure AI Foundry endpoint with timeout
            self.openai_client = openai.AzureOpenAI(
                azure_endpoint=base_endpoint,
                api_key=self.azure_key,
                api_version="2024-10-21",  # Updated API version
                timeout=self.api_timeout,
                max_retries=self.max_retries
            )
            self.model_name = deployment_name
            print(f"✅ Architecture Analyzer: Using Azure AI Foundry endpoint: {base_endpoint}")
            print(f"🎯 Using deployment: {deployment_name}")
            print(f"⚡ Timeout: {self.api_timeout}s, Max retries: {self.max_retries}")
        else:
            # Fallback to OpenAI with timeout
            self.openai_client = openai.OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                timeout=self.api_timeout,
                max_retries=self.max_retries
            )
            self.model_name = "gpt-4"
            print(f"⚠️ Architecture Analyzer: Using OpenAI fallback (configure Azure AI Foundry for production)")
            print(f"⚡ Timeout: {self.api_timeout}s, Max retries: {self.max_retries}")
        
        # Enhanced caching system
        self._cache = {}
        self._max_cache_size = 200  # Increased cache size
        self._cache_hits = 0
        self._cache_misses = 0
        
        # Pre-compiled patterns for faster processing
        self._azure_service_patterns = self._compile_azure_service_patterns()
        self._complexity_patterns = self._compile_complexity_patterns()
        
        # Service detection confidence thresholds
        self._confidence_threshold = 0.95
        
    def _compile_azure_service_patterns(self):
        """Pre-compile regex patterns for faster service detection"""
        import re
        
        # High-confidence patterns for common Azure services
        high_confidence_patterns = [
            (re.compile(r'\b(azure\s+)?app\s+service\b', re.IGNORECASE), 'app service'),
            (re.compile(r'\b(azure\s+)?sql\s+(database|db)\b', re.IGNORECASE), 'sql database'),
            (re.compile(r'\b(azure\s+)?storage\s+account\b', re.IGNORECASE), 'storage account'),
            (re.compile(r'\b(azure\s+)?virtual\s+(machine|vm)\b', re.IGNORECASE), 'virtual machine'),
            (re.compile(r'\b(azure\s+)?kubernetes\s+service|aks\b', re.IGNORECASE), 'kubernetes service'),
            (re.compile(r'\b(azure\s+)?container\s+registry|acr\b', re.IGNORECASE), 'container registry'),
            (re.compile(r'\b(azure\s+)?key\s+vault\b', re.IGNORECASE), 'key vault'),
            (re.compile(r'\b(azure\s+)?cosmos\s+db\b', re.IGNORECASE), 'cosmos db'),
            (re.compile(r'\b(azure\s+)?application\s+gateway\b', re.IGNORECASE), 'application gateway'),
            (re.compile(r'\b(azure\s+)?load\s+balancer\b', re.IGNORECASE), 'load balancer'),
            (re.compile(r'\b(azure\s+)?virtual\s+network|vnet\b', re.IGNORECASE), 'virtual network'),
            (re.compile(r'\b(azure\s+)?functions?\b', re.IGNORECASE), 'functions'),
            (re.compile(r'\b(azure\s+)?redis\s+cache\b', re.IGNORECASE), 'redis cache'),
            (re.compile(r'\b(azure\s+)?service\s+bus\b', re.IGNORECASE), 'service bus'),
            (re.compile(r'\b(azure\s+)?event\s+hubs?\b', re.IGNORECASE), 'event hubs'),
            (re.compile(r'\b(azure\s+)?api\s+management|apim\b', re.IGNORECASE), 'api management'),
            (re.compile(r'\b(azure\s+)?cdn\b', re.IGNORECASE), 'cdn'),
            (re.compile(r'\b(azure\s+)?monitor\b', re.IGNORECASE), 'monitor'),
            (re.compile(r'\b(azure\s+)?active\s+directory|aad\b', re.IGNORECASE), 'active directory'),
            (re.compile(r'\b(azure\s+)?data\s+factory|adf\b', re.IGNORECASE), 'data factory'),
            (re.compile(r'\b(azure\s+)?synapse\s+analytics?\b', re.IGNORECASE), 'synapse analytics'),
            (re.compile(r'\b(azure\s+)?machine\s+learning|azure\s+ml\b', re.IGNORECASE), 'machine learning'),
            (re.compile(r'\b(azure\s+)?iot\s+hub\b', re.IGNORECASE), 'iot hub'),
            (re.compile(r'\b(azure\s+)?stream\s+analytics\b', re.IGNORECASE), 'stream analytics'),
            (re.compile(r'\b(azure\s+)?logic\s+apps?\b', re.IGNORECASE), 'logic apps'),
            (re.compile(r'\b(azure\s+)?security\s+center\b', re.IGNORECASE), 'security center'),
            (re.compile(r'\b(azure\s+)?cognitive\s+services?\b', re.IGNORECASE), 'cognitive services'),
            (re.compile(r'\bpower\s+bi\b', re.IGNORECASE), 'power bi'),
            (re.compile(r'\b(azure\s+)?firewall\b', re.IGNORECASE), 'firewall'),
            (re.compile(r'\b(azure\s+)?vpn\s+gateway\b', re.IGNORECASE), 'vpn gateway'),
            (re.compile(r'\b(azure\s+)?backup\b', re.IGNORECASE), 'backup'),
            (re.compile(r'\b(azure\s+)?site\s+recovery\b', re.IGNORECASE), 'site recovery'),
            (re.compile(r'\b(azure\s+)?postgresql\b', re.IGNORECASE), 'postgresql'),
            (re.compile(r'\b(azure\s+)?mysql\b', re.IGNORECASE), 'mysql'),
            (re.compile(r'\b(azure\s+)?mariadb\b', re.IGNORECASE), 'mariadb'),
            (re.compile(r'\b(azure\s+)?data\s+lake\b', re.IGNORECASE), 'data lake'),
            (re.compile(r'\b(azure\s+)?sentinel\b', re.IGNORECASE), 'sentinel'),
            (re.compile(r'\b(azure\s+)?log\s+analytics\b', re.IGNORECASE), 'log analytics'),
            (re.compile(r'\b(azure\s+)?event\s+grid\b', re.IGNORECASE), 'event grid'),
            (re.compile(r'\b(azure\s+)?batch\b', re.IGNORECASE), 'batch'),
            (re.compile(r'\b(azure\s+)?analysis\s+services\b', re.IGNORECASE), 'analysis services'),
            (re.compile(r'\b(azure\s+)?time\s+series\s+insights\b', re.IGNORECASE), 'time series insights'),
            (re.compile(r'\b(azure\s+)?devops\b', re.IGNORECASE), 'devops'),
            (re.compile(r'\b(azure\s+)?network\s+security\s+group|nsg\b', re.IGNORECASE), 'network security group'),
            (re.compile(r'\b(azure\s+)?expressroute\b', re.IGNORECASE), 'expressroute'),
            (re.compile(r'\b(azure\s+)?search\s+service\b', re.IGNORECASE), 'search service'),
            (re.compile(r'\b(azure\s+)?container\s+instances\b', re.IGNORECASE), 'container instances'),
            (re.compile(r'\b(azure\s+)?notification\s+hubs?\b', re.IGNORECASE), 'notification hubs'),
        ]
        
        # Medium confidence patterns
        medium_confidence_patterns = [
            (re.compile(r'\bweb\s+app\b', re.IGNORECASE), 'app service'),
            (re.compile(r'\bdatabase\b', re.IGNORECASE), 'sql database'),
            (re.compile(r'\bstorage\b', re.IGNORECASE), 'storage account'),
            (re.compile(r'\bvm\b', re.IGNORECASE), 'virtual machine'),
            (re.compile(r'\bk8s\b', re.IGNORECASE), 'kubernetes service'),
            (re.compile(r'\bregistry\b', re.IGNORECASE), 'container registry'),
            (re.compile(r'\bvault\b', re.IGNORECASE), 'key vault'),
            (re.compile(r'\bcosmos\b', re.IGNORECASE), 'cosmos db'),
            (re.compile(r'\bgateway\b', re.IGNORECASE), 'application gateway'),
            (re.compile(r'\bbalancer\b', re.IGNORECASE), 'load balancer'),
            (re.compile(r'\bnetwork\b', re.IGNORECASE), 'virtual network'),
            (re.compile(r'\bserverless\b', re.IGNORECASE), 'functions'),
            (re.compile(r'\bcache\b', re.IGNORECASE), 'redis cache'),
            (re.compile(r'\bmessaging\b', re.IGNORECASE), 'service bus'),
            (re.compile(r'\bevents?\b', re.IGNORECASE), 'event hubs'),
            (re.compile(r'\bapi\b', re.IGNORECASE), 'api management'),
            (re.compile(r'\bmonitoring\b', re.IGNORECASE), 'monitor'),
            (re.compile(r'\bidentity\b', re.IGNORECASE), 'active directory'),
            (re.compile(r'\betl\b', re.IGNORECASE), 'data factory'),
            (re.compile(r'\bwarehouse\b', re.IGNORECASE), 'synapse analytics'),
            (re.compile(r'\bml\b', re.IGNORECASE), 'machine learning'),
            (re.compile(r'\biot\b', re.IGNORECASE), 'iot hub'),
            (re.compile(r'\bstreaming\b', re.IGNORECASE), 'stream analytics'),
            (re.compile(r'\bworkflow\b', re.IGNORECASE), 'logic apps'),
            (re.compile(r'\bsecurity\b', re.IGNORECASE), 'security center'),
            (re.compile(r'\bai\b', re.IGNORECASE), 'cognitive services'),
            (re.compile(r'\breporting\b', re.IGNORECASE), 'power bi'),
            (re.compile(r'\bfirewall\b', re.IGNORECASE), 'firewall'),
            (re.compile(r'\bvpn\b', re.IGNORECASE), 'vpn gateway'),
            (re.compile(r'\bbackup\b', re.IGNORECASE), 'backup'),
            (re.compile(r'\brecovery\b', re.IGNORECASE), 'site recovery'),
            (re.compile(r'\bpostgres\b', re.IGNORECASE), 'postgresql'),
            (re.compile(r'\bmysql\b', re.IGNORECASE), 'mysql'),
            (re.compile(r'\bmariadb\b', re.IGNORECASE), 'mariadb'),
            (re.compile(r'\blake\b', re.IGNORECASE), 'data lake'),
            (re.compile(r'\bsiem\b', re.IGNORECASE), 'sentinel'),
            (re.compile(r'\blogs\b', re.IGNORECASE), 'log analytics'),
            (re.compile(r'\bevent\b', re.IGNORECASE), 'event grid'),
            (re.compile(r'\bbatch\b', re.IGNORECASE), 'batch'),
            (re.compile(r'\banalysis\b', re.IGNORECASE), 'analysis services'),
            (re.compile(r'\btime\s+series\b', re.IGNORECASE), 'time series insights'),
            (re.compile(r'\bdevops\b', re.IGNORECASE), 'devops'),
            (re.compile(r'\bsearch\b', re.IGNORECASE), 'search service'),
            (re.compile(r'\bcontainer\b', re.IGNORECASE), 'container instances'),
            (re.compile(r'\bnotification\b', re.IGNORECASE), 'notification hubs'),
        ]
        
        self._azure_service_patterns = {
            'high_confidence': high_confidence_patterns,
            'medium_confidence': medium_confidence_patterns
        }
        
        return self._azure_service_patterns
    
    def _compile_complexity_patterns(self):
        """Pre-compile patterns for complexity detection"""
        import re
        
        return [
            re.compile(r'\b(microservices?|micro-services?)\b', re.IGNORECASE),
            re.compile(r'\b(kubernetes|k8s|aks|container)\b', re.IGNORECASE),
            re.compile(r'\b(machine\s+learning|ai|cognitive|ml)\b', re.IGNORECASE),
            re.compile(r'\b(data\s+factory|synapse|databricks)\b', re.IGNORECASE),
            re.compile(r'\b(iot|event\s+hubs|stream\s+analytics)\b', re.IGNORECASE),
            re.compile(r'\b(expressroute|vpn|firewall|security)\b', re.IGNORECASE),
            re.compile(r'\b(hybrid|multi-region|disaster\s+recovery)\b', re.IGNORECASE),
            re.compile(r'\b(rbac|policy|compliance|governance)\b', re.IGNORECASE),
        ]
    
    def _get_cache_key(self, content):
        """Generate optimized cache key from content"""
        # Create a more efficient cache key
        if isinstance(content, dict):
            text_content = content.get('text', '')
            metadata = content.get('metadata', {})
            filename = metadata.get('filename', '')
            
            # Create hash from key components only
            key_content = f"{text_content[:500]}{filename}"  # First 500 chars + filename
            return hashlib.md5(key_content.encode()).hexdigest()
        else:
            return hashlib.md5(str(content)[:500].encode()).hexdigest()
    
    def _get_from_cache(self, cache_key):
        """Get cached result if available"""
        result = self._cache.get(cache_key)
        if result:
            self._cache_hits += 1
            return result
        else:
            self._cache_misses += 1
            return None
    
    def _save_to_cache(self, cache_key, result):
        """Save result to cache with LRU eviction"""
        if len(self._cache) >= self._max_cache_size:
            # Remove oldest entry (simple FIFO for now)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[cache_key] = result
    
    def _quick_service_detection(self, text_content: str) -> Dict[str, Any]:
        """Fast pattern-based service detection before AI analysis"""
        detected_services = {}
        confidence_scores = {}
        
        # Apply high-confidence patterns first
        for pattern, service_type in self._azure_service_patterns['high_confidence']:
            matches = pattern.findall(text_content)
            if matches:
                detected_services[service_type] = {
                    'matches': len(matches),
                    'confidence': 0.9,
                    'pattern_type': 'high_confidence'
                }
                confidence_scores[service_type] = 0.9
        
        # Apply medium-confidence patterns for missed services
        for pattern, service_type in self._azure_service_patterns['medium_confidence']:
            if service_type not in detected_services:
                matches = pattern.findall(text_content)
                if matches:
                    detected_services[service_type] = {
                        'matches': len(matches),
                        'confidence': 0.6,
                        'pattern_type': 'medium_confidence'
                    }
                    confidence_scores[service_type] = 0.6
        
        return {
            'detected_services': detected_services,
            'service_count': len(detected_services),
            'average_confidence': sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0,
            'high_confidence_services': [s for s, data in detected_services.items() if data['confidence'] >= 0.9]
        }

    def _parallel_analyze_components(self, text_content: str, pre_detected_services: Dict[str, Any]) -> Dict[str, Any]:
        """Parallel analysis of different component types"""
        import concurrent.futures
        
        # Define analysis tasks
        analysis_tasks = {
            'compute_services': self._analyze_compute_services,
            'storage_services': self._analyze_storage_services,
            'network_services': self._analyze_network_services,
            'database_services': self._analyze_database_services,
            'security_services': self._analyze_security_services,
            'monitoring_services': self._analyze_monitoring_services
        }
        
        results = {}
        
        # Run analysis tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            future_to_task = {
                executor.submit(task_func, text_content, pre_detected_services): task_name
                for task_name, task_func in analysis_tasks.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    results[task_name] = future.result(timeout=3.0)  # 3 second timeout per task
                except Exception as exc:
                    print(f'Analysis task {task_name} generated an exception: {exc}')
                    results[task_name] = []
        
        return results
    
    def _analyze_compute_services(self, text_content: str, pre_detected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze compute services with enhanced patterns"""
        compute_services = []
        
        # Enhanced compute patterns
        compute_patterns = {
            'virtual_machines': [
                r'virtual\s+machine', r'vm\b', r'azure\s+vm', r'compute\s+instance',
                r'windows\s+server', r'linux\s+server', r'ubuntu\s+server'
            ],
            'app_service': [
                r'app\s+service', r'web\s+app', r'webapp', r'azure\s+app',
                r'web\s+service', r'application\s+service'
            ],
            'kubernetes': [
                r'aks', r'kubernetes', r'container\s+service', r'k8s',
                r'azure\s+kubernetes', r'container\s+orchestration'
            ],
            'functions': [
                r'azure\s+functions', r'function\s+app', r'serverless',
                r'functions', r'lambda'
            ],
            'batch': [
                r'azure\s+batch', r'batch\s+processing', r'batch\s+service',
                r'compute\s+batch'
            ]
        }
        
        for service_type, patterns in compute_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    compute_services.append({
                        'type': service_type,
                        'name': service_type.replace('_', ' ').title(),
                        'matches': len(matches),
                        'confidence': 0.8,
                        'category': 'compute'
                    })
                    break  # Avoid duplicates
        
        return compute_services
    
    def _analyze_storage_services(self, text_content: str, pre_detected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze storage services with enhanced patterns"""
        storage_services = []
        
        storage_patterns = {
            'storage_account': [
                r'storage\s+account', r'blob\s+storage', r'azure\s+storage',
                r'storage\s+service', r'data\s+storage'
            ],
            'cosmos_db': [
                r'cosmos\s+db', r'cosmosdb', r'document\s+db', r'nosql',
                r'azure\s+cosmos'
            ],
            'data_lake': [
                r'data\s+lake', r'adls', r'azure\s+data\s+lake',
                r'data\s+lake\s+storage'
            ],
            'sql_database': [
                r'sql\s+database', r'azure\s+sql', r'sql\s+server',
                r'managed\s+instance', r'database\s+server'
            ],
            'redis_cache': [
                r'redis', r'cache', r'azure\s+cache', r'redis\s+cache',
                r'in-memory\s+cache'
            ]
        }
        
        for service_type, patterns in storage_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    storage_services.append({
                        'type': service_type,
                        'name': service_type.replace('_', ' ').title(),
                        'matches': len(matches),
                        'confidence': 0.8,
                        'category': 'storage'
                    })
                    break
        
        return storage_services
    
    def _analyze_network_services(self, text_content: str, pre_detected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze network services with enhanced patterns"""
        network_services = []
        
        network_patterns = {
            'virtual_network': [
                r'virtual\s+network', r'vnet', r'azure\s+vnet', r'network',
                r'subnet', r'vpc'
            ],
            'load_balancer': [
                r'load\s+balancer', r'lb', r'azure\s+lb', r'application\s+gateway',
                r'traffic\s+manager'
            ],
            'vpn_gateway': [
                r'vpn\s+gateway', r'vpn', r'site-to-site', r'point-to-site',
                r'virtual\s+gateway'
            ],
            'application_gateway': [
                r'application\s+gateway', r'app\s+gateway', r'waf',
                r'web\s+application\s+firewall'
            ],
            'cdn': [
                r'cdn', r'content\s+delivery', r'azure\s+cdn',
                r'content\s+delivery\s+network'
            ]
        }
        
        for service_type, patterns in network_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    network_services.append({
                        'type': service_type,
                        'name': service_type.replace('_', ' ').title(),
                        'matches': len(matches),
                        'confidence': 0.8,
                        'category': 'network'
                    })
                    break
        
        return network_services
    
    def _analyze_database_services(self, text_content: str, pre_detected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze database services with enhanced patterns"""
        database_services = []
        
        database_patterns = {
            'azure_sql': [
                r'azure\s+sql', r'sql\s+database', r'sql\s+server',
                r'managed\s+instance', r'sql\s+pool'
            ],
            'cosmos_db': [
                r'cosmos\s+db', r'cosmosdb', r'document\s+database',
                r'nosql\s+database', r'azure\s+cosmos'
            ],
            'postgresql': [
                r'postgresql', r'postgres', r'azure\s+database\s+for\s+postgresql',
                r'postgres\s+database'
            ],
            'mysql': [
                r'mysql', r'azure\s+database\s+for\s+mysql',
                r'mysql\s+database'
            ],
            'mariadb': [
                r'mariadb', r'azure\s+database\s+for\s+mariadb',
                r'maria\s+database'
            ]
        }
        
        for service_type, patterns in database_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    database_services.append({
                        'type': service_type,
                        'name': service_type.replace('_', ' ').title(),
                        'matches': len(matches),
                        'confidence': 0.8,
                        'category': 'database'
                    })
                    break
        
        return database_services
    
    def _analyze_security_services(self, text_content: str, pre_detected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze security services with enhanced patterns"""
        security_services = []
        
        security_patterns = {
            'key_vault': [
                r'key\s+vault', r'azure\s+key\s+vault', r'secrets\s+management',
                r'certificate\s+management', r'key\s+management'
            ],
            'security_center': [
                r'security\s+center', r'azure\s+security\s+center',
                r'defender', r'azure\s+defender'
            ],
            'active_directory': [
                r'active\s+directory', r'azure\s+ad', r'aad',
                r'identity\s+management', r'authentication'
            ],
            'sentinel': [
                r'sentinel', r'azure\s+sentinel', r'siem',
                r'security\s+information'
            ]
        }
        
        for service_type, patterns in security_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    security_services.append({
                        'type': service_type,
                        'name': service_type.replace('_', ' ').title(),
                        'matches': len(matches),
                        'confidence': 0.8,
                        'category': 'security'
                    })
                    break
        
        return security_services
    
    def _analyze_monitoring_services(self, text_content: str, pre_detected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze monitoring services with enhanced patterns"""
        monitoring_services = []
        
        monitoring_patterns = {
            'monitor': [
                r'azure\s+monitor', r'monitoring', r'application\s+insights',
                r'log\s+analytics', r'metrics'
            ],
            'application_insights': [
                r'application\s+insights', r'app\s+insights', r'telemetry',
                r'performance\s+monitoring'
            ],
            'log_analytics': [
                r'log\s+analytics', r'logs', r'azure\s+logs',
                r'log\s+management', r'log\s+aggregation'
            ]
        }
        
        for service_type, patterns in monitoring_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    monitoring_services.append({
                        'type': service_type,
                        'name': service_type.replace('_', ' ').title(),
                        'matches': len(matches),
                        'confidence': 0.8,
                        'category': 'monitoring'
                    })
                    break
        
        return monitoring_services

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
            
            # Get text content for analysis
            text_content = extracted_content.get('text', '')
            
            # Quick pre-detection of services using pattern matching
            pre_detected_services = self._quick_service_detection(text_content)
            
            # Check if we can handle this with pattern matching only (fast path)
            if (pre_detected_services['service_count'] > 0 and 
                pre_detected_services['average_confidence'] > 0.8 and 
                len(text_content) < 2000):
                
                print("🚀 Architecture Analyzer: Using pattern-only fast path")
                
                # Create components from pattern detection
                components = []
                for service_name, service_data in pre_detected_services['detected_services'].items():
                    components.append({
                        'name': service_name.replace('_', ' ').title(),
                        'type': service_name,
                        'category': self._get_service_category(service_name),
                        'confidence': service_data['confidence'],
                        'source': 'pattern_detection'
                    })
                
                # Generate basic relationships
                relationships = self._generate_basic_relationships(components)
                
                analysis_result = {
                    'components': components,
                    'relationships': relationships,
                    'network_topology': {'type': 'cloud_native'},
                    'summary': f'Azure architecture with {len(components)} services detected via pattern matching',
                    'tokens_used': 0,  # No AI tokens used
                    'processing_method': 'pattern_only_fast_path',
                    'confidence': pre_detected_services['average_confidence'],
                    'accuracy_score': pre_detected_services['average_confidence'],
                    'performance_metrics': {
                        'processing_time': 0.001,
                        'method': 'pattern_only',
                        'ai_calls': 0
                    }
                }
                
                # Cache and return fast result
                self._save_to_cache(cache_key, analysis_result)
                return analysis_result
            
            # Use parallel processing for complex diagrams
            elif len(text_content) > 3000 or pre_detected_services['service_count'] > 5:
                # Use hybrid approach: parallel processing + AI validation
                parallel_results = self._parallel_analyze_components(text_content, pre_detected_services)
                
                # Combine results from parallel processing
                all_components = []
                for service_category, services in parallel_results.items():
                    all_components.extend(services)
                
                # Use AI to validate and enhance the results
                ai_analysis = self._ai_validate_and_enhance(text_content, all_components)
                
                # Combine results with AI validation
                analysis_result = {
                    'components': ai_analysis.get('components', all_components),
                    'relationships': ai_analysis.get('relationships', []),
                    'network_topology': ai_analysis.get('network_topology', {}),
                    'summary': ai_analysis.get('summary', f'Azure architecture with {len(all_components)} components'),
                    'tokens_used': ai_analysis.get('tokens_used', 0),
                    'processing_method': 'parallel_hybrid'
                }
            else:
                # Use enhanced AI analysis for simpler diagrams
                analysis_prompt = self._create_optimized_analysis_prompt(extracted_content)
                model_to_use = self._select_optimal_model(extracted_content)
                
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
                    max_tokens=2500,
                    timeout=90
                )
                
                if response and response.choices and len(response.choices) > 0:
                    analysis_result = self._parse_analysis_response(response.choices[0].message.content)
                    
                    # Add token usage information
                    if hasattr(response, 'usage') and response.usage:
                        analysis_result['tokens_used'] = response.usage.total_tokens
                    else:
                        analysis_result['tokens_used'] = len(analysis_prompt.split()) * 2
                    
                    analysis_result['processing_method'] = 'ai_enhanced'
                else:
                    print(f"Standard AI analysis - No response choices: {response}")
                    raise Exception("No response from OpenAI API")
            
            # Post-process to improve accuracy
            analysis_result = self._post_process_analysis(analysis_result)
            
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
    
    def _ai_validate_and_enhance(self, text_content: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use AI to validate and enhance pattern-detected components"""
        
        # Create focused prompt for validation and enhancement
        component_list = []
        for comp in components:
            component_list.append(f"- {comp.get('name', 'Unknown')} ({comp.get('type', 'Unknown')})")
        
        prompt = f"""
        You are an expert Azure architect. Review and enhance this list of detected Azure components from an architecture diagram.

        DETECTED COMPONENTS:
        {chr(10).join(component_list)}

        ARCHITECTURE CONTEXT:
        {text_content[:3000]}  # Truncated for performance

        TASKS:
        1. Validate each detected component (is it actually present in the architecture?)
        2. Identify any missing Azure services that should be included
        3. Determine relationships between components
        4. Identify network topology

        Respond with ONLY this JSON structure:
        {{
            "components": [
                {{
                    "name": "specific_service_name",
                    "type": "exact_azure_service_type",
                    "configuration": {{"region": "region_if_mentioned", "sku": "tier_if_mentioned"}},
                    "dependencies": ["other_service_names"],
                    "validated": true
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
                "vnets": ["vnet_names"],
                "subnets": ["subnet_names"]
            }},
            "summary": "One sentence summary of the validated architecture"
        }}

        IMPORTANT: Only include components that are actually present in the architecture. Add missing components if clearly indicated.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,  # Use the configured model name
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Azure architect focused on validating and enhancing component detection with high accuracy."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                timeout=60
            )
            
            if response and response.choices and len(response.choices) > 0:
                result = self._parse_analysis_response(response.choices[0].message.content)
                
                # Add token usage
                if hasattr(response, 'usage') and response.usage:
                    result['tokens_used'] = response.usage.total_tokens
                else:
                    result['tokens_used'] = len(prompt.split()) * 2
                
                return result
            else:
                print(f"AI validation - No response choices: {response}")
                raise Exception("No response from OpenAI API")
            
        except Exception as e:
            print(f"AI validation failed: {str(e)}")
            return {
                'components': components,  # Return original components as fallback
                'relationships': [],
                'network_topology': {},
                'summary': f'Azure architecture with {len(components)} components (validation failed)',
                'tokens_used': 0
            }

    def _ai_analyze_relationships(self, text_content: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use AI to analyze relationships between pre-detected components"""
        
        # Create focused prompt for relationship analysis
        component_names = [comp['name'] for comp in components]
        
        prompt = f"""
        You are an expert Azure architect. Given these detected Azure components, identify their relationships and network topology.

        DETECTED COMPONENTS:
        {', '.join(component_names)}

        ARCHITECTURE CONTEXT:
        {text_content[:2000]}  # Truncated for performance

        Respond with ONLY this JSON structure:
        {{
            "relationships": [
                {{
                    "source": "source_component_name",
                    "target": "target_component_name",
                    "type": "connection_type"
                }}
            ],
            "network_topology": {{
                "vnets": ["vnet_names"],
                "subnets": ["subnet_names"]
            }},
            "summary": "One sentence summary focusing on component relationships"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_name,  # Use the configured model name
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Azure architect focused on identifying component relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000,
                timeout=30
            )
            
            if response and response.choices and len(response.choices) > 0:
                result = self._parse_analysis_response(response.choices[0].message.content)
                
                # Add token usage
                if hasattr(response, 'usage') and response.usage:
                    result['tokens_used'] = response.usage.total_tokens
                else:
                    result['tokens_used'] = len(prompt.split()) * 2
                
                return result
            else:
                raise Exception("No response from OpenAI API")
            
        except Exception as e:
            return {
                'relationships': [],
                'network_topology': {},
                'summary': f'Azure architecture with {len(components)} components (relationship analysis failed)',
                'tokens_used': 0
            }
    
    def _create_optimized_analysis_prompt(self, content: Dict[str, Any]) -> str:
        """Create an optimized prompt for faster and more accurate architecture analysis"""
        
        # Truncate content for faster processing
        text_content = content.get('text', 'No text found')
        if len(text_content) > 4000:
            text_content = text_content[:4000] + "... [truncated for performance]"
        
        prompt = f"""
        You are an expert Azure architect with extensive knowledge of Azure service icons, naming conventions, and architectural patterns. Analyze this architecture diagram to extract Azure services with maximum accuracy.

        AZURE SERVICES REFERENCE GUIDE:
        🖥️ COMPUTE: 
        - Virtual Machines: VM, Windows Server, Linux → "virtual_machine"
        - App Service: Web App, webapp → "app_service"  
        - Azure Functions: Functions, serverless → "azure_functions"
        - AKS: Kubernetes, K8s → "kubernetes_service"
        - Container Instances: ACI → "container_instances"
        
        🗄️ STORAGE:
        - Storage Account: Blob Storage, File Storage → "storage_account"
        - Data Lake: ADLS, Data Lake Storage → "data_lake_storage"
        - Managed Disks: Premium SSD, Standard HDD → "managed_disks"
        
        🌐 NETWORKING:
        - Virtual Network: VNet → "virtual_network"
        - Application Gateway: App Gateway, WAF → "application_gateway"
        - Load Balancer: LB → "load_balancer"
        - VPN Gateway: Site-to-Site VPN → "vpn_gateway"
        - ExpressRoute: Dedicated connection → "expressroute"
        - CDN: Content Delivery Network → "cdn"
        - Firewall: Azure Firewall → "azure_firewall"
        - Network Security Group: NSG → "network_security_group"
        
        🗃️ DATABASES:
        - SQL Database: Azure SQL, SQL DB → "sql_database"
        - Cosmos DB: NoSQL, DocumentDB → "cosmos_db"
        - PostgreSQL: PostgreSQL DB → "postgresql_database"
        - MySQL: MySQL DB → "mysql_database"
        - Redis Cache: Redis → "redis_cache"
        
        🔐 SECURITY & IDENTITY:
        - Active Directory: AAD, Azure AD → "active_directory"
        - Key Vault: Secrets, Keys → "key_vault"
        - Security Center: ASC → "security_center"
        - Sentinel: SIEM → "azure_sentinel"
        
        📡 INTEGRATION:
        - Service Bus: Messaging → "service_bus"
        - Event Hubs: Event streaming → "event_hubs"
        - Event Grid: Event routing → "event_grid"
        - API Management: APIM, API Gateway → "api_management"
        - Logic Apps: Workflow → "logic_apps"
        
        📊 ANALYTICS & AI:
        - Data Factory: ETL, ADF → "data_factory"
        - Synapse Analytics: Data Warehouse → "synapse_analytics"
        - Stream Analytics: Real-time analytics → "stream_analytics"
        - Machine Learning: Azure ML → "machine_learning"
        - Cognitive Services: AI services → "cognitive_services"
        - Power BI: Business Intelligence → "power_bi"
        
        📱 IOT:
        - IoT Hub: Device management → "iot_hub"
        - IoT Central: SaaS IoT → "iot_central"
        - Time Series Insights: TSI → "time_series_insights"
        
        🔧 MANAGEMENT:
        - Azure Monitor: Monitoring, App Insights → "azure_monitor"
        - Log Analytics: Log workspace → "log_analytics"
        - Azure DevOps: CI/CD → "azure_devops"
        - Backup: Azure Backup → "azure_backup"
        - Site Recovery: DR → "site_recovery"

        ARCHITECTURE CONTENT TO ANALYZE:
        {text_content}

        CRITICAL INSTRUCTIONS:
        1. Use EXACT service type names with underscores (e.g., "app_service" not "app service")
        2. Look for Azure blue colors (#0078D4) and Microsoft iconography
        3. Check for service names in labels, tooltips, and legends
        4. Identify connection lines showing data flow
        5. Extract any mentioned configurations, sizes, or tiers
        6. Provide realistic cost estimates in EUR when possible

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
        
        # Always use the configured model name since we're using Azure AI Foundry
        return self.model_name
    
    def _post_process_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process analysis results to improve accuracy with enhanced validation"""
        
        # Normalize service types
        components = result.get('components', [])
        normalized_components = []
        
        service_type_mappings = {
            # Common variations to standard names
            'web app': 'app service',
            'webapp': 'app service',
            'azure app service': 'app service',
            'web application': 'app service',
            'website': 'app service',
            
            'sql db': 'sql database',
            'database': 'sql database',
            'azure sql': 'sql database',
            'sql server': 'sql database',
            'sql': 'sql database',
            
            'storage': 'storage account',
            'blob storage': 'storage account',
            'azure storage': 'storage account',
            'blob': 'storage account',
            'data storage': 'storage account',
            
            'vnet': 'virtual network',
            'network': 'virtual network',
            'azure virtual network': 'virtual network',
            'vpc': 'virtual network',
            
            'app gateway': 'application gateway',
            'gateway': 'application gateway',
            'azure application gateway': 'application gateway',
            'waf': 'application gateway',
            
            'lb': 'load balancer',
            'balancer': 'load balancer',
            'azure load balancer': 'load balancer',
            'traffic manager': 'load balancer',
            
            'aks': 'kubernetes service',
            'kubernetes': 'kubernetes service',
            'azure kubernetes service': 'kubernetes service',
            'k8s': 'kubernetes service',
            'container service': 'kubernetes service',
            
            'acr': 'container registry',
            'registry': 'container registry',
            'azure container registry': 'container registry',
            
            'vault': 'key vault',
            'keyvault': 'key vault',
            'azure key vault': 'key vault',
            'secrets management': 'key vault',
            
            'cosmosdb': 'cosmos db',
            'cosmos': 'cosmos db',
            'azure cosmos db': 'cosmos db',
            'document db': 'cosmos db',
            'nosql': 'cosmos db',
            
            'redis': 'redis cache',
            'cache': 'redis cache',
            'azure redis cache': 'redis cache',
            'azure cache': 'redis cache',
            
            'function app': 'functions',
            'azure functions': 'functions',
            'serverless': 'functions',
            'function': 'functions',
            
            'logic app': 'logic apps',
            'workflow': 'logic apps',
            'azure logic apps': 'logic apps',
            'logic': 'logic apps',
            
            'servicebus': 'service bus',
            'messaging': 'service bus',
            'azure service bus': 'service bus',
            'message queue': 'service bus',
            
            'event hub': 'event hubs',
            'events': 'event hubs',
            'azure event hubs': 'event hubs',
            'eventhub': 'event hubs',
            
            'apim': 'api management',
            'api gateway': 'api management',
            'azure api management': 'api management',
            'api': 'api management',
            
            'content delivery network': 'cdn',
            'azure cdn': 'cdn',
            'content delivery': 'cdn',
            
            'monitoring': 'monitor',
            'application insights': 'monitor',
            'azure monitor': 'monitor',
            'app insights': 'monitor',
            'metrics': 'monitor',
            
            'aad': 'active directory',
            'ad': 'active directory',
            'azure active directory': 'active directory',
            'azure ad': 'active directory',
            'identity': 'active directory',
            
            'asc': 'security center',
            'azure security center': 'security center',
            'defender': 'security center',
            'azure defender': 'security center',
            
            'adf': 'data factory',
            'azure data factory': 'data factory',
            'etl': 'data factory',
            
            'synapse': 'synapse analytics',
            'sql dw': 'synapse analytics',
            'data warehouse': 'synapse analytics',
            'azure synapse analytics': 'synapse analytics',
            'azure synapse': 'synapse analytics',
            
            'ml': 'machine learning',
            'azure ml': 'machine learning',
            'azure machine learning': 'machine learning',
            'machine learning studio': 'machine learning',
            
            'cognitive': 'cognitive services',
            'ai services': 'cognitive services',
            'azure cognitive services': 'cognitive services',
            'ai': 'cognitive services',
            
            'azure iot hub': 'iot hub',
            'iot': 'iot hub',
            'internet of things': 'iot hub',
            
            'stream': 'stream analytics',
            'analytics': 'stream analytics',
            'azure stream analytics': 'stream analytics',
            'streaming': 'stream analytics',
            
            'powerbi': 'power bi',
            'power bi premium': 'power bi',
            'pbi': 'power bi',
            'power bi embedded': 'power bi',
            
            'nsg': 'network security group',
            'security group': 'network security group',
            'azure network security group': 'network security group',
            'network security': 'network security group',
            
            'azure firewall': 'firewall',
            'fw': 'firewall',
            'firewall': 'firewall',
            
            'vpn': 'vpn gateway',
            'azure vpn gateway': 'vpn gateway',
            'vpn gateway': 'vpn gateway',
            
            'express route': 'expressroute',
            'azure expressroute': 'expressroute',
            'expressroute': 'expressroute',
            
            'azure backup': 'backup',
            'backup service': 'backup',
            'backup': 'backup',
            
            'asr': 'site recovery',
            'disaster recovery': 'site recovery',
            'azure site recovery': 'site recovery',
            'site recovery': 'site recovery',
            
            # VM variations
            'vm': 'virtual machine',
            'virtual machine': 'virtual machine',
            'azure vm': 'virtual machine',
            'compute instance': 'virtual machine',
            'server': 'virtual machine',
            
            # Database variations
            'postgresql': 'postgresql',
            'postgres': 'postgresql',
            'mysql': 'mysql',
            'mariadb': 'mariadb',
            
            # Data services
            'data lake': 'data lake',
            'adls': 'data lake',
            'azure data lake': 'data lake',
            
            # Security services
            'sentinel': 'sentinel',
            'azure sentinel': 'sentinel',
            'siem': 'sentinel',
            
            # Monitoring
            'log analytics': 'log analytics',
            'logs': 'log analytics',
            'azure logs': 'log analytics'
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
            
            # Add confidence score if missing
            if 'confidence' not in component:
                component['confidence'] = 0.7  # Default confidence
            
            # Ensure category is set
            if 'category' not in component:
                component['category'] = self._get_service_category(component['type'])
            
            normalized_components.append(component)
        
        result['components'] = normalized_components
        
        # Remove duplicates based on service type (keeping highest confidence)
        seen_types = {}
        unique_components = []
        
        for component in normalized_components:
            component_type = component.get('type', '')
            if component_type:
                if component_type not in seen_types:
                    seen_types[component_type] = component
                    unique_components.append(component)
                else:
                    # Keep component with higher confidence
                    existing_confidence = seen_types[component_type].get('confidence', 0)
                    current_confidence = component.get('confidence', 0)
                    if current_confidence > existing_confidence:
                        # Replace with higher confidence component
                        for i, existing_comp in enumerate(unique_components):
                            if existing_comp['type'] == component_type:
                                unique_components[i] = component
                                seen_types[component_type] = component
                                break
        
        result['components'] = unique_components
        
        # Validate and clean relationships
        relationships = result.get('relationships', [])
        valid_relationships = []
        component_names = {comp.get('name', '').lower() for comp in unique_components}
        
        for rel in relationships:
            source = rel.get('source', '').lower()
            target = rel.get('target', '').lower()
            
            # Only keep relationships between detected components
            if source in component_names and target in component_names:
                valid_relationships.append(rel)
        
        result['relationships'] = valid_relationships
        
        # Add accuracy score
        total_components = len(unique_components)
        high_confidence_count = sum(1 for comp in unique_components if comp.get('confidence', 0) >= 0.8)
        
        result['accuracy_score'] = (high_confidence_count / total_components) if total_components > 0 else 0
        result['total_components'] = total_components
        result['high_confidence_components'] = high_confidence_count
        
        return result
    
    def _get_service_category(self, service_type: str) -> str:
        """Get the category for a service type"""
        service_categories = {
            'virtual machine': 'compute',
            'app service': 'compute',
            'kubernetes service': 'compute',
            'functions': 'compute',
            'batch': 'compute',
            
            'storage account': 'storage',
            'cosmos db': 'storage',
            'data lake': 'storage',
            'sql database': 'storage',
            'redis cache': 'storage',
            'postgresql': 'storage',
            'mysql': 'storage',
            'mariadb': 'storage',
            
            'virtual network': 'network',
            'load balancer': 'network',
            'application gateway': 'network',
            'vpn gateway': 'network',
            'cdn': 'network',
            'firewall': 'network',
            'network security group': 'network',
            'expressroute': 'network',
            
            'key vault': 'security',
            'security center': 'security',
            'active directory': 'security',
            'sentinel': 'security',
            
            'monitor': 'monitoring',
            'log analytics': 'monitoring',
            
            'api management': 'integration',
            'service bus': 'integration',
            'event hubs': 'integration',
            'logic apps': 'integration',
            
            'data factory': 'analytics',
            'synapse analytics': 'analytics',
            'stream analytics': 'analytics',
            'power bi': 'analytics',
            
            'machine learning': 'ai',
            'cognitive services': 'ai',
            
            'iot hub': 'iot',
            
            'backup': 'management',
            'site recovery': 'management'
        }
        
        return service_categories.get(service_type, 'other')
    
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
                
                # For images without clear indicators, assume it could be Azure
                # since we want to be more permissive for legitimate use cases
                print(f"📋 Image file uploaded. Assuming Azure architecture for analysis...")
                return {
                    'is_azure_architecture': True,
                    'confidence_score': 0.5,  # Lower confidence but still proceed
                    'note': f'Image file assumed to be Azure architecture: {filename}'
                }
            
            # Regular text-based validation for non-image files
            if not content_text.strip():
                # Empty content - let it proceed but with low confidence
                return {
                    'is_azure_architecture': True,
                    'confidence_score': 0.3,
                    'note': 'Empty content detected - validation skipped'
                }
            
            # Fast pattern-based validation instead of AI call
            return self._fast_pattern_validation(content_text)
            
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

    def _get_service_category(self, service_name: str) -> str:
        """Get the category for a service name"""
        service_lower = service_name.lower()
        
        # Compute services
        compute_services = ['app service', 'functions', 'kubernetes service', 'virtual machine', 'container', 'batch', 'logic apps']
        if any(compute in service_lower for compute in compute_services):
            return 'compute'
        
        # Storage services
        storage_services = ['storage account', 'cosmos db', 'sql database', 'redis cache', 'blob storage', 'file storage']
        if any(storage in service_lower for storage in storage_services):
            return 'storage'
        
        # Network services
        network_services = ['application gateway', 'load balancer', 'virtual network', 'cdn', 'firewall', 'vpn']
        if any(network in service_lower for network in network_services):
            return 'network'
        
        # Security services
        security_services = ['key vault', 'active directory', 'security center']
        if any(security in service_lower for security in security_services):
            return 'security'
        
        # Monitoring services
        monitoring_services = ['monitor', 'application insights', 'log analytics']
        if any(monitoring in service_lower for monitoring in monitoring_services):
            return 'monitoring'
        
        # Integration services
        integration_services = ['service bus', 'event hubs', 'event grid', 'api management']
        if any(integration in service_lower for integration in integration_services):
            return 'integration'
        
        return 'other'

    def _generate_basic_relationships(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate basic relationships between components based on common patterns"""
        relationships = []
        
        # Find common relationship patterns
        app_services = [c for c in components if 'app service' in c['type'].lower()]
        databases = [c for c in components if any(db in c['type'].lower() for db in ['sql database', 'cosmos db', 'redis cache'])]
        gateways = [c for c in components if 'gateway' in c['type'].lower()]
        storage = [c for c in components if 'storage' in c['type'].lower()]
        
        # App Service to Database relationships
        for app in app_services:
            for db in databases:
                relationships.append({
                    'source': app['name'],
                    'target': db['name'],
                    'type': 'data_connection',
                    'description': f"{app['name']} connects to {db['name']} for data storage"
                })
        
        # Gateway to App Service relationships
        for gateway in gateways:
            for app in app_services:
                relationships.append({
                    'source': gateway['name'],
                    'target': app['name'],
                    'type': 'traffic_routing',
                    'description': f"{gateway['name']} routes traffic to {app['name']}"
                })
        
        # App Service to Storage relationships
        for app in app_services:
            for stor in storage:
                relationships.append({
                    'source': app['name'],
                    'target': stor['name'],
                    'type': 'storage_connection',
                    'description': f"{app['name']} uses {stor['name']} for file storage"
                })
        
        return relationships

    def _fast_pattern_validation(self, content_text: str) -> Dict[str, Any]:
        """Fast pattern-based validation for Azure architecture content"""
        content_lower = content_text.lower()
        
        # Azure service patterns
        azure_patterns = [
            'azure', 'microsoft', 'app service', 'virtual machine', 'sql database',
            'cosmos db', 'storage account', 'key vault', 'active directory',
            'application gateway', 'load balancer', 'functions', 'kubernetes service',
            'container registry', 'redis cache', 'service bus', 'event hubs',
            'api management', 'cdn', 'monitor', 'application insights'
        ]
        
        # Strong non-Azure patterns
        non_azure_patterns = [
            'aws', 'amazon', 'ec2', 's3', 'lambda', 'rds', 'dynamo',
            'gcp', 'google cloud', 'compute engine', 'cloud storage', 'big query'
        ]
        
        # Count matches
        azure_matches = sum(1 for pattern in azure_patterns if pattern in content_lower)
        non_azure_matches = sum(1 for pattern in non_azure_patterns if pattern in content_lower)
        
        # Determine if it's Azure architecture
        if non_azure_matches > azure_matches and non_azure_matches > 0:
            return {
                'is_azure_architecture': False,
                'error_message': "❌ Non-Azure architecture detected. We only support Azure-related diagrams.",
                'detected_platforms': ['AWS'] if 'aws' in content_lower else ['GCP'] if 'gcp' in content_lower else ['Non-Azure'],
                'confidence_score': 0.8,
                'suggestion': "Upload Azure architecture diagrams with services like App Service, Virtual Machines, SQL Database, etc."
            }
        
        # If Azure services found or no clear non-Azure indicators, proceed
        confidence = min(azure_matches / 10.0, 1.0) if azure_matches > 0 else 0.5
        
        return {
            'is_azure_architecture': True,
            'confidence_score': confidence,
            'azure_services_found': [pattern for pattern in azure_patterns if pattern in content_lower],
            'note': f'Pattern validation: {azure_matches} Azure patterns found'
        }
