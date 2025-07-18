import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import config
from agents.architecture_analyzer import ArchitectureAnalyzer
from agents.fast_analyzer import FastArchitectureAnalyzer
from agents.policy_checker import PolicyChecker
from agents.cost_optimization_agent import CostOptimizationAgent
from agents.bicep_generator import BicepGenerator
from utils.file_processor import FileProcessor
from utils.zip_generator import ZipGenerator
from utils.performance import perf_monitor, cache, cache_result, measure_execution_time

app = Flask(__name__)
app.config.from_object(config)

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

# Optimized singleton instances with lazy loading and caching
_instances = {}
_instance_lock = asyncio.Lock()

def get_instance(class_name, creator_func):
    """Thread-safe singleton instance getter with caching"""
    if class_name not in _instances:
        _instances[class_name] = creator_func()
    return _instances[class_name]

def get_arch_analyzer():
    return get_instance('arch_analyzer', ArchitectureAnalyzer)

def get_policy_checker():
    return get_instance('policy_checker', PolicyChecker)

def get_cost_optimizer():
    return get_instance('cost_optimizer', CostOptimizationAgent)

def get_bicep_generator():
    return get_instance('bicep_generator', BicepGenerator)

def get_file_processor():
    return get_instance('file_processor', FileProcessor)

def get_zip_generator():
    return get_instance('zip_generator', ZipGenerator)

@measure_execution_time
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

@app.route('/')
@cache_result(lambda: "index_page", ttl=300)  # Cache for 5 minutes
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@perf_monitor.time_function("upload_file")
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    file = request.files['file']
    environment = request.form.get('environment', 'development')
    fast_mode = request.form.get('fast_mode', 'false').lower() == 'true'
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid file type'})
    
    # Save file with timestamp
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        # Choose processing mode
        if fast_mode:
            print("🚀 Using Fast Mode Processing")
            from fast_mode_processor import FastModeProcessor
            processor = FastModeProcessor()
            result = processor.process_fast(filepath, environment)
        else:
            print("🔧 Using Full Processing Mode")
            # Process through optimized agent pipeline
            result = process_architecture_diagram_async(filepath, environment)
        
        # Check if there was a validation error
        if isinstance(result, dict) and result.get('error'):
            error_type = result.get('error_type')
            if error_type == 'non_azure_architecture':
                return jsonify({
                    'success': False,
                    'error_type': 'non_azure_architecture',
                    'message': result.get('message', 'We only support Azure architecture diagrams.'),
                    'detected_platforms': result.get('detected_platforms', []),
                    'non_azure_services': result.get('non_azure_services', []),
                    'suggestion': result.get('suggestion', 'Please upload an Azure-specific architecture diagram.')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': result.get('message', 'An error occurred during processing.'),
                    'error_details': result.get('error_details', '')
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
def process_architecture_diagram_async(filepath, environment):
    """Optimized processing with parallel agent execution and caching"""
    
    try:
        # Generate cache key based on file content hash and environment
        cache_key = f"process_{hash(filepath)}_{environment}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            print("🚀 Using cached result for file processing")
            return cached_result
        
        # Step 1: Extract content from the uploaded file (cached)
        content = get_file_processor().process_file(filepath)
        
        # Step 2: Analyze architecture with Agent 1
        future_arch = executor.submit(get_arch_analyzer().analyze_architecture, content)
        architecture_analysis = future_arch.result()
        
        # Check if architecture validation failed (non-Azure resources detected)
        if architecture_analysis.get('error') == 'non_azure_architecture':
            return {
                'error': 'non_azure_architecture',
                'error_type': 'non_azure_architecture',
                'message': architecture_analysis.get('error_message', 'We only support Azure architecture diagrams.'),
                'detected_platforms': architecture_analysis.get('detected_platforms', []),
                'non_azure_services': architecture_analysis.get('non_azure_services', []),
                'suggestion': architecture_analysis.get('suggestion', 'Please upload an Azure-specific architecture diagram.')
            }
        
        # Step 3: Parallel processing of Policy and Cost optimization
        future_policy = executor.submit(get_policy_checker().check_compliance, architecture_analysis, environment)
        
        # Wait for policy check to complete
        policy_compliance = future_policy.result()
        
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
        
        # Step 4: Run cost optimization and bicep generation in parallel
        future_cost = executor.submit(get_cost_optimizer().optimize_architecture, 
                                     fixed_analysis, policy_compliance, environment)
        
        cost_optimization = future_cost.result()
        
        # Step 5: Generate bicep templates
        future_bicep = executor.submit(get_bicep_generator().generate_bicep_templates,
                                      fixed_analysis, policy_compliance, cost_optimization, environment)
        
        bicep_templates = future_bicep.result()
        
        # Step 6: Create ZIP file
        zip_filename = get_zip_generator().create_zip_package(
            bicep_templates,
            architecture_analysis,
            policy_compliance,
            cost_optimization,
            environment
        )
        
        # Prepare processing summary
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
            },
            'cost_optimization': {
                'recommendations_count': len(cost_optimization.get('optimization_recommendations', [])),
                'estimated_savings': cost_optimization.get('optimization_summary', {}).get('estimated_monthly_savings', 'N/A'),
                'framework_applied': cost_optimization.get('framework_applied', 'Microsoft Well-Architected Framework')
            }
        }
        
        result = {
            'zip_filename': zip_filename,
            'processing_summary': processing_summary
        }
        
        # Cache the result
        cache.set(cache_key, result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Processing failed: {str(e)}")

@app.route('/download/<filename>')
@measure_execution_time
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
@cache_result(lambda sample_type: f"sample_{sample_type}", ttl=3600)
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
@cache_result(lambda: "samples_list", ttl=1800)
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
@cache_result(lambda: "policies_info", ttl=600)
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
        # Clear cache
        cache.clear()
        
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
    """Enhanced health check with performance metrics"""
    health_data = perf_monitor.get_health_status()
    return jsonify(health_data)

@app.route('/performance')
def performance_stats():
    """Get performance statistics"""
    return jsonify(perf_monitor.get_stats())

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear application cache"""
    try:
        cache.clear()
        return jsonify({'status': 'success', 'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    stats = perf_monitor.get_stats()
    return jsonify(stats.get('cache', {}))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Performance middleware
@app.before_request
def before_request():
    """Track request start time"""
    request.start_time = time.time()

@app.after_request
def after_request(response):
    """Log request performance"""
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        if duration > 1.0:  # Log slow requests
            print(f"⚠️ Slow request: {request.method} {request.path} took {duration:.2f}s")
    return response

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000, threaded=True)
