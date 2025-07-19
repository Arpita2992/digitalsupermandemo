#!/usr/bin/env python3
"""
Digital Superman - Simple Flask Application
No complex middleware, just core functionality
"""

import os
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
import config

# Create Flask app
app = Flask(__name__)
app.config.from_object(config)

# Ensure upload directory exists
os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
os.makedirs('output', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Digital Superman Flask is running perfectly!'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Simple file upload handler"""
    try:
        from app import process_architecture_diagram_async
        from utils.file_validator import file_validator
        from utils.logging_config import get_logger
        logger = get_logger(__name__)
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file selected'
            })
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            })
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Allowed: PNG, JPG, PDF, XML, DrawIO, VSDX, SVG'
            })
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Get environment parameter
        environment = request.form.get('environment', 'development')
        # Enhanced file validation with MIME type checking
        is_valid, validation_error = file_validator.validate_file(filepath, file.filename)
        if not is_valid:
            try:
                os.remove(filepath)
            except OSError:
                pass
            return jsonify({
                'success': False,
                'message': f'File validation failed: {validation_error}'
            })
        # Log file info for security monitoring
        file_info = file_validator.get_file_info(filepath)
        logger.info(f"Validated file upload: {file.filename}", extra={
            'file_info': file_info,
            'user_ip': request.remote_addr,
            'file_size': file_info.get('size', 0)
        })
        # Run the real agent pipeline
        result = process_architecture_diagram_async(filepath, environment)
        # Handle errors
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
            zip_filename = result
            processing_summary = {}
        # Return successful result
        return jsonify({
            'success': True,
            'message': 'File processed successfully',
            'download_url': url_for('download_result', filename=zip_filename),
            'processing_summary': processing_summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Upload error: {str(e)}'
        })

@app.route('/download/<filename>')
def download_result(filename):
    """Download endpoint - for now returns a placeholder"""
    try:
        # TODO: Replace with actual ZIP file generation
        # For now, create a simple text file as placeholder
        placeholder_content = f"""
Digital Superman - Architecture Analysis Results
==============================================

Filename: {filename}
Generated: {datetime.now().isoformat()}
Environment: Development

This is a placeholder file. 
The actual Bicep templates and DevOps pipelines will be generated here.

Architecture Components Detected:
- Web App Service
- SQL Database  
- Application Gateway
- Key Vault
- Storage Account

Policy Compliance: PASSED
Cost Optimization: 2 recommendations
Estimated Savings: $150/month

Next Steps:
1. Review the generated Bicep templates
2. Customize parameters for your environment
3. Deploy using the included DevOps pipeline
4. Monitor with the included ARM policies

Thank you for using Digital Superman!
"""
        
        # Create a temporary text file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', 
                                       delete=False) as tmp_file:
            tmp_file.write(placeholder_content)
            tmp_file_path = tmp_file.name
        
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=f"{filename}.txt",
            mimetype='text/plain'
        )
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500


@app.route('/test')
def test_endpoint():
    """Test endpoint to verify everything is working"""
    return jsonify({
        'message': 'Test successful!',
        'flask_version': Flask.__version__,
        'python_executable': os.sys.executable,
        'working_directory': os.getcwd(),
        'upload_folder': app.config.get('UPLOAD_FOLDER'),
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Digital Superman - Simple Flask Server")
    print("=" * 45)
    print(f"📡 URL: http://localhost:5000")
    print(f"🏥 Health: http://localhost:5000/health")
    print(f"🧪 Test: http://localhost:5000/test")
    print(f"📁 Uploads: {app.config.get('UPLOAD_FOLDER', 'uploads')}")
    print("🎯 Status: Ready for testing")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    # Simple Flask run - no complex configurations
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        threaded=True,
        use_reloader=False  # Disable reloader to prevent issues
    )
