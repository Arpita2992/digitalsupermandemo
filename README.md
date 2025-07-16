# Digital Superman - Azure Architecture to Infrastructure Code

Transform your Azure architecture diagrams into production-ready infrastructure code with AI-powered automation.

## 🚀 Features

- **AI-Powered Analysis**: Three specialized AI agents process your architecture diagrams
- **Multi-Format Support**: PNG, JPG, PDF, XML, Draw.io, VSDX, SVG files
- **Bicep Templates**: Generate modular, production-ready Bicep templates
- **Azure DevOps Integration**: Create CI/CD pipelines for automated deployments
- **Policy Compliance**: Validate architecture against Azure best practices and custom policies
- **Cost Estimation**: Generate detailed cost estimates for Azure resources
- **Environment-Specific**: Support for development, staging, and production environments
- **Complete Documentation**: Generate comprehensive deployment guides and cost reports

## 🤖 AI Agents

### 1. Architecture Analyzer
- Analyzes uploaded architecture diagrams
- Identifies Azure components and relationships
- Extracts configuration details and dependencies
- Provides Azure policy compliance recommendations

### 2. Policy Checker
- Validates architecture against Microsoft Azure policies
- Checks security, governance, and compliance requirements
- Supports 41+ custom organizational policies
- Provides environment-specific recommendations
- Generates detailed compliance reports with custom policies table

### 3. Bicep Generator
- Creates production-ready Bicep templates
- Generates Azure DevOps YAML pipelines
- Provides parameter files for different environments
- Includes deployment scripts and documentation

### 4. Cost Estimator
- Estimates monthly and yearly costs for Azure resources
- Provides environment-specific cost adjustments
- Generates detailed cost breakdown by resource type
- Includes cost optimization recommendations
- Supports regional pricing variations

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Azure subscription (optional, for enhanced features)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DigitalSuperman
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up environment variables**
   ```bash
   # Azure AI Foundry Configuration (Recommended)
   AZURE_AI_AGENT1_ENDPOINT=https://your-foundry-endpoint.cognitiveservices.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview
   AZURE_AI_AGENT1_KEY=your-azure-ai-foundry-key
   AZURE_AI_AGENT1_DEPLOYMENT=gpt-4.1
   
   AZURE_AI_AGENT2_ENDPOINT=https://your-foundry-endpoint.cognitiveservices.azure.com/openai/deployments/gpt-4.1-2/chat/completions?api-version=2025-01-01-preview
   AZURE_AI_AGENT2_KEY=your-azure-ai-foundry-key
   AZURE_AI_AGENT2_DEPLOYMENT=gpt-4.1
   
   AZURE_AI_AGENT3_ENDPOINT=https://your-foundry-endpoint.cognitiveservices.azure.com/openai/deployments/gpt-4.1-3/chat/completions?api-version=2025-01-01-preview
   AZURE_AI_AGENT3_KEY=your-azure-ai-foundry-key
   AZURE_AI_AGENT3_DEPLOYMENT=gpt-4.1
   
   # Fallback OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key-here
   
   # Optional Azure Configuration
   AZURE_SUBSCRIPTION_ID=your-azure-subscription-id
   AZURE_TENANT_ID=your-azure-tenant-id
   AZURE_CLIENT_ID=your-azure-client-id
   AZURE_CLIENT_SECRET=your-azure-client-secret
   
   # Flask Configuration
   SECRET_KEY=your-very-secret-key-change-this-in-production
   DEBUG=True
   ```

## 🚀 Usage

### Running the Application

1. **Start the Flask application**
   ```bash
   # Using PowerShell script (recommended)
   .\scripts\start_flask.ps1

   # Or directly with Python
   python app.py
   ```

2. **Access the web interface**
   - Open your browser to `http://localhost:5000`

3. **Upload your architecture diagram**
   - Select environment (Development/Production)
   - Upload your diagram file
   - Wait for AI processing
   - Download the generated package

### Supported File Formats

- **Images**: PNG, JPG, JPEG
- **Documents**: PDF
- **Diagrams**: Draw.io (.drawio), Visio (.vsdx), SVG
- **Structured**: XML

### Generated Output

The application creates a clean ZIP package containing:

