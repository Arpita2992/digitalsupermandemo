"""
ZIP generator utility to create downloadable packages
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
                
                # Add simplified documentation (only 2 files)
                self._add_simplified_documentation(zipf, policy_compliance, environment)
                
                # Add cost estimation report
                self._add_cost_estimation(zipf, architecture_analysis, environment)
                
                # Add cost optimization report if available
                if cost_optimization:
                    self._add_cost_optimization_report(zipf, cost_optimization, environment)
            
            return zip_filename
            
        except Exception as e:
            raise Exception(f"Failed to create ZIP package: {str(e)}")
    
    def _add_bicep_templates(self, zipf: zipfile.ZipFile, templates: Dict[str, Any], environment: str):
        """Add Bicep templates to ZIP"""
        bicep_templates = templates.get('bicep_templates', {})
        
        for template_name, template_content in bicep_templates.items():
            if template_name.endswith('/'):
                # Handle directory structure
                continue
            
            if isinstance(template_content, dict):
                # Handle nested structure like modules/
                for sub_name, sub_content in template_content.items():
                    if isinstance(sub_content, str):
                        zipf.writestr(f"bicep/{template_name}/{sub_name}", sub_content)
            else:
                zipf.writestr(f"bicep/{template_name}", template_content)
        
        # Handle modules directory
        modules = bicep_templates.get('modules/', {})
        for module_name, module_content in modules.items():
            zipf.writestr(f"bicep/modules/{module_name}", module_content)
        
        # Handle parameters directory - only include environment-specific parameters
        parameters = bicep_templates.get('parameters/', {})
        for param_name, param_content in parameters.items():
            # Only include parameters for the target environment
            if environment in param_name or not any(env in param_name for env in ['dev', 'staging', 'prod']):
                zipf.writestr(f"bicep/parameters/{param_name}", param_content)
    
    def _add_yaml_pipelines(self, zipf: zipfile.ZipFile, templates: Dict[str, Any], environment: str):
        """Add environment-specific YAML pipelines to ZIP"""
        yaml_pipelines = templates.get('yaml_pipelines', {})
        
        for pipeline_name, pipeline_content in yaml_pipelines.items():
            # Only include pipelines that match the target environment or are generic
            if environment in pipeline_name or 'azure-pipelines.' in pipeline_name:
                if isinstance(pipeline_content, dict):
                    # Handle nested structure like pipelines/
                    for sub_name, sub_content in pipeline_content.items():
                        if isinstance(sub_content, str) and (environment in sub_name or 'main' in sub_name):
                            zipf.writestr(f"pipelines/{sub_name}", sub_content)
                else:
                    zipf.writestr(f"pipelines/{pipeline_name}", pipeline_content)
    
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
        zipf.writestr("reports/README.md", readme)
    
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
            zipf.writestr("cost_estimation.json", cost_json)
            
            print(f"💰 Cost estimation completed: €{cost_estimation.get('total_monthly_cost', 0):.2f}/month")
            
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

    def _generate_enhanced_policy_compliance_report(self, compliance: Dict[str, Any], environment: str) -> str:
        """Generate enhanced policy compliance report with custom policies table at the top"""
        
        # Generate custom policies table first
        custom_policies_table = self._generate_custom_policies_table_for_zip(compliance)
        
        overall = compliance.get('overall_compliance', {})
        violations = compliance.get('violations', [])
        recommendations = compliance.get('recommendations', [])
        fixes_applied = compliance.get('fixes_applied', [])
        post_fix_compliance = compliance.get('post_fix_compliance', {})
        
        # Use post-fix compliance if available
        if post_fix_compliance:
            overall = post_fix_compliance.get('overall_compliance', overall)
            remaining_violations = post_fix_compliance.get('violations', [])
        else:
            remaining_violations = violations
        
        report = f"""# Azure Architecture Compliance Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Environment:** {environment.title()}  
**Compliance Status:** {'✅ COMPLIANT' if overall.get('compliant', False) else '❌ NON-COMPLIANT'}  
**Compliance Score:** {overall.get('compliance_score', 'Unknown')}
**Auto-Fixes Applied:** {len(fixes_applied)} {'🔧' if fixes_applied else ''}

{custom_policies_table}

---

## 📊 Compliance Summary

