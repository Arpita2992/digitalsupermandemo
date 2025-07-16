"""
ZIP generator utility to create downloadable packages - BACKUP
"""

import os
import zipfile
import json
import tempfile
from typing import Dict, Any
from datetime import datetime
from .cost_estimator import AzureCostEstimator

class ZipGenerator:
    def __init__(self):
        self.output_dir = 'output'
        os.makedirs(self.output_dir, exist_ok=True)
        self.cost_estimator = AzureCostEstimator()
    
    def create_zip_package(self, 
                          bicep_templates: Dict[str, Any], 
                          architecture_analysis: Dict[str, Any],
                          policy_compliance: Dict[str, Any],
                          cost_optimization: Dict[str, Any] = None,
                          environment: str = 'development') -> str:
        """Create a ZIP package with all generated content including cost optimization"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"digital_superman_{environment}_{timestamp}.zip"
        zip_filepath = os.path.join(self.output_dir, zip_filename)
        
        try:
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add Bicep templates
                self._add_bicep_templates(zipf, bicep_templates, environment)
                
                # Add YAML pipelines
                self._add_yaml_pipelines(zipf, bicep_templates, environment)
                
                # Add scripts
                self._add_scripts(zipf, bicep_templates, environment)
                
                # Add simplified documentation (moved to reports folder)
                self._add_simplified_documentation(zipf, policy_compliance, environment)
                
                # Add cost estimation report
                self._add_cost_estimation(zipf, architecture_analysis, environment)
                
                # Add cost optimization report if available
                if cost_optimization:
                    self._add_cost_optimization_report(zipf, cost_optimization, environment)
            
            return zip_filename
            
        except Exception as e:
            raise Exception(f"Failed to create ZIP package: {str(e)}")
    
    def _add_simplified_documentation(self, zipf: zipfile.ZipFile, compliance: Dict[str, Any], environment: str):
        """Add only essential documentation - Policy Compliance Report and README"""
        
        # 1. Enhanced Policy Compliance Report with custom policies table
        compliance_report = self._generate_enhanced_policy_compliance_report(compliance, environment)
        zipf.writestr("reports/POLICY_COMPLIANCE_REPORT.md", compliance_report)
        
        # 2. Auto-fix summary if fixes were applied
        if compliance.get('fixes_applied'):
            autofix_report = self._generate_autofix_summary(compliance.get('fixes_applied', []))
            zipf.writestr("reports/AUTOFIX_SUMMARY.md", autofix_report)
        
        # 3. Simple README with usage instructions
        readme = self._generate_simple_readme()
        zipf.writestr("README.md", readme)  # Keep README in root
        
    def _add_cost_estimation(self, zipf: zipfile.ZipFile, architecture_analysis: Dict[str, Any], environment: str):
        """Add cost estimation report to ZIP"""
        try:
            print(f"💰 Generating cost estimation for {environment} environment...")
            
            # Generate cost estimation
            cost_estimation = self.cost_estimator.estimate_costs(architecture_analysis, environment)
            
            # Generate cost report
            cost_report = self.cost_estimator.generate_cost_report(cost_estimation)
            zipf.writestr("reports/COST_ESTIMATION_REPORT.md", cost_report)
            
            # Also add cost estimation as JSON for programmatic access
            cost_json = json.dumps(cost_estimation, indent=2)
            zipf.writestr("reports/cost_estimation.json", cost_json)
            
        except Exception as e:
            print(f"❌ Error generating cost estimation: {str(e)}")
            # Add error report
            error_report = f"""# Cost Estimation Error

An error occurred while generating the cost estimation:

**Error**: {str(e)}

**Recommendation**: Please review the architecture analysis and try again.

**Note**: Cost estimation is an optional feature and does not affect the core functionality.
"""
            zipf.writestr("reports/COST_ESTIMATION_ERROR.md", error_report)
    
    def _add_cost_optimization_report(self, zipf: zipfile.ZipFile, cost_optimization: Dict[str, Any], environment: str):
        """Add cost optimization report to ZIP"""
        try:
            # Import here to avoid circular imports
            from agents.cost_optimization_agent import CostOptimizationAgent
            
            # Create cost optimization agent instance
            cost_optimizer = CostOptimizationAgent()
            
            # Generate cost optimization report
            report_content = cost_optimizer.generate_cost_optimization_report(cost_optimization)
            
            # Add to ZIP
            zipf.writestr(f'reports/cost_optimization_report_{environment}.md', report_content)
            
            # Also add raw optimization data as JSON
            optimization_data = {
                'optimization_summary': cost_optimization.get('optimization_summary', {}),
                'optimization_recommendations': cost_optimization.get('optimization_recommendations', []),
                'cost_savings': cost_optimization.get('cost_savings', []),
                'ai_insights': cost_optimization.get('ai_insights', {}),
                'framework_applied': cost_optimization.get('framework_applied', 'Microsoft Well-Architected Framework'),
                'bicep_generation_hints': cost_optimization.get('bicep_generation_hints', {})
            }
            
            zipf.writestr(f'reports/cost_optimization_data_{environment}.json', 
                         json.dumps(optimization_data, indent=2))
            
        except Exception as e:
            print(f"⚠️ Warning: Could not add cost optimization report: {str(e)}")
            # Add fallback report
            fallback_report = f"""# Cost Optimization Report - {environment.title()}

## Error
Could not generate detailed cost optimization report: {str(e)}

## Basic Information
- Environment: {environment}
- Framework: Microsoft Well-Architected Framework - Cost Optimization
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please refer to the architecture analysis and policy compliance reports for additional context.
"""
            zipf.writestr(f'reports/cost_optimization_report_{environment}.md', fallback_report)
