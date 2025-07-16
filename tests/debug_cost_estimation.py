"""
Debug script to examine the architecture analysis data structure for cost estimation
"""

import sys
import os
import json
import zipfile
from datetime import datetime

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cost_estimator import AzureCostEstimator

def debug_cost_estimation():
    """Debug the cost estimation with a real architecture analysis"""
    
    # Get the latest production ZIP file
    output_dir = "output"
    zip_files = [f for f in os.listdir(output_dir) if f.startswith("digital_superman_production_") and f.endswith(".zip")]
    
    if not zip_files:
        print("❌ No production ZIP files found")
        return
    
    # Get the most recent ZIP file
    latest_zip = max(zip_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
    zip_path = os.path.join(output_dir, latest_zip)
    
    print(f"🔍 Examining ZIP file: {latest_zip}")
    
    # Extract cost estimation data
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            print(f"📁 ZIP contains {len(file_list)} files:")
            for file_name in file_list:
                print(f"   - {file_name}")
            
            # Look for cost estimation JSON
            if 'cost_estimation.json' in file_list:
                print("\n📊 Found cost estimation JSON. Reading...")
                cost_data = json.loads(zip_ref.read('cost_estimation.json').decode('utf-8'))
                
                print(f"Total Monthly Cost: ${cost_data.get('total_monthly_cost', 0):.2f}")
                print(f"Total Yearly Cost: ${cost_data.get('total_yearly_cost', 0):.2f}")
                print(f"Environment: {cost_data.get('environment', 'Unknown')}")
                print(f"Region: {cost_data.get('region', 'Unknown')}")
                
                # Examine resource costs
                resource_costs = cost_data.get('resource_costs', [])
                print(f"\n📋 Resource Costs ({len(resource_costs)} resources):")
                
                for i, resource in enumerate(resource_costs):
                    print(f"   {i+1}. {resource['resource_name']} ({resource['resource_type']})")
                    print(f"      SKU: {resource['sku']}")
                    print(f"      Monthly Cost: ${resource['monthly_cost']:.2f}")
                    print(f"      Cost Factors: {resource.get('cost_factors', [])}")
                    print(f"      Assumptions: {resource.get('assumptions', [])}")
                    if 'error' in resource:
                        print(f"      ⚠️ Error: {resource['error']}")
                    print()
                
                # Create a sample architecture structure to test
                print("\n🧪 Testing with sample architecture structure...")
                
                # Create a mock architecture analysis that should have costs
                sample_architecture = {
                    "components": [
                        {
                            "name": "web-vm",
                            "type": "Microsoft.Compute/virtualMachines",
                            "properties": {
                                "hardwareProfile": {
                                    "vmSize": "Standard_D2s_v3"
                                }
                            }
                        },
                        {
                            "name": "storage-account",
                            "type": "Microsoft.Storage/storageAccounts",
                            "sku": {
                                "name": "Standard_LRS"
                            }
                        },
                        {
                            "name": "sql-database",
                            "type": "Microsoft.Sql/servers/databases",
                            "sku": {
                                "name": "S1"
                            }
                        }
                    ],
                    "resources": [
                        {
                            "name": "app-service-plan",
                            "type": "Microsoft.Web/serverfarms",
                            "sku": {
                                "name": "Standard_S1"
                            }
                        }
                    ],
                    "metadata": {
                        "region": "eastus"
                    }
                }
                
                # Test the cost estimator directly
                estimator = AzureCostEstimator()
                test_cost_estimation = estimator.estimate_costs(sample_architecture, 'production')
                
                print(f"Test estimation - Total Monthly Cost: ${test_cost_estimation['total_monthly_cost']:.2f}")
                print(f"Test estimation - Resource Count: {len(test_cost_estimation['resource_costs'])}")
                
                # Compare with actual data
                if test_cost_estimation['total_monthly_cost'] > 0:
                    print("\n✅ Cost estimator is working correctly with sample data")
                    print("❌ The issue is likely in the architecture analysis data structure")
                    print("\n💡 The architecture analysis might not be providing resources in the expected format")
                    
                    # Show the structure difference
                    print("\n🔍 Expected structure:")
                    print("   - components[] or resources[] arrays")
                    print("   - Each resource should have 'name', 'type', and optionally 'sku'")
                    print("   - Type should match Azure resource types like 'Microsoft.Compute/virtualMachines'")
                    
                else:
                    print("\n❌ Cost estimator is not working even with sample data")
                    print("🔧 Need to debug the cost estimation logic")
                    
            else:
                print("❌ No cost estimation JSON found in ZIP file")
                
    except Exception as e:
        print(f"❌ Error examining ZIP file: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cost_estimation()