| Metric | Original | After Auto-Fix | Status |
|--------|----------|----------------|--------|
| 🔴 Critical Violations | {len([v for v in violations if v.get('severity') == 'critical'])} | {len([v for v in remaining_violations if v.get('severity') == 'critical'])} | {'✅ Improved' if len(fixes_applied) > 0 else '❌ Action Required' if len(remaining_violations) > 0 else '✅ Clean'} |
| 🟡 Warnings | {len([v for v in violations if v.get('severity') in ['medium', 'warning']])} | {len([v for v in remaining_violations if v.get('severity') in ['medium', 'warning']])} | {'✅ Improved' if len(fixes_applied) > 0 else '⚠️ Review Needed' if len(remaining_violations) > 0 else '✅ Clean'} |
| 💡 Recommendations | {len(recommendations)} | {len(recommendations)} | {'📝 Available' if len(recommendations) > 0 else '✅ None'} |
| 📋 Total Issues | {len(violations)} | {len(remaining_violations)} | {'🔧 Auto-Fixed' if len(fixes_applied) > 0 else '🔍 Review Required' if len(remaining_violations) > 0 else '✅ All Clear'} |

---

"""

        # Auto-fix summary section
        if fixes_applied:
            report += f"""## 🔧 Auto-Fix Summary

**{len(fixes_applied)} violations were automatically resolved:**

| Component | Fix Applied | Status |
|-----------|-------------|--------|
"""
            for fix in fixes_applied:
                component = fix.get('component', 'Unknown')
                fix_desc = fix.get('fix_applied', 'Security enhancement applied')
                report += f"| {component} | {fix_desc} | ✅ Fixed |\n"
            
            report += "\n💡 *See AUTOFIX_SUMMARY.md for detailed fix information*\n\n---\n\n"

        if remaining_violations:
            report += """## 🚨 Remaining Policy Violations

| Severity | Component | Category | Issue | Recommendation |
|----------|-----------|----------|-------|----------------|
"""
            for violation in remaining_violations:
                severity_icon = {
                    'critical': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢',
                    'info': 'ℹ️'
                }.get(violation.get('severity', 'unknown').lower(), '❓')
                
                component = violation.get('component', 'Unknown')[:30]
                category = violation.get('category', 'Unknown')[:20]
                description = violation.get('description', 'No description')[:50] + ('...' if len(violation.get('description', '')) > 50 else '')
                recommendation = violation.get('recommendation', 'No recommendation')[:60] + ('...' if len(violation.get('recommendation', '')) > 60 else '')
                
                report += f"| {severity_icon} {violation.get('severity', 'Unknown').title()} | {component} | {category} | {description} | {recommendation} |\n"
            
            report += "\n"
        else:
            report += "## ✅ No Policy Violations Found\n\nAll Azure policies are compliant! 🎉\n\n"

        # Add recommendations section if available
        if recommendations:
            report += """---

## 💡 Recommendations for Improvement

| Priority | Component | Category | Recommendation | Benefits |
|----------|-----------|----------|----------------|----------|
"""
            for rec in recommendations:
                priority_icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec.get('priority', 'medium').lower(), '🟡')
                
                component = rec.get('component', 'Unknown')[:25]
                category = rec.get('category', 'Unknown')[:15]
                description = rec.get('description', 'No description')[:60] + ('...' if len(rec.get('description', '')) > 60 else '')
                benefits = rec.get('benefits', 'Improved compliance')[:50] + ('...' if len(rec.get('benefits', '')) > 50 else '')
                
                report += f"| {priority_icon} {rec.get('priority', 'Medium').title()} | {component} | {category} | {description} | {benefits} |\n"
        
        report += f"""
---

## 📋 Next Steps

### Immediate Actions Required:
{self._generate_immediate_actions(remaining_violations)}

### Deployment Notes:
- Review the Bicep templates in the `bicep/` folder
- Check parameter files for environment-specific values
- Run `az deployment group validate` before actual deployment
- Monitor compliance post-deployment

### Support:
- Check the `README.md` for deployment instructions
- View `AUTOFIX_SUMMARY.md` for applied fixes
- Contact your Azure administrator for policy exemptions if needed

---
*Report generated by Digital Superman Azure Architecture Analyzer*
"""
        
        return report
    
    def _generate_custom_policies_table_for_zip(self, compliance: Dict[str, Any]) -> str:
        """Generate custom policies table for ZIP report"""
        
        # Check if we have custom policy validation results
        custom_validation = compliance.get('custom_policy_validation', {})
        policy_checks = custom_validation.get('policy_checks', [])
        
        if not policy_checks:
            return """
---

## 🏢 Organization-Specific Azure Policies

*No custom Azure policies were evaluated for this architecture.*

To add organization-specific policies:
1. Place Azure Policy JSON files in the `policies/` folder
2. Policies will be automatically loaded and evaluated
3. Re-run the analysis to see results

