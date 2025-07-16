import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import config
from agents.architecture_analyzer import ArchitectureAnalyzer
from agents.policy_checker import PolicyChecker
from agents.bicep_generator import BicepGenerator
from utils.file_processor import FileProcessor
from utils.zip_generator import ZipGenerator
from utils.performance import perf_monitor

app = Flask(__name__)
app.config.from_object(config)

# Singleton instances for performance (lazy loading)
_arch_analyzer = None
_policy_checker = None
_bicep_generator = None
_file_processor = None
_zip_generator = None

def get_arch_analyzer():
    global _arch_analyzer
    if _arch_analyzer is None:
        _arch_analyzer = ArchitectureAnalyzer()
    return _arch_analyzer

def get_policy_checker():
    global _policy_checker
    if _policy_checker is None:
        _policy_checker = PolicyChecker()
    return _policy_checker

def get_bicep_generator():
    global _bicep_generator
    if _bicep_generator is None:
        _bicep_generator = BicepGenerator()
    return _bicep_generator

def get_file_processor():
    global _file_processor
    if _file_processor is None:
        _file_processor = FileProcessor()
    return _file_processor

def get_zip_generator():
    global _zip_generator
    if _zip_generator is None:
        _zip_generator = ZipGenerator()
    return _zip_generator

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['file']
    environment = request.form.get('environment', 'development')
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type'})
    
    # Save file with timestamp
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Process through unified agent (faster single call)
        result = process_architecture_diagram(filepath, environment)
        
        # Check if there was a validation error
        if isinstance(result, dict) and result.get('error'):
            error_type = result.get('error_type')
            if error_type == 'non_azure_architecture':
                return jsonify({
                    'success': False,
                    'error_type': 'non_azure_architecture',
                    'message': result.get('message', 'We only support Azure architecture diagrams.'),
                    'detected_platforms': result.get('detected_platforms', []),
                    'suggestion': result.get('suggestion', 'Please upload an Azure-specific architecture diagram.')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'An error occurred during processing.')
                })
        
        # Extract zip filename and processing summary from successful result
        if isinstance(result, dict) and 'zip_filename' in result:
            zip_filename = result['zip_filename']
            processing_summary = result.get('processing_summary', {})
        else:
            # Backward compatibility - if just filename returned
            zip_filename = result
            processing_summary = {}
        
        # Normal successful processing
        return jsonify({
            'success': True,
            'message': 'File processed successfully',
            'download_url': url_for('download_result', filename=zip_filename),
            'processing_summary': processing_summary
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@perf_monitor.time_function("process_architecture_diagram")
def process_architecture_diagram(filepath, environment):
    """Optimized processing through 3 agents with caching and performance monitoring"""
    try:
        # Step 1: Extract content from the uploaded file (cached)
        content = get_file_processor().process_file(filepath)
        
        # Step 2: Analyze architecture with Agent 1
        architecture_analysis = get_arch_analyzer().analyze_architecture(content)
        
        # Check if architecture validation failed (non-Azure resources detected)
        if architecture_analysis.get('error') == 'non_azure_architecture':
            return {
                'error': 'non_azure_architecture',
                'error_type': 'non_azure_architecture',
                'message': architecture_analysis.get('error_message', 'We only support Azure architecture diagrams.'),
                'detected_platforms': architecture_analysis.get('detected_platforms', []),
                'suggestion': architecture_analysis.get('suggestion', 'Please upload an Azure-specific architecture diagram.')
            }
        
        # Step 3: Check policy compliance with Agent 2
        policy_compliance = get_policy_checker().check_compliance(architecture_analysis, environment)
        
        # Step 3.5: Auto-fix policy violations if any exist
        fixed_analysis = architecture_analysis
        if policy_compliance.get('violations'):
            print(f"🔧 Auto-fixing {len(policy_compliance.get('violations', []))} policy violations...")
            fixed_analysis = get_policy_checker().fix_policy_violations(
                architecture_analysis, 
                policy_compliance, 
                environment
            )
            
            # Re-run policy check on fixed analysis
            print("🔍 Re-checking compliance after auto-fixes...")
            updated_policy_compliance = get_policy_checker().check_compliance(fixed_analysis, environment)
            
            # Update policy result with fix information
            policy_compliance['fixes_applied'] = fixed_analysis.get('metadata', {}).get('policy_fixes_applied', [])
            policy_compliance['post_fix_compliance'] = updated_policy_compliance
            print(f"✅ Policy compliance improved: {len(policy_compliance.get('fixes_applied', []))} fixes applied")
        
        # Step 4: Generate bicep templates and YAML pipelines with Agent 3 (using fixed analysis)
        bicep_templates = get_bicep_generator().generate_bicep_templates(
            fixed_analysis, 
            policy_compliance,
            environment
        )
        
        # Step 5: Create ZIP file with all generated content
        zip_filename = get_zip_generator().create_zip_package(
            bicep_templates,
            architecture_analysis,
            policy_compliance,
            environment
        )
        
        # Prepare processing summary for frontend
        processing_summary = {
            'architecture_summary': {
                'components_count': len(architecture_analysis.get('components', [])),
                'services_identified': len(set(comp.get('type', '') for comp in architecture_analysis.get('components', []))),
                'environment': environment
            },
            'policy_compliance': {
                'compliant': policy_compliance.get('compliant', False),
                'violations_count': len(policy_compliance.get('violations', [])),
                'fixes_applied': len(policy_compliance.get('fixes_applied', []))
            }
        }
        
        return {
            'zip_filename': zip_filename,
            'processing_summary': processing_summary
        }
        
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

@app.route('/download/<filename>')
def download_result(filename):
    try:
        return send_file(
            os.path.join('output', filename),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error downloading file: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download-sample/<sample_type>')
def download_sample(sample_type):
    """Download sample architecture diagrams for testing"""
    try:
        sample_files = {
            'svg': ('sample-azure-architecture.svg', 'Sample Azure Architecture (SVG)'),
            'drawio': ('sample-azure-architecture.drawio', 'Sample Azure Architecture (Draw.io)'),
            'txt': ('sample-architecture-description.txt', 'Sample Architecture Description (Text)')
        }
        
        if sample_type not in sample_files:
            flash('Invalid sample type')
            return redirect(url_for('index'))
            
        filename, description = sample_files[sample_type]
        filepath = os.path.join('static', 'samples', filename)
        
        if not os.path.exists(filepath):
            flash(f'Sample file not found: {filename}')
            return redirect(url_for('index'))
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Error downloading sample: {str(e)}')
        return redirect(url_for('index'))

@app.route('/samples')
def list_samples():
    """API endpoint to list available sample files"""
    samples = [
        {
            'type': 'svg',
            'name': 'Azure Web App Architecture (SVG)',
            'description': 'Visual diagram showing a 3-tier Azure web application with Front Door, App Service, SQL Database, and monitoring components',
            'download_url': url_for('download_sample', sample_type='svg')
        },
        {
            'type': 'drawio',
            'name': 'Azure Web App Architecture (Draw.io)',
            'description': 'Draw.io XML format of the same architecture - perfect for testing XML processing',
            'download_url': url_for('download_sample', sample_type='drawio')
        },
        {
            'type': 'txt',
            'name': 'Architecture Description (Text)',
            'description': 'Detailed text description of Azure architecture components and data flow',
            'download_url': url_for('download_sample', sample_type='txt')
        }
    ]
    return jsonify({'samples': samples})

@app.route('/policies')
def policy_info():
    """Get information about loaded policies"""
    try:
        policy_checker = get_policy_checker()
        summary = policy_checker.get_policy_summary()
        return jsonify({
            'status': 'success',
            'data': summary,
            'message': f"Loaded {summary['total_policies']} policies across {len(summary['categories'])} categories"
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving policy information: {str(e)}'
        }), 500

@app.route('/policies/reload', methods=['POST'])
def reload_policies():
    """Reload policies from the policies folder"""
    try:
        policy_checker = get_policy_checker()
        policy_checker.reload_policies()
        summary = policy_checker.get_policy_summary()
        return jsonify({
            'status': 'success',
            'data': summary,
            'message': f"Policies reloaded successfully. {summary['total_policies']} policies loaded."
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error reloading policies: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/performance')
def performance_stats():
    """Get performance statistics"""
    return jsonify(perf_monitor.get_stats())

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