```
digital_superman_<environment>_<timestamp>.zip
├── bicep/
│   ├── main.bicep              # Main Bicep template
│   ├── modules/                # Modular templates
│   │   ├── network.bicep
│   │   ├── compute.bicep
│   │   └── storage.bicep
│   └── parameters/             # Parameter files
│       ├── dev.parameters.json
│       └── prod.parameters.json
├── pipelines/
│   ├── azure-pipelines.yml     # Main CI/CD pipeline
│   ├── build.yml              # Build pipeline
│   ├── deploy-dev.yml         # Development deployment
│   └── deploy-prod.yml        # Production deployment
├── scripts/
│   ├── deploy.ps1             # PowerShell deployment
│   └── validate.ps1           # Validation script
├── POLICY_COMPLIANCE_REPORT.md # Policy compliance with tables
└── README.md                  # Usage instructions
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main application interface |
| POST | `/upload` | Upload and process architecture diagram |
| GET | `/download/<filename>` | Download generated package |
| GET | `/download-sample/<type>` | Download sample diagrams (svg/drawio/txt) |
| GET | `/samples` | List available sample files (API) |
| GET | `/health` | Health check endpoint |

### Upload Request

```bash
curl -X POST -F "file=@diagram.png" -F "environment=development" http://localhost:5000/upload
```

### Response

```json
{
  "success": true,
  "message": "File processed successfully",
  "download_url": "/download/digital_superman_development_20250714_143022.zip"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI processing | Yes |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | No |
| `AZURE_TENANT_ID` | Azure tenant ID | No |
| `AZURE_CLIENT_ID` | Azure client ID | No |
| `AZURE_CLIENT_SECRET` | Azure client secret | No |
| `SECRET_KEY` | Flask secret key | Yes |
| `DEBUG` | Enable debug mode | No |

### File Upload Limits

- **Maximum file size**: 16MB
- **Supported formats**: PNG, JPG, JPEG, PDF, XML, Draw.io, VSDX, SVG
- **Concurrent uploads**: Single file processing

## 🏗️ Architecture

### Project Structure

```
digitalsupermandemo/
├── app.py                          # Main Flask application
├── config.py                       # Application configuration
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── agents/                         # AI Processing Agents
│   ├── architecture_analyzer.py    # Analyzes architecture diagrams
│   ├── bicep_generator.py          # Generates Bicep templates
│   └── policy_checker.py           # Validates compliance policies
│
├── utils/                          # Utility Functions
│   ├── cost_estimator.py           # Azure cost estimation
│   ├── file_processor.py           # File format processing
│   ├── performance.py              # Performance monitoring
│   └── zip_generator.py            # Output package generation
│
├── static/                         # Static Web Assets
│   └── samples/                    # Sample architecture files
│
├── templates/                      # HTML Templates
│   └── index.html                  # Main web interface
│
├── scripts/                        # Deployment & Utility Scripts
│   ├── start_flask.ps1             # Flask startup script
│   └── production_checklist.ps1    # Production deployment checklist
│
├── tests/                          # Test Suite
│   └── (comprehensive test files)
│
├── docs/                           # Documentation
│   ├── TROUBLESHOOTING.md          # Troubleshooting guide
│   └── PRODUCTION_SUMMARY.md       # Production deployment guide
│
├── policies/                       # Azure Policy Templates
├── uploads/                        # File Uploads (Runtime)
└── output/                         # Generated Outputs (Runtime)
```

### AI Processing Flow

1. **File Upload** → File processor extracts content
2. **Agent 1** → Architecture analyzer processes diagram
3. **Agent 2** → Policy checker validates compliance
4. **Agent 3** → Bicep generator creates templates
5. **Package** → ZIP generator creates download package

## 🧪 Testing

### Manual Testing

1. **Test Azure AI Foundry connectivity**
   ```bash
   python test_agents.py
   ```

2. **Test sample downloads**
   ```bash
   curl http://localhost:5000/download-sample/svg -o sample.svg
   curl http://localhost:5000/download-sample/drawio -o sample.drawio
   curl http://localhost:5000/download-sample/txt -o sample.txt
   ```

3. **Test file upload**
   ```bash
   curl -X POST -F "file=@test-diagram.png" -F "environment=development" http://localhost:5000/upload
   ```

4. **Test health endpoint**
   ```bash
   curl http://localhost:5000/health
   ```

5. **Test web interface**
   - Navigate to `http://localhost:5000`
   - Download a sample diagram from the "Try It with Sample Diagrams" section
   - Upload the downloaded sample
   - Verify processing and download the generated package

### Deployment Testing

1. **Validate generated Bicep templates**
   ```bash
   az bicep build --file bicep/main.bicep
   ```

2. **Test deployment (dry run)**
   ```bash
   az deployment group validate --resource-group test-rg --template-file bicep/main.bicep
   ```

## 🚀 Deployment

### Local Development

```bash
python app.py
```

### Production Deployment

1. **Using Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Using Docker** (create Dockerfile)
   ```dockerfile
   FROM python:3.9-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
   ```

3. **Azure App Service**
   - Deploy to Azure App Service
   - Configure environment variables
   - Set up continuous deployment

## 🔒 Security

### Best Practices

- **API Keys**: Store in environment variables
- **File Validation**: Validate all uploaded files
- **Input Sanitization**: Sanitize all user inputs
- **Error Handling**: Don't expose sensitive information
- **HTTPS**: Use HTTPS in production
- **Authentication**: Implement authentication if needed

### Security Considerations

- File upload validation and size limits
- Secure file storage and cleanup
- API rate limiting
- Input validation and sanitization
- Secure environment variable handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

1. **OpenAI API errors**: Check API key and quota
2. **File processing errors**: Verify file format and size
3. **Template generation errors**: Check Azure policies
4. **Deployment errors**: Validate Bicep templates

### Getting Help

- Check the documentation in the `docs/` folder
- Review generated compliance reports
- Validate templates using provided scripts
- Contact support for assistance

## 🎯 Roadmap

- [ ] Support for additional diagram formats
- [ ] Enhanced AI model fine-tuning
- [ ] Real-time collaboration features
- [ ] Integration with more Azure services
- [ ] Advanced policy compliance features
- [ ] Multi-cloud support (AWS, GCP)

---

**Digital Superman** - Transforming Azure architecture diagrams to infrastructure code with AI-powered automation.