---"""
        
        # Generate table with policy check results
        table = """
---

## 🏢 Organization-Specific Azure Policies Evaluated

The following custom Azure policies were evaluated against the architecture:

| Policy Name | Category | Effect | Severity | Status | Affected Resources |
|-------------|----------|--------|----------|--------|--------------------|"""
        
        for check in policy_checks:
            policy_name = check.get('policy_name', 'Unknown')
            category = check.get('category', 'Unknown').title()
            effect = check.get('effect', 'Unknown')
            severity = check.get('severity', 'Unknown').upper()
            status = '✅ COMPLIANT' if check.get('compliant', False) else '❌ NON-COMPLIANT'
            affected_resources = ', '.join(check.get('affected_resources', [])) or 'None'
            
            # Truncate long resource lists for table formatting
            if len(affected_resources) > 40:
                affected_resources = affected_resources[:37] + '...'
            
            # Truncate policy name if too long
            if len(policy_name) > 30:
                policy_name = policy_name[:27] + '...'
            
            table += f"\n| {policy_name} | {category} | {effect} | {severity} | {status} | {affected_resources} |"
        
        # Add summary statistics
        total_policies = len(policy_checks)
        compliant_policies = sum(1 for check in policy_checks if check.get('compliant', False))
        non_compliant_policies = total_policies - compliant_policies
        compliance_rate = (compliant_policies/total_policies*100) if total_policies > 0 else 0
        
        table += f"""

### 📊 Custom Policy Compliance Summary
- **Total Custom Policies Evaluated**: {total_policies}
- **Compliant**: {compliant_policies} ✅
- **Non-Compliant**: {non_compliant_policies} ❌
- **Compliance Rate**: {compliance_rate:.1f}%

"""
        
        # Add breakdown by category
        if policy_checks:
            categories = {}
            for check in policy_checks:
                category = check.get('category', 'Unknown')
                if category not in categories:
                    categories[category] = {'total': 0, 'compliant': 0}
                categories[category]['total'] += 1
                if check.get('compliant', False):
                    categories[category]['compliant'] += 1
            
            table += "### 📂 Compliance by Category\n"
            for category, stats in categories.items():
                compliance_rate = (stats['compliant']/stats['total']*100) if stats['total'] > 0 else 0
                table += f"- **{category}**: {stats['compliant']}/{stats['total']} compliant ({compliance_rate:.1f}%)\n"
        
        table += "\n---\n"
        return table
    
    def _generate_immediate_actions(self, violations: list) -> str:
        """Generate immediate actions based on violations"""
        if not violations:
            return "✅ **No immediate actions required** - All policies are compliant!"
        
        critical_violations = [v for v in violations if v.get('severity') == 'critical']
        
        actions = []
        
        if critical_violations:
            actions.append("🔴 **CRITICAL**: Address critical security violations immediately:")
            for violation in critical_violations[:3]:  # Show top 3 critical
                component = violation.get('component', 'Unknown')
                description = violation.get('description', 'Critical issue')[:60]
                actions.append(f"   - **{component}**: {description}")
            
            if len(critical_violations) > 3:
                actions.append(f"   - ... and {len(critical_violations) - 3} more critical issues")
        
        high_medium_violations = [v for v in violations if v.get('severity') in ['high', 'medium']]
        if high_medium_violations:
            actions.append("\n🟡 **HIGH/MEDIUM**: Review and plan fixes for:")
            for violation in high_medium_violations[:2]:  # Show top 2
                component = violation.get('component', 'Unknown')
                recommendation = violation.get('recommendation', 'Review required')[:50]
                actions.append(f"   - **{component}**: {recommendation}")
        
        if not actions:
            actions.append("🔍 **Review all violations** and implement recommended fixes")
        
        return "\n".join(actions)
    
    def _generate_simple_readme(self) -> str:
        """Generate simple README for the ZIP package"""
        return """# Digital Superman Azure Architecture Package

This package contains the generated Azure architecture resources and compliance reports.

## Contents

- `main.bicep` - Main Bicep template with all resources
- `parameters.json` - Parameter file for deployment
- `POLICY_COMPLIANCE_REPORT.md` - Detailed compliance analysis with custom policies
- `AUTOFIX_SUMMARY.md` - Summary of auto-applied fixes (if any)

## Quick Start

1. Review the compliance report to understand any policy violations
2. Modify parameters.json with your specific values
3. Deploy using Azure CLI:
   ```bash
   az deployment group create --resource-group myResourceGroup --template-file main.bicep --parameters @parameters.json
   ```

