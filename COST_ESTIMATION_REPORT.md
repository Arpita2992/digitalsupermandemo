# Azure Cost Estimation Report

## Summary
**Total Monthly Cost**: $594.52
**Total Annual Cost**: $7134.24
**Environment**: production
**Region**: eastus
**Generated**: N/A

## Resource Cost Breakdown

### Azure Front Door
- **Type**: Microsoft.Network/frontDoors
- **Monthly Cost**: $343.50
- **Annual Cost**: $4122.00
- **Cost Factors**:
  - Front Door Tier: Premium
  - Routing Rules: 5
  - Data Transfer: 100 GB
- **Assumptions**:
  - Estimated 5 routing rules
  - Estimated 100 GB data transfer per month
  - Standard configuration without WAF
- **SKU/Pricing Tier**: Premium

### Application Gateway
- **Type**: Microsoft.Network/applicationGateways
- **Monthly Cost**: $22.70
- **Annual Cost**: $272.40
- **Cost Factors**:
  - Gateway Size: Standard_Small
  - Data Processing: 100 GB
- **Assumptions**:
  - Estimated 100 GB data processing per month
  - Standard configuration
  - No additional features
- **SKU/Pricing Tier**: Standard_Small

### Virtual Network
- **Type**: Microsoft.Network/virtualNetworks
- **Monthly Cost**: $0.00
- **Annual Cost**: $0.00
- **Cost Factors**:
  - Virtual Network: Free
  - Subnets: Free
  - VNet Peering: Additional cost if configured
- **Assumptions**:
  - Virtual Network itself is free
  - Costs may apply for VNet peering, gateways, and data transfer
  - Standard configuration
- **SKU/Pricing Tier**: Standard

### App Service
- **Type**: Microsoft.Web/sites
- **Monthly Cost**: $13.14
- **Annual Cost**: $157.68
- **Cost Factors**:
  - App Service Plan: P1V2
  - Always On: Enabled
  - Scaling: Manual/Auto
- **Assumptions**:
  - Uses shared App Service Plan pricing
  - Standard configuration
  - No additional features (custom domains, SSL certificates)
- **SKU/Pricing Tier**: P1V2

### SQL Database
- **Type**: Microsoft.Sql/servers/databases
- **Monthly Cost**: $75.00
- **Annual Cost**: $900.00
- **Cost Factors**:
  - Service Tier: S2
  - Max Size: 250 GB
- **Assumptions**:
  - Standard compute tier
  - No additional features (backup, geo-replication)
  - Moderate usage patterns
- **SKU/Pricing Tier**: S2

### Storage Account
- **Type**: Microsoft.Storage/storageAccounts
- **Monthly Cost**: $1.88
- **Annual Cost**: $22.56
- **Cost Factors**:
  - Storage Tier: Standard_LRS
  - Estimated Storage: 100 GB
  - Estimated Transactions: 1,000,000
- **Assumptions**:
  - Estimated 100 GB storage usage
  - Estimated 1M transactions per month
  - Standard redundancy level
- **SKU/Pricing Tier**: Standard_LRS

### Key Vault
- **Type**: Microsoft.KeyVault/vaults
- **Monthly Cost**: $0.30
- **Annual Cost**: $3.60
- **Cost Factors**:
  - Operations: 100,000
  - Rate: $0.03 per 10K operations
  - Certificate operations: Additional cost
- **Assumptions**:
  - Estimated 100,000 operations per month
  - Standard tier pricing
  - No premium features or HSM
- **SKU/Pricing Tier**: Standard

### Application Insights
- **Type**: Microsoft.Insights/components
- **Monthly Cost**: $34.50
- **Annual Cost**: $414.00
- **Cost Factors**:
  - Data Ingestion: 20 GB
  - Data Retention: 90 days (free)
  - Pricing: First 5 GB free, then $2.30/GB
- **Assumptions**:
  - Estimated 20 GB data ingestion per month
  - 90 days data retention (free tier)
  - Standard telemetry collection
- **SKU/Pricing Tier**: Pay-as-you-go

### Log Analytics
- **Type**: Microsoft.OperationalInsights/workspaces
- **Monthly Cost**: $103.50
- **Annual Cost**: $1242.00
- **Cost Factors**:
  - Data Ingestion: 50 GB
  - Data Retention: 31 days (free)
  - Pricing: First 5 GB free, then $2.30/GB
- **Assumptions**:
  - Estimated 50 GB data ingestion per month
  - 31 days data retention (free tier)
  - Standard log collection from connected resources
- **SKU/Pricing Tier**: Per-GB

## Cost by Category

- **Compute**: $13.14/month
- **Storage**: $1.88/month
- **Networking**: $366.20/month
- **Database**: $75.00/month
- **Monitoring**: $138.00/month
- **Security**: $0.30/month

## Disclaimers

- Cost estimates are based on current Azure pricing and may change
- Actual costs may vary based on usage patterns and configurations
- Estimates assume standard configurations and may not reflect all pricing tiers
- Regional pricing variations are applied where available
- This is an estimate only and should not be used for budgeting purposes