# Digital Superman - Clean Project Structure

## Directory Structure

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
│   ├── __init__.py
│   ├── architecture_analyzer.py    # Analyzes architecture diagrams
│   ├── bicep_generator.py          # Generates Bicep templates
│   └── policy_checker.py           # Validates compliance policies
│
├── utils/                          # Utility Functions
│   ├── __init__.py
│   ├── cost_estimator.py           # Azure cost estimation
│   ├── file_processor.py           # File format processing
│   ├── performance.py              # Performance monitoring
│   └── zip_generator.py            # Output package generation
│
├── static/                         # Static Web Assets
│   └── samples/                    # Sample architecture files
│       ├── sample-azure-architecture.drawio
│       ├── sample-azure-architecture.svg
│       └── sample-architecture-description.txt
│
├── templates/                      # HTML Templates
│   └── index.html                  # Main web interface
│
├── scripts/                        # Deployment & Utility Scripts
│   ├── start_flask.ps1             # Flask startup script
│   ├── start_flask.bat             # Flask startup batch file
│   ├── check_flask.ps1             # Health check script
│   ├── diagnose_flask.ps1          # Diagnostic script
│   └── production_checklist.ps1    # Production deployment checklist
│
├── tests/                          # Test Suite
│   ├── test_architecture_analyzer.py
│   ├── test_comprehensive_cost_estimation.py
│   ├── test_simple_flow.py
│   ├── test_complete_integration.py
│   ├── test_policy_integration.py
│   ├── test_visual_architecture.py
│   ├── test_cost_estimator.py
│   ├── test_environment_costs.py
│   ├── test_enhanced_report.py
│   ├── test_image_validation.py
│   ├── test_upload.py
│   ├── test_validation.py
│   ├── test_complete_flow.py
│   ├── test_complete_zip.py
│   ├── test_cost_optimization.py
│   └── debug_cost_estimation.py
│
├── docs/                           # Documentation
│   ├── AGENT_COMMUNICATION.md      # Agent interaction documentation
│   ├── ARCHITECTURE_ANALYZER_TEST_REPORT.md
│   ├── COST_ESTIMATION_FIX_SUMMARY.md
│   ├── PRODUCTION_SUMMARY.md       # Production deployment guide
│   └── TROUBLESHOOTING.md          # Troubleshooting guide
│
├── policies/                       # Azure Policy Templates
│   └── (policy files)
│
├── uploads/                        # File Uploads (Runtime)
│   └── (uploaded architecture files)
│
├── output/                         # Generated Outputs (Runtime)
│   └── (generated ZIP packages)
│
├── .github/                        # GitHub Configuration
│   └── copilot-instructions.md     # Copilot development guidelines
│
├── .vscode/                        # VS Code Configuration
│   └── tasks.json                  # Build and run tasks
│
└── venv/                           # Python Virtual Environment
    └── (virtual environment files)
```

## Core Application Files

- **app.py**: Main Flask application with routes and request handling
- **config.py**: Environment and application configuration management
- **requirements.txt**: Python package dependencies

## Key Features

### AI Agents (`agents/`)
- **Architecture Analyzer**: Processes architecture diagrams and extracts Azure components
- **Policy Checker**: Validates architecture against Azure policies and compliance rules
- **Bicep Generator**: Generates Infrastructure as Code templates and deployment pipelines

### Utilities (`utils/`)
- **Cost Estimator**: Calculates Azure resource costs with environment-based scaling
- **File Processor**: Handles multiple file formats (PNG, JPG, PDF, XML, Draw.io, VSDX, SVG)
- **ZIP Generator**: Creates downloadable packages with Bicep templates and documentation

### Web Interface (`static/`, `templates/`)
- Modern Bootstrap-based UI for file upload and processing
- Sample architecture files for testing and demonstration

### Development Tools (`scripts/`)
- PowerShell scripts for Flask application management
- Health checking and diagnostic utilities
- Production deployment checklists

### Testing (`tests/`)
- Comprehensive test suite covering all components
- Integration tests for end-to-end workflow validation
- Performance and cost estimation testing

### Documentation (`docs/`)
- Architecture and design documentation
- Troubleshooting guides and production deployment instructions
- Test reports and analysis summaries

## Runtime Directories

- **uploads/**: Temporary storage for uploaded architecture files
- **output/**: Generated ZIP packages ready for download
- **policies/**: Azure policy templates and validation rules

This clean structure separates concerns properly and makes the project easier to navigate and maintain.