## Prerequisites

- Azure CLI installed and configured
- Appropriate permissions to deploy resources
- Resource group created

## Custom Policies

This package includes evaluation results for organization-specific Azure policies. 
Check the compliance report for details on which policies were evaluated and their results.

## Support

For issues or questions, contact your Azure administrator or review the compliance report for specific recommendations.

---
*Generated by Digital Superman Azure Architecture Analyzer*
"""
    
    def _generate_policy_compliance_table(self, compliance: Dict[str, Any], environment: str) -> str:
        """Generate a clean policy compliance report with tables"""
        
        overall = compliance.get('overall_compliance', {})
        violations = compliance.get('violations', [])
        recommendations = compliance.get('recommendations', [])
        fixes_applied = compliance.get('fixes_applied', [])
        post_fix_compliance = compliance.get('post_fix_compliance', {})
        
        # Use post-fix compliance if available
        if post_fix_compliance:
            overall = post_fix_compliance.get('overall_compliance', overall)
            remaining_violations = post_fix_compliance.get('violations', [])
        else:
            remaining_violations = violations
        
        report = f"""# Policy Compliance Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Environment:** {environment.title()}  
**Compliance Status:** {'✅ COMPLIANT' if overall.get('compliant', False) else '❌ NON-COMPLIANT'}  
**Compliance Score:** {overall.get('compliance_score', 'Unknown')}
**Auto-Fixes Applied:** {len(fixes_applied)} {'🔧' if fixes_applied else ''}

---

## 📊 Compliance Summary

| Metric | Original | After Auto-Fix | Status |
|--------|----------|----------------|--------|
| 🔴 Critical Violations | {len([v for v in violations if v.get('severity') == 'critical'])} | {len([v for v in remaining_violations if v.get('severity') == 'critical'])} | {'✅ Improved' if len(fixes_applied) > 0 else '❌ Action Required' if len(remaining_violations) > 0 else '✅ Clean'} |
| 🟡 Warnings | {len([v for v in violations if v.get('severity') in ['medium', 'warning']])} | {len([v for v in remaining_violations if v.get('severity') in ['medium', 'warning']])} | {'✅ Improved' if len(fixes_applied) > 0 else '⚠️ Review Needed' if len(remaining_violations) > 0 else '✅ Clean'} |
| 💡 Recommendations | {len(recommendations)} | {len(recommendations)} | {'📝 Available' if len(recommendations) > 0 else '✅ None'} |
| 📋 Total Issues | {len(violations)} | {len(remaining_violations)} | {'🔧 Auto-Fixed' if len(fixes_applied) > 0 else '🔍 Review Required' if len(remaining_violations) > 0 else '✅ All Clear'} |

---

"""

        # Auto-fix summary section
        if fixes_applied:
            report += f"""## 🔧 Auto-Fix Summary

**{len(fixes_applied)} violations were automatically resolved:**

| Component | Fix Applied | Status |
|-----------|-------------|--------|
"""
            for fix in fixes_applied:
                component = fix.get('component', 'Unknown')
                fix_desc = fix.get('fix_applied', 'Security enhancement applied')
                report += f"| {component} | {fix_desc} | ✅ Fixed |\n"
            
            report += "\n💡 *See AUTOFIX_SUMMARY.md for detailed fix information*\n\n---\n\n"

        if remaining_violations:
            report += """## 🚨 Remaining Policy Violations

| Severity | Component | Category | Issue | Recommendation |
|----------|-----------|----------|-------|----------------|
"""
            for violation in remaining_violations:
                severity_icon = {
                    'critical': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢',
                    'info': 'ℹ️'
                }.get(violation.get('severity', 'unknown').lower(), '❓')
                
                component = violation.get('component', 'Unknown')[:30]
                category = violation.get('category', 'Unknown')[:20]
                description = violation.get('description', 'No description')[:50] + ('...' if len(violation.get('description', '')) > 50 else '')
                recommendation = violation.get('recommendation', 'No recommendation')[:60] + ('...' if len(violation.get('recommendation', '')) > 60 else '')
                
                report += f"| {severity_icon} {violation.get('severity', 'Unknown').title()} | {component} | {category} | {description} | {recommendation} |\n"
            
            report += "\n"
        else:
            report += "## ✅ No Policy Violations Found\n\nAll Azure policies are compliant! 🎉\n\n"

        # Add recommendations section if available
        if recommendations:
            report += """---

## 💡 Recommendations for Improvement

