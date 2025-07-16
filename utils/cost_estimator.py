"""
Cost Estimator for Azure Resources
Provides cost estimates for Azure resources based on Bicep templates and architecture analysis
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class AzureCostEstimator:
    # Resource type mapping from generic types to Azure resource types
    RESOURCE_TYPE_MAPPING = {
        'FrontDoor': 'Microsoft.Network/frontDoors',
        'ApplicationGateway': 'Microsoft.Network/applicationGateways',
        'VirtualNetwork': 'Microsoft.Network/virtualNetworks',
        'Subnet': 'Microsoft.Network/virtualNetworks/subnets',
        'AppService': 'Microsoft.Web/sites',
        'WebApp': 'Microsoft.Web/sites',
        'SQLDatabase': 'Microsoft.Sql/servers/databases',
        'StorageAccount': 'Microsoft.Storage/storageAccounts',
        'KeyVault': 'Microsoft.KeyVault/vaults',
        'ApplicationInsights': 'Microsoft.Insights/components',
        'LogAnalyticsWorkspace': 'Microsoft.OperationalInsights/workspaces',
        'LogAnalytics': 'Microsoft.OperationalInsights/workspaces',
        'VirtualMachine': 'Microsoft.Compute/virtualMachines',
        'Database': 'Microsoft.Sql/servers/databases',
        'CosmosDB': 'Microsoft.DocumentDB/databaseAccounts',
        'RedisCache': 'Microsoft.Cache/redis',
        'ServiceBus': 'Microsoft.ServiceBus/namespaces',
        'EventHub': 'Microsoft.EventHub/namespaces',
        'LoadBalancer': 'Microsoft.Network/loadBalancers',
        'PublicIP': 'Microsoft.Network/publicIPAddresses',
        'NetworkSecurityGroup': 'Microsoft.Network/networkSecurityGroups',
        'ContainerRegistry': 'Microsoft.ContainerRegistry/registries',
        'AKS': 'Microsoft.ContainerService/managedClusters',
        'Functions': 'Microsoft.Web/sites',
        'ApiManagement': 'Microsoft.ApiManagement/service',
        'CDN': 'Microsoft.Cdn/profiles',
        'TrafficManager': 'Microsoft.Network/trafficManagerProfiles',
        'Monitor': 'Microsoft.Insights/components',
        'Backup': 'Microsoft.RecoveryServices/vaults',
        
        # Additional common mappings
        'AppServicePlan': 'Microsoft.Web/serverfarms',
        'App Service Plan': 'Microsoft.Web/serverfarms',
        'Azure Front Door': 'Microsoft.Network/frontDoors',
        'Application Gateway': 'Microsoft.Network/applicationGateways',
        'Virtual Network': 'Microsoft.Network/virtualNetworks',
        'App Service': 'Microsoft.Web/sites',
        'SQL Database': 'Microsoft.Sql/servers/databases',
        'Storage Account': 'Microsoft.Storage/storageAccounts',
        'Key Vault': 'Microsoft.KeyVault/vaults',
        'Application Insights': 'Microsoft.Insights/components',
        'Log Analytics': 'Microsoft.OperationalInsights/workspaces',
        'Azure SQL Database': 'Microsoft.Sql/servers/databases',
        'Azure Storage Account': 'Microsoft.Storage/storageAccounts',
        'Azure Key Vault': 'Microsoft.KeyVault/vaults',
        'Azure Application Insights': 'Microsoft.Insights/components',
        'Azure Monitor': 'Microsoft.Insights/components',
        'Web Subnet': 'Microsoft.Network/virtualNetworks/subnets',
        'Database Subnet': 'Microsoft.Network/virtualNetworks/subnets',
        'DB Subnet': 'Microsoft.Network/virtualNetworks/subnets'
    }
    
    def __init__(self):
        """Initialize the cost estimator with Azure pricing data"""
        self.pricing_data = self._load_pricing_data()
        self.region_multipliers = self._load_region_multipliers()
        
    def _load_pricing_data(self) -> Dict[str, Any]:
        """Load Azure pricing data for different resource types"""
        # This would typically come from Azure Pricing API or a database
        # For now, we'll use estimated pricing data (USD per month)
        return {
            'Microsoft.Compute/virtualMachines': {
                'Standard_B1s': {'cores': 1, 'memory': 1, 'monthly_cost': 7.59},
                'Standard_B2s': {'cores': 2, 'memory': 4, 'monthly_cost': 30.37},
                'Standard_D2s_v3': {'cores': 2, 'memory': 8, 'monthly_cost': 70.08},
                'Standard_D4s_v3': {'cores': 4, 'memory': 16, 'monthly_cost': 140.16},
                'Standard_F2s_v2': {'cores': 2, 'memory': 4, 'monthly_cost': 60.74},
                'Standard_F4s_v2': {'cores': 4, 'memory': 8, 'monthly_cost': 121.47}
            },
            'Microsoft.Storage/storageAccounts': {
                'Standard_LRS': {'monthly_cost_per_gb': 0.0184, 'transactions_per_10k': 0.0004},
                'Standard_ZRS': {'monthly_cost_per_gb': 0.023, 'transactions_per_10k': 0.0004},
                'Standard_GRS': {'monthly_cost_per_gb': 0.0368, 'transactions_per_10k': 0.0004},
                'Premium_LRS': {'monthly_cost_per_gb': 0.15, 'transactions_per_10k': 0.0013}
            },
            'Microsoft.Sql/servers/databases': {
                'Basic': {'monthly_cost': 4.99, 'max_size_gb': 2},
                'S0': {'monthly_cost': 15.00, 'max_size_gb': 250},
                'S1': {'monthly_cost': 30.00, 'max_size_gb': 250},
                'S2': {'monthly_cost': 75.00, 'max_size_gb': 250},
                'P1': {'monthly_cost': 465.00, 'max_size_gb': 1000},
                'P2': {'monthly_cost': 930.00, 'max_size_gb': 1000}
            },
            'Microsoft.Web/serverfarms': {
                'Free': {'monthly_cost': 0.00, 'instances': 1},
                'Shared': {'monthly_cost': 9.49, 'instances': 1},
                'Basic_B1': {'monthly_cost': 13.14, 'instances': 3},
                'Basic_B2': {'monthly_cost': 26.28, 'instances': 3},
                'Standard_S1': {'monthly_cost': 70.08, 'instances': 10},
                'Standard_S2': {'monthly_cost': 140.16, 'instances': 10},
                'Premium_P1': {'monthly_cost': 175.20, 'instances': 20},
                'Premium_P2': {'monthly_cost': 350.40, 'instances': 20}
            },
            'Microsoft.Network/applicationGateways': {
                'Standard_Small': {'monthly_cost': 21.90, 'data_processing_per_gb': 0.008},
                'Standard_Medium': {'monthly_cost': 43.80, 'data_processing_per_gb': 0.008},
                'Standard_Large': {'monthly_cost': 87.60, 'data_processing_per_gb': 0.008},
                'WAF_Medium': {'monthly_cost': 175.20, 'data_processing_per_gb': 0.008},
                'WAF_Large': {'monthly_cost': 350.40, 'data_processing_per_gb': 0.008}
            },
            'Microsoft.Network/loadBalancers': {
                'Basic': {'monthly_cost': 0.00, 'data_processing_per_gb': 0.00},
                'Standard': {'monthly_cost': 18.25, 'data_processing_per_gb': 0.005}
            },
            'Microsoft.KeyVault/vaults': {
                'Standard': {'monthly_cost': 0.00, 'operations_per_10k': 0.03},
                'Premium': {'monthly_cost': 0.00, 'operations_per_10k': 0.03, 'hsm_operations_per_10k': 1.00}
            },
            'Microsoft.DocumentDB/databaseAccounts': {
                'Standard': {'monthly_cost_per_ru': 0.008, 'storage_per_gb': 0.25}
            },
            'Microsoft.Cache/Redis': {
                'Basic_C0': {'monthly_cost': 15.18, 'memory_gb': 0.25},
                'Basic_C1': {'monthly_cost': 30.37, 'memory_gb': 1},
                'Standard_C0': {'monthly_cost': 30.37, 'memory_gb': 0.25},
                'Standard_C1': {'monthly_cost': 60.74, 'memory_gb': 1},
                'Premium_P1': {'monthly_cost': 455.10, 'memory_gb': 6}
            },
            'Microsoft.ContainerRegistry/registries': {
                'Basic': {'monthly_cost': 5.00, 'storage_per_gb': 0.10},
                'Standard': {'monthly_cost': 20.00, 'storage_per_gb': 0.10},
                'Premium': {'monthly_cost': 50.00, 'storage_per_gb': 0.10}
            },
            'Microsoft.ContainerService/managedClusters': {
                'Standard': {'monthly_cost': 73.00, 'node_cost_multiplier': 1.0}
            }
        }
    
    def _load_region_multipliers(self) -> Dict[str, float]:
        """Load region-specific cost multipliers"""
        return {
            'eastus': 1.0,
            'eastus2': 1.0,
            'westus': 1.0,
            'westus2': 1.0,
            'centralus': 1.0,
            'northcentralus': 1.0,
            'southcentralus': 1.0,
            'westcentralus': 1.0,
            'canadacentral': 1.05,
            'canadaeast': 1.05,
            'brazilsouth': 1.15,
            'northeurope': 1.08,
            'westeurope': 1.08,
            'uksouth': 1.10,
            'ukwest': 1.10,
            'francecentral': 1.10,
            'germanywestcentral': 1.10,
            'switzerlandnorth': 1.20,
            'norwayeast': 1.15,
            'eastasia': 1.12,
            'southeastasia': 1.12,
            'australiaeast': 1.15,
            'australiasoutheast': 1.15,
            'japaneast': 1.20,
            'japanwest': 1.20,
            'koreacentral': 1.15,
            'koreasouth': 1.15,
            'southindia': 1.05,
            'westindia': 1.05,
            'centralindia': 1.05,
            'uaenorth': 1.18,
            'southafricanorth': 1.15
        }
    
    def estimate_costs(self, architecture_analysis: Dict[str, Any], environment: str = 'development') -> Dict[str, Any]:
        """
        Estimate costs for the entire architecture
        """
        try:
            # Debug: Print the architecture analysis structure
            print(f"🔍 Architecture Analysis Structure:")
            print(f"   - Keys: {list(architecture_analysis.keys())}")
            
            components = architecture_analysis.get('components', [])
            resources = architecture_analysis.get('resources', [])
            
            print(f"   - Components: {len(components)} items")
            print(f"   - Resources: {len(resources)} items")
            
            # Filter out relationships that might be mistaken for resources
            relationship_types = {
                'ingress', 'forwarding', 'internal_load_balancing', 'database_connection',
                'telemetry', 'monitoring', 'data_access', 'api_calls', 'reads_writes_data',
                'reads_static_assets', 'retrieves_secrets', 'sends_telemetry', 'sends_logs',
                'connects_to', 'deployed_in', 'integrated_with', 'accessible_from',
                'routes_traffic_to', 'forwards_traffic_to', 'reverse_proxy', 'storage_access',
                'secrets_access', 'log_aggregation', 'contains', 'hosts'
            }
            
            # Filter components to only include actual Azure resources
            filtered_components = []
            for component in components:
                comp_type = component.get('type', '').lower()
                comp_name = component.get('name', '').lower()
                
                # Skip if this looks like a relationship
                if comp_type in relationship_types or comp_name in relationship_types:
                    print(f"   - Skipping relationship: {component.get('name', 'Unknown')} ({comp_type})")
                    continue
                
                # Only include items that look like Azure resources
                if (comp_type.startswith('microsoft.') or 
                    comp_type in self.RESOURCE_TYPE_MAPPING or
                    any(azure_type in comp_type for azure_type in ['service', 'app', 'database', 'storage', 'network', 'insights', 'analytics', 'vault', 'front'])):
                    filtered_components.append(component)
                else:
                    print(f"   - Skipping non-resource: {component.get('name', 'Unknown')} ({comp_type})")
            
            # Also check for other possible keys that might contain resources
            additional_resources = []
            for key, value in architecture_analysis.items():
                if key not in ['components', 'resources', 'metadata', 'relationships'] and isinstance(value, list):
                    print(f"   - {key}: {len(value)} items (checking for resources)")
                    for item in value:
                        if isinstance(item, dict) and 'type' in item:
                            item_type = item.get('type', '').lower()
                            item_name = item.get('name', '').lower()
                            
                            # Skip relationships
                            if item_type in relationship_types or item_name in relationship_types:
                                continue
                                
                            # Only include actual Azure resources
                            if (item_type.startswith('microsoft.') or 
                                item_type in self.RESOURCE_TYPE_MAPPING or
                                any(azure_type in item_type for azure_type in ['service', 'app', 'database', 'storage', 'network', 'insights', 'analytics', 'vault', 'front'])):
                                additional_resources.append(item)
            
            if additional_resources:
                print(f"   - Found {len(additional_resources)} additional resources in other keys")
            
            # Combine all resources for comprehensive cost analysis
            all_resources = filtered_components + resources + additional_resources
            
            # If we still don't have resources, try to extract from bicep templates or other sources
            if not all_resources:
                print(f"   - No resources found in standard keys, checking for alternative structures...")
                
                # Check if there are any dictionaries that might represent resources
                for key, value in architecture_analysis.items():
                    if isinstance(value, dict):
                        print(f"   - Checking {key} dictionary...")
                        if 'type' in value and value['type'].startswith('Microsoft.'):
                            print(f"     - Found resource: {value.get('name', key)} ({value['type']})")
                            all_resources.append(value)
                        elif isinstance(value, dict):
                            # Check nested dictionaries
                            for nested_key, nested_value in value.items():
                                if isinstance(nested_value, dict) and 'type' in nested_value and nested_value['type'].startswith('Microsoft.'):
                                    print(f"     - Found nested resource: {nested_value.get('name', nested_key)} ({nested_value['type']})")
                                    all_resources.append(nested_value)
            
            cost_estimates = []
            total_monthly_cost = 0
            total_yearly_cost = 0
            
            # Environment-specific cost adjustments
            env_multiplier = self._get_environment_multiplier(environment)
            
            # Region detection
            region = self._detect_region(architecture_analysis)
            region_multiplier = self.region_multipliers.get(region.lower(), 1.0)
            
            print(f"💰 Cost Estimator: Analyzing {len(all_resources)} resources for {environment} environment")
            
            # Debug: Show what resources we're processing
            for i, resource in enumerate(all_resources):
                raw_type = resource.get('type', 'Unknown')
                mapped_type = self.RESOURCE_TYPE_MAPPING.get(raw_type, raw_type)
                print(f"   {i+1}. {resource.get('name', 'Unknown')} - Type: {raw_type} -> {mapped_type}")
            
            for resource in all_resources:
                # Map generic resource types to Azure resource types
                raw_type = resource.get('type', 'Unknown')
                mapped_type = self.RESOURCE_TYPE_MAPPING.get(raw_type, raw_type)
                
                # Create a copy of the resource with the mapped type
                resource_copy = resource.copy()
                resource_copy['type'] = mapped_type
                resource_copy['original_type'] = raw_type
                
                resource_cost = self._estimate_resource_cost(resource_copy, environment)
                if resource_cost['monthly_cost'] > 0:
                    # Apply environment and region multipliers
                    adjusted_monthly = resource_cost['monthly_cost'] * env_multiplier * region_multiplier
                    resource_cost['monthly_cost'] = adjusted_monthly
                    resource_cost['yearly_cost'] = adjusted_monthly * 12
                    resource_cost['environment_multiplier'] = env_multiplier
                    resource_cost['region_multiplier'] = region_multiplier
                    
                    cost_estimates.append(resource_cost)
                    total_monthly_cost += adjusted_monthly
                    total_yearly_cost += adjusted_monthly * 12
                else:
                    # Include zero-cost resources for debugging
                    cost_estimates.append(resource_cost)
            
            # Calculate cost breakdown by category
            cost_breakdown = self._calculate_cost_breakdown(cost_estimates)
            
            # Generate recommendations
            recommendations = self._generate_cost_recommendations(cost_estimates, environment)
            
            print(f"💰 Cost estimation completed: ${total_monthly_cost:.2f}/month")
            
            return {
                'total_monthly_cost': round(total_monthly_cost, 2),
                'total_yearly_cost': round(total_yearly_cost, 2),
                'currency': 'USD',
                'region': region,
                'environment': environment,
                'environment_multiplier': env_multiplier,
                'region_multiplier': region_multiplier,
                'resource_costs': cost_estimates,
                'cost_breakdown': cost_breakdown,
                'recommendations': recommendations,
                'estimation_date': datetime.now().isoformat(),
                'debug_info': {
                    'total_resources_found': len(all_resources),
                    'architecture_keys': list(architecture_analysis.keys()),
                    'resources_with_costs': len([r for r in cost_estimates if r['monthly_cost'] > 0])
                },
                'disclaimer': 'Cost estimates are approximate and based on standard pricing. Actual costs may vary based on usage patterns, discounts, and current Azure pricing.'
            }
            
        except Exception as e:
            print(f"❌ Cost Estimator: Error during cost estimation: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'error': f'Cost estimation failed: {str(e)}',
                'total_monthly_cost': 0,
                'total_yearly_cost': 0,
                'currency': 'USD',
                'resource_costs': [],
                'recommendations': []
            }
    
    def _estimate_resource_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for a single resource"""
        resource_type = resource.get('type', '')
        resource_name = resource.get('name', 'Unknown')
        
        base_cost = {
            'resource_name': resource_name,
            'resource_type': resource_type,
            'monthly_cost': 0,
            'yearly_cost': 0,
            'sku': 'Unknown',
            'cost_factors': [],
            'assumptions': []
        }
        
        try:
            if resource_type == 'Microsoft.Compute/virtualMachines':
                return self._estimate_vm_cost(resource, environment)
            elif resource_type == 'Microsoft.Storage/storageAccounts':
                return self._estimate_storage_cost(resource, environment)
            elif resource_type == 'Microsoft.Sql/servers/databases':
                return self._estimate_sql_cost(resource, environment)
            elif resource_type == 'Microsoft.Web/serverfarms':
                return self._estimate_app_service_cost(resource, environment)
            elif resource_type == 'Microsoft.Web/sites':
                return self._estimate_web_app_cost(resource, environment)
            elif resource_type == 'Microsoft.Network/applicationGateways':
                return self._estimate_app_gateway_cost(resource, environment)
            elif resource_type == 'Microsoft.Network/loadBalancers':
                return self._estimate_load_balancer_cost(resource, environment)
            elif resource_type == 'Microsoft.Network/frontDoors':
                return self._estimate_front_door_cost(resource, environment)
            elif resource_type == 'Microsoft.Network/virtualNetworks':
                return self._estimate_vnet_cost(resource, environment)
            elif resource_type == 'Microsoft.Network/virtualNetworks/subnets':
                return self._estimate_subnet_cost(resource, environment)
            elif resource_type == 'Microsoft.KeyVault/vaults':
                return self._estimate_key_vault_cost(resource, environment)
            elif resource_type == 'Microsoft.DocumentDB/databaseAccounts':
                return self._estimate_cosmos_cost(resource, environment)
            elif resource_type == 'Microsoft.Cache/Redis':
                return self._estimate_redis_cost(resource, environment)
            elif resource_type == 'Microsoft.ContainerRegistry/registries':
                return self._estimate_acr_cost(resource, environment)
            elif resource_type == 'Microsoft.ContainerService/managedClusters':
                return self._estimate_aks_cost(resource, environment)
            elif resource_type == 'Microsoft.Insights/components':
                return self._estimate_app_insights_cost(resource, environment)
            elif resource_type == 'Microsoft.OperationalInsights/workspaces':
                return self._estimate_log_analytics_cost(resource, environment)
            else:
                # Generic estimation for unknown resource types
                base_cost['assumptions'].append('Unknown resource type - no cost estimation available')
                return base_cost
                
        except Exception as e:
            base_cost['error'] = f'Cost estimation failed: {str(e)}'
            return base_cost
    
    def _estimate_vm_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Virtual Machine"""
        properties = resource.get('properties', {})
        hardware_profile = properties.get('hardwareProfile', {})
        
        # Try to get VM size from various possible locations
        vm_size = (
            hardware_profile.get('vmSize') or 
            properties.get('vmSize') or
            resource.get('sku', {}).get('name') or
            self._get_default_vm_size(environment)
        )
        
        pricing = self.pricing_data['Microsoft.Compute/virtualMachines']
        vm_pricing = pricing.get(vm_size, pricing.get('Standard_B1s'))
        
        monthly_cost = vm_pricing['monthly_cost']
        
        # Add OS disk cost
        os_disk_cost = 4.0  # Standard SSD OS disk
        monthly_cost += os_disk_cost
        
        # Add data disk costs if any
        storage_profile = properties.get('storageProfile', {})
        data_disks = storage_profile.get('dataDisks', [])
        for disk in data_disks:
            disk_size = disk.get('diskSizeGB', 128)
            monthly_cost += (disk_size / 128) * 4.0  # Standard SSD pricing
        
        return {
            'resource_name': resource.get('name', 'Unknown VM'),
            'resource_type': 'Microsoft.Compute/virtualMachines',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': vm_size,
            'cost_factors': [
                f'VM Size: {vm_size}',
                f'OS Disk: Standard SSD',
                f'Data Disks: {len(data_disks)} disks'
            ],
            'assumptions': [
                'VM running 24/7',
                'Standard SSD for OS disk',
                'No additional compute services'
            ]
        }
    
    def _estimate_storage_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Storage Account"""
        properties = resource.get('properties', {})
        sku = resource.get('sku', {}).get('name', 'Standard_LRS')
        
        pricing = self.pricing_data['Microsoft.Storage/storageAccounts']
        storage_pricing = pricing.get(sku, pricing.get('Standard_LRS'))
        
        # Estimate storage usage based on environment
        estimated_gb = self._get_estimated_storage_usage(environment)
        
        monthly_cost = estimated_gb * storage_pricing['monthly_cost_per_gb']
        
        # Add estimated transaction costs
        estimated_transactions = 1000000  # 1M transactions per month
        transaction_cost = (estimated_transactions / 10000) * storage_pricing['transactions_per_10k']
        monthly_cost += transaction_cost
        
        return {
            'resource_name': resource.get('name', 'Unknown Storage'),
            'resource_type': 'Microsoft.Storage/storageAccounts',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'Storage Tier: {sku}',
                f'Estimated Storage: {estimated_gb} GB',
                f'Estimated Transactions: {estimated_transactions:,}'
            ],
            'assumptions': [
                f'Estimated {estimated_gb} GB storage usage',
                f'Estimated 1M transactions per month',
                'Standard redundancy level'
            ]
        }
    
    def _estimate_sql_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for SQL Database"""
        properties = resource.get('properties', {})
        sku = resource.get('sku', {}).get('name', self._get_default_sql_sku(environment))
        
        pricing = self.pricing_data['Microsoft.Sql/servers/databases']
        sql_pricing = pricing.get(sku, pricing.get('Basic'))
        
        monthly_cost = sql_pricing['monthly_cost']
        
        return {
            'resource_name': resource.get('name', 'Unknown SQL DB'),
            'resource_type': 'Microsoft.Sql/servers/databases',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'Service Tier: {sku}',
                f'Max Size: {sql_pricing["max_size_gb"]} GB'
            ],
            'assumptions': [
                'Standard compute tier',
                'No additional features (backup, geo-replication)',
                'Moderate usage patterns'
            ]
        }
    
    def _estimate_app_service_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for App Service Plan"""
        properties = resource.get('properties', {})
        sku = resource.get('sku', {}).get('name', self._get_default_app_service_sku(environment))
        
        pricing = self.pricing_data['Microsoft.Web/serverfarms']
        app_service_pricing = pricing.get(sku, pricing.get('Basic_B1'))
        
        monthly_cost = app_service_pricing['monthly_cost']
        
        return {
            'resource_name': resource.get('name', 'Unknown App Service'),
            'resource_type': 'Microsoft.Web/serverfarms',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'Service Plan: {sku}',
                f'Max Instances: {app_service_pricing["instances"]}'
            ],
            'assumptions': [
                'Single instance running',
                'Standard compute hours',
                'No additional app services'
            ]
        }
    
    def _estimate_web_app_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Web App (App Service)"""
        properties = resource.get('properties', {})
        
        # Try to get App Service Plan details
        app_service_plan = properties.get('serverFarmId', '')
        
        # Default SKU based on environment
        sku = self._get_default_app_service_sku(environment)
        
        # Get pricing for the SKU
        pricing = self.pricing_data.get('Microsoft.Web/serverfarms', {})
        plan_pricing = pricing.get(sku, pricing.get('Basic_B1', {'monthly_cost': 13.0}))
        
        monthly_cost = plan_pricing['monthly_cost']
        
        return {
            'resource_name': resource.get('name', 'Unknown Web App'),
            'resource_type': 'Microsoft.Web/sites',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'App Service Plan: {sku}',
                f'Always On: Enabled',
                f'Scaling: Manual/Auto'
            ],
            'assumptions': [
                f'Uses shared App Service Plan pricing',
                'Standard configuration',
                'No additional features (custom domains, SSL certificates)'
            ]
        }
    
    def _estimate_app_gateway_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Application Gateway"""
        properties = resource.get('properties', {})
        sku = resource.get('sku', {}).get('name', 'Standard_Small')
        
        pricing = self.pricing_data['Microsoft.Network/applicationGateways']
        gateway_pricing = pricing.get(sku, pricing.get('Standard_Small'))
        
        monthly_cost = gateway_pricing['monthly_cost']
        
        # Add data processing cost (estimated)
        estimated_data_gb = 100  # 100 GB per month
        data_processing_cost = estimated_data_gb * gateway_pricing['data_processing_per_gb']
        monthly_cost += data_processing_cost
        
        return {
            'resource_name': resource.get('name', 'Unknown App Gateway'),
            'resource_type': 'Microsoft.Network/applicationGateways',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'Gateway Size: {sku}',
                f'Data Processing: {estimated_data_gb} GB'
            ],
            'assumptions': [
                f'Estimated {estimated_data_gb} GB data processing per month',
                'Standard configuration',
                'No additional features'
            ]
        }
    
    def _estimate_load_balancer_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Load Balancer"""
        properties = resource.get('properties', {})
        sku = resource.get('sku', {}).get('name', 'Standard')
        
        pricing = self.pricing_data['Microsoft.Network/loadBalancers']
        lb_pricing = pricing.get(sku, pricing.get('Standard'))
        
        monthly_cost = lb_pricing['monthly_cost']
        
        # Add data processing cost for Standard LB
        if sku == 'Standard':
            estimated_data_gb = 50  # 50 GB per month
            data_processing_cost = estimated_data_gb * lb_pricing['data_processing_per_gb']
            monthly_cost += data_processing_cost
        
        return {
            'resource_name': resource.get('name', 'Unknown Load Balancer'),
            'resource_type': 'Microsoft.Network/loadBalancers',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'Load Balancer Tier: {sku}',
                f'Data Processing: {estimated_data_gb if sku == "Standard" else 0} GB'
            ],
            'assumptions': [
                'Standard load balancing rules',
                f'Estimated {50 if sku == "Standard" else 0} GB data processing per month'
            ]
        }
    
    def _estimate_front_door_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Azure Front Door"""
        properties = resource.get('properties', {})
        
        # Default SKU based on environment
        sku = 'Standard' if environment == 'development' else 'Premium'
        
        # Base cost for Front Door
        base_cost = 22.0 if sku == 'Standard' else 330.0
        
        # Estimated routing rules and data transfer
        estimated_rules = 5
        estimated_data_transfer = 100  # GB per month
        
        monthly_cost = base_cost + (estimated_rules * 1.0) + (estimated_data_transfer * 0.085)
        
        return {
            'resource_name': resource.get('name', 'Unknown Front Door'),
            'resource_type': 'Microsoft.Network/frontDoors',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': sku,
            'cost_factors': [
                f'Front Door Tier: {sku}',
                f'Routing Rules: {estimated_rules}',
                f'Data Transfer: {estimated_data_transfer} GB'
            ],
            'assumptions': [
                f'Estimated {estimated_rules} routing rules',
                f'Estimated {estimated_data_transfer} GB data transfer per month',
                'Standard configuration without WAF'
            ]
        }
    
    def _estimate_vnet_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Virtual Network"""
        # Virtual Networks are generally free, but may have associated costs
        return {
            'resource_name': resource.get('name', 'Unknown VNet'),
            'resource_type': 'Microsoft.Network/virtualNetworks',
            'monthly_cost': 0.0,
            'yearly_cost': 0.0,
            'sku': 'Standard',
            'cost_factors': [
                'Virtual Network: Free',
                'Subnets: Free',
                'VNet Peering: Additional cost if configured'
            ],
            'assumptions': [
                'Virtual Network itself is free',
                'Costs may apply for VNet peering, gateways, and data transfer',
                'Standard configuration'
            ]
        }
    
    def _estimate_subnet_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Subnet"""
        # Subnets are free
        return {
            'resource_name': resource.get('name', 'Unknown Subnet'),
            'resource_type': 'Microsoft.Network/virtualNetworks/subnets',
            'monthly_cost': 0.0,
            'yearly_cost': 0.0,
            'sku': 'Standard',
            'cost_factors': [
                'Subnet: Free',
                'IP addresses: Free within VNet'
            ],
            'assumptions': [
                'Subnets are free',
                'No additional costs for IP addresses within VNet',
                'Standard configuration'
            ]
        }
    
    def _estimate_app_insights_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Application Insights"""
        # Estimated data ingestion based on environment
        data_ingestion_gb = {
            'development': 1,
            'staging': 5,
            'production': 20
        }.get(environment, 5)
        
        # Pricing: First 5 GB free, then $2.30 per GB
        monthly_cost = max(0, (data_ingestion_gb - 5) * 2.30)
        
        return {
            'resource_name': resource.get('name', 'Unknown App Insights'),
            'resource_type': 'Microsoft.Insights/components',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': 'Pay-as-you-go',
            'cost_factors': [
                f'Data Ingestion: {data_ingestion_gb} GB',
                f'Data Retention: 90 days (free)',
                f'Pricing: First 5 GB free, then $2.30/GB'
            ],
            'assumptions': [
                f'Estimated {data_ingestion_gb} GB data ingestion per month',
                '90 days data retention (free tier)',
                'Standard telemetry collection'
            ]
        }
    
    def _estimate_log_analytics_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate cost for Log Analytics Workspace"""
        # Estimated data ingestion based on environment
        data_ingestion_gb = {
            'development': 2,
            'staging': 10,
            'production': 50
        }.get(environment, 10)
        
        # Pricing: First 5 GB free, then $2.30 per GB
        monthly_cost = max(0, (data_ingestion_gb - 5) * 2.30)
        
        return {
            'resource_name': resource.get('name', 'Unknown Log Analytics'),
            'resource_type': 'Microsoft.OperationalInsights/workspaces',
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': 'Per-GB',
            'cost_factors': [
                f'Data Ingestion: {data_ingestion_gb} GB',
                f'Data Retention: 31 days (free)',
                f'Pricing: First 5 GB free, then $2.30/GB'
            ],
            'assumptions': [
                f'Estimated {data_ingestion_gb} GB data ingestion per month',
                '31 days data retention (free tier)',
                'Standard log collection from connected resources'
            ]
        }

    def _get_environment_multiplier(self, environment: str) -> float:
        """Get cost multiplier based on environment"""
        environment_multipliers = {
            'development': 0.5,   # Dev environments typically smaller
            'staging': 0.7,       # Staging environments medium sized
            'production': 1.0,    # Production full scale
            'test': 0.3,         # Test environments minimal
            'demo': 0.4,         # Demo environments small
            'unknown': 1.0       # Default to production pricing
        }
        return environment_multipliers.get(environment.lower(), 1.0)
    
    def _detect_region(self, architecture_analysis: Dict[str, Any]) -> str:
        """Detect Azure region from architecture analysis"""
        # Check for region in metadata
        metadata = architecture_analysis.get('metadata', {})
        if 'region' in metadata:
            return metadata['region']
        
        # Check for common region indicators
        region_indicators = [
            'eastus', 'westus', 'centralus', 'northcentralus', 'southcentralus',
            'eastus2', 'westus2', 'westus3', 'northeurope', 'westeurope',
            'southeastasia', 'eastasia', 'australiaeast', 'australiasoutheast',
            'brazilsouth', 'canadacentral', 'canadaeast', 'japaneast', 'japanwest',
            'koreacentral', 'koreasouth', 'uksouth', 'ukwest', 'francecentral',
            'francesouth', 'germanywestcentral', 'norwayeast', 'switzerlandnorth',
            'uaenorth', 'southafricanorth', 'centralindia', 'southindia', 'westindia'
        ]
        
        # Search through all text fields for region indicators
        for key, value in architecture_analysis.items():
            if isinstance(value, str):
                for region in region_indicators:
                    if region in value.lower():
                        return region
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for nested_key, nested_value in item.items():
                            if isinstance(nested_value, str):
                                for region in region_indicators:
                                    if region in nested_value.lower():
                                        return region
        
        # Default to East US
        return 'eastus'
    
    def _calculate_cost_breakdown(self, cost_estimates: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate cost breakdown by resource category"""
        breakdown = {
            'Compute': 0,
            'Storage': 0,
            'Networking': 0,
            'Database': 0,
            'Monitoring': 0,
            'Security': 0,
            'Other': 0
        }
        
        for resource in cost_estimates:
            resource_type = resource.get('resource_type', '').lower()
            monthly_cost = resource.get('monthly_cost', 0)
            
            if 'compute' in resource_type or 'virtualmachine' in resource_type or 'sites' in resource_type or 'serverfarms' in resource_type:
                breakdown['Compute'] += monthly_cost
            elif 'storage' in resource_type or 'blob' in resource_type:
                breakdown['Storage'] += monthly_cost
            elif 'network' in resource_type or 'loadbalancer' in resource_type or 'frontdoor' in resource_type or 'applicationgateway' in resource_type or 'virtualnetwork' in resource_type:
                breakdown['Networking'] += monthly_cost
            elif 'sql' in resource_type or 'database' in resource_type or 'cosmos' in resource_type:
                breakdown['Database'] += monthly_cost
            elif 'insights' in resource_type or 'monitor' in resource_type or 'analytics' in resource_type or 'operationalinsights' in resource_type:
                breakdown['Monitoring'] += monthly_cost
            elif 'vault' in resource_type or 'security' in resource_type or 'keyvault' in resource_type:
                breakdown['Security'] += monthly_cost
            else:
                breakdown['Other'] += monthly_cost
        
        return breakdown
    
    def _generate_cost_recommendations(self, cost_estimates: List[Dict[str, Any]], environment: str) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        total_cost = sum(r.get('monthly_cost', 0) for r in cost_estimates)
        
        if total_cost > 1000:
            recommendations.append("Consider using Azure Reserved Instances for production workloads to save up to 72%")
        
        if environment == 'development':
            recommendations.append("Use Azure Dev/Test pricing for development environments")
            recommendations.append("Consider using B-series VMs for development workloads")
        
        # Check for expensive resources
        expensive_resources = [r for r in cost_estimates if r.get('monthly_cost', 0) > 500]
        if expensive_resources:
            recommendations.append("Review high-cost resources and consider right-sizing or alternative SKUs")
        
        # Check for storage optimization
        storage_resources = [r for r in cost_estimates if 'storage' in r.get('type', '').lower()]
        if storage_resources:
            recommendations.append("Consider using appropriate storage tiers (Cool, Archive) for infrequently accessed data")
        
        # Check for networking optimization
        networking_resources = [r for r in cost_estimates if 'network' in r.get('type', '').lower()]
        if len(networking_resources) > 3:
            recommendations.append("Consolidate network resources where possible to reduce costs")
        
        return recommendations

    def generate_cost_report(self, cost_estimation: Dict[str, Any]) -> str:
        """Generate a formatted cost estimation report"""
        
        report = []
        report.append("# Azure Cost Estimation Report")
        report.append("")
        
        # Summary
        total_cost = cost_estimation.get('total_monthly_cost', 0)
        report.append(f"## Summary")
        report.append(f"**Total Monthly Cost**: ${total_cost:.2f}")
        report.append(f"**Total Annual Cost**: ${total_cost * 12:.2f}")
        report.append(f"**Environment**: {cost_estimation.get('environment', 'development')}")
        report.append(f"**Region**: {cost_estimation.get('region', 'East US')}")
        report.append(f"**Generated**: {cost_estimation.get('generated_date', 'N/A')}")
        report.append("")
        
        # Resource breakdown
        resources = cost_estimation.get('resource_costs', [])
        if resources:
            report.append("## Resource Cost Breakdown")
            report.append("")
            
            for resource in resources:
                name = resource.get('resource_name', 'Unknown')
                resource_type = resource.get('resource_type', 'Unknown')
                monthly_cost = resource.get('monthly_cost', 0)
                
                report.append(f"### {name}")
                report.append(f"- **Type**: {resource_type}")
                report.append(f"- **Monthly Cost**: ${monthly_cost:.2f}")
                report.append(f"- **Annual Cost**: ${monthly_cost * 12:.2f}")
                
                # Add cost factors if available
                cost_factors = resource.get('cost_factors', [])
                if cost_factors:
                    report.append("- **Cost Factors**:")
                    for factor in cost_factors:
                        report.append(f"  - {factor}")
                
                # Add assumptions if available
                assumptions = resource.get('assumptions', [])
                if assumptions:
                    report.append("- **Assumptions**:")
                    for assumption in assumptions:
                        report.append(f"  - {assumption}")
                
                # Add pricing tier if available
                sku = resource.get('sku', '')
                if sku:
                    report.append(f"- **SKU/Pricing Tier**: {sku}")
                
                # Add error if present
                error = resource.get('error', '')
                if error:
                    report.append(f"- **Error**: {error}")
                
                report.append("")
        
        # Cost by category
        cost_breakdown = cost_estimation.get('cost_breakdown', {})
        if cost_breakdown:
            report.append("## Cost by Category")
            report.append("")
            
            for category, cost in cost_breakdown.items():
                if cost > 0:  # Only show categories with actual costs
                    report.append(f"- **{category}**: ${cost:.2f}/month")
            report.append("")
        
        # Recommendations
        recommendations = cost_estimation.get('recommendations', [])
        if recommendations:
            report.append("## Cost Optimization Recommendations")
            report.append("")
            
            for i, recommendation in enumerate(recommendations, 1):
                report.append(f"{i}. {recommendation}")
            report.append("")
        
        # Disclaimers
        report.append("## Disclaimers")
        report.append("")
        report.append("- Cost estimates are based on current Azure pricing and may change")
        report.append("- Actual costs may vary based on usage patterns and configurations")
        report.append("- Estimates assume standard configurations and may not reflect all pricing tiers")
        report.append("- Regional pricing variations are applied where available")
        report.append("- This is an estimate only and should not be used for budgeting purposes")
        
        return "\n".join(report)
    
    def _get_default_app_service_sku(self, environment: str) -> str:
        """Get default App Service SKU based on environment"""
        if environment == 'development':
            return 'F1'  # Free tier
        elif environment == 'staging':
            return 'S1'  # Standard small
        else:  # production
            return 'P1V2'  # Premium V2
    
    def _get_default_sql_sku(self, environment: str) -> str:
        """Get default SQL Database SKU based on environment"""
        if environment == 'development':
            return 'Basic'
        elif environment == 'staging':
            return 'S1'  # Standard S1
        else:  # production
            return 'S2'  # Standard S2
    
    def _get_estimated_storage_usage(self, environment: str) -> int:
        """Get estimated storage usage in GB based on environment"""
        if environment == 'development':
            return 10  # 10 GB
        elif environment == 'staging':
            return 50  # 50 GB
        else:  # production
            return 100  # 100 GB
    
    def _estimate_key_vault_cost(self, resource: Dict[str, Any], environment: str) -> Dict[str, Any]:
        """Estimate Key Vault costs"""
        base_cost = 0.03  # $0.03 per 10,000 operations
        
        # Estimate operations based on environment
        if environment == 'development':
            operations = 10000  # 10K operations
        elif environment == 'staging':
            operations = 50000  # 50K operations
        else:  # production
            operations = 100000  # 100K operations
        
        monthly_cost = (operations / 10000) * base_cost
        
        return {
            'resource_name': resource.get('name', 'Key Vault'),
            'resource_type': resource.get('type', 'Microsoft.KeyVault/vaults'),
            'monthly_cost': monthly_cost,
            'yearly_cost': monthly_cost * 12,
            'sku': 'Standard',
            'cost_factors': [
                f'Operations: {operations:,}',
                f'Rate: $0.03 per 10K operations',
                'Certificate operations: Additional cost'
            ],
            'assumptions': [
                f'Estimated {operations:,} operations per month',
                'Standard tier pricing',
                'No premium features or HSM'
            ]
        }