| Priority | Component | Category | Recommendation | Benefits |
|----------|-----------|----------|----------------|----------|
"""
            for rec in recommendations:
                priority_icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rec.get('priority', 'medium').lower(), '🟡')
                
                component = rec.get('component', 'Unknown')[:25]
                category = rec.get('category', 'Unknown')[:15]
                description = rec.get('description', 'No description')[:60] + ('...' if len(rec.get('description', '')) > 60 else '')
                benefits = rec.get('benefits', 'Improved compliance')[:50] + ('...' if len(rec.get('benefits', '')) > 50 else '')
                
                report += f"| {priority_icon} {rec.get('priority', 'Medium').title()} | {component} | {category} | {description} | {benefits} |\n"
        
        report += f"""
---

## 📋 Next Steps

### Immediate Actions Required:
{self._generate_immediate_actions(remaining_violations)}

### Deployment Notes:
- Review the Bicep templates in the `bicep/` folder
- Check parameter files for environment-specific values
- Run `az deployment group validate` before actual deployment
- Monitor compliance post-deployment

### Support:
- Check the `README.md` for deployment instructions
- View `AUTOFIX_SUMMARY.md` for applied fixes
- Contact your Azure administrator for policy exemptions if needed

---
*Report generated by Digital Superman Azure Architecture Analyzer*
"""
        
        return report
    
    def _add_scripts(self, zipf: zipfile.ZipFile, templates: Dict[str, Any], environment: str):
        """Add environment-specific scripts to ZIP"""
        scripts = templates.get('scripts', {})
        
        for script_name, script_content in scripts.items():
            # Only include scripts for the target environment
            if environment in script_name or 'main' in script_name or not any(env in script_name for env in ['dev', 'staging', 'prod']):
                zipf.writestr(f"scripts/{script_name}", script_content)
    
    def _generate_deploy_script(self) -> str:
        """Generate deployment script"""
        return """param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$Location,
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = "../bicep/main.bicep",
    
    [Parameter(Mandatory=$false)]
    [string]$ParametersFile = "../bicep/parameters/$Environment.parameters.json"
)

Write-Host "🚀 Digital Superman - Infrastructure Deployment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "❌ Azure CLI not found. Please install Azure CLI."
    exit 1
}

if (-not (Get-Command bicep -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Bicep CLI..." -ForegroundColor Yellow
    az bicep install
}

# Create resource group if it doesn't exist
Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Green
az group create --name $ResourceGroupName --location $Location

# Validate template
Write-Host "Validating Bicep template..." -ForegroundColor Green
$validationResult = az deployment group validate `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters @$ParametersFile `
    --output json | ConvertFrom-Json

if ($validationResult.error) {
    Write-Error "❌ Template validation failed:"
    Write-Error $validationResult.error.message
    exit 1
}

Write-Host "✅ Template validation successful!" -ForegroundColor Green

# Deploy infrastructure
Write-Host "Deploying infrastructure..." -ForegroundColor Green
$deploymentResult = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters @$ParametersFile `
    --output json | ConvertFrom-Json

if ($deploymentResult.properties.provisioningState -eq "Succeeded") {
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
    Write-Host "Location: $Location" -ForegroundColor Cyan
    Write-Host "Environment: $Environment" -ForegroundColor Cyan
} else {
    Write-Error "❌ Deployment failed!"
    Write-Error $deploymentResult.properties.error.message
    exit 1
}
"""

    def _generate_validation_script(self) -> str:
        """Generate validation script"""
        return """param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$TemplateFile = "../bicep/main.bicep",
    
    [Parameter(Mandatory=$false)]
    [string]$ParametersFile = "../bicep/parameters/dev.parameters.json"
)

Write-Host "🔍 Digital Superman - Template Validation" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if Azure CLI is available
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "❌ Azure CLI not found. Please install Azure CLI."
    exit 1
}

# Check if Bicep CLI is available
if (-not (Get-Command bicep -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Bicep CLI..." -ForegroundColor Yellow
    az bicep install
}

# Validate Bicep syntax
Write-Host "Validating Bicep syntax..." -ForegroundColor Green
bicep build $TemplateFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Bicep syntax validation failed!"
    exit 1
}

# Validate ARM template
Write-Host "Validating ARM template..." -ForegroundColor Green
$validationResult = az deployment group validate `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters @$ParametersFile `
    --output json | ConvertFrom-Json

if ($validationResult.error) {
    Write-Error "❌ ARM template validation failed:"
    Write-Error $validationResult.error.message
    exit 1
}

Write-Host "✅ Validation completed successfully!" -ForegroundColor Green
Write-Host "Templates are ready for deployment." -ForegroundColor Green
"""
