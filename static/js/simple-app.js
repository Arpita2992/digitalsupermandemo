// ================================================
// DIGITAL SUPERMAN - SIMPLIFIED VERSION (No WebSocket)
// ================================================

class SimpleDigitalSupermanApp {
    constructor() {
        this.fileInput = document.getElementById('fileInput');
        this.uploadZone = document.getElementById('uploadZone');
        this.uploadForm = document.getElementById('uploadForm');
        this.filePreview = document.getElementById('filePreview');
        this.submitBtn = document.getElementById('submitBtn');
        
        this.progressSection = document.getElementById('progressSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.overallProgress = document.getElementById('overallProgress');
        this.overallPercentage = document.getElementById('overallPercentage');
        this.progressStatus = document.getElementById('progressStatus');
        
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newAnalysisBtn = document.getElementById('newAnalysisBtn');
        
        this.currentFile = null;
        this.isProcessing = false;
        
        this.initializeEventListeners();
        this.initializeFileHandling();
    }
    
    initializeEventListeners() {
        // File input change event
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                this.handleFileSelection(e.target.files[0]);
            });
        }
        
        // Upload form submission
        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFileUpload();
            });
        }
        
        // New analysis button
        if (this.newAnalysisBtn) {
            this.newAnalysisBtn.addEventListener('click', () => {
                this.resetForm();
            });
        }
        
        // Download button
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', () => {
                if (this.downloadUrl) {
                    window.open(this.downloadUrl, '_blank');
                }
            });
        }
    }
    
    initializeFileHandling() {
        // Drag and drop for upload zone
        if (this.uploadZone) {
            this.uploadZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.uploadZone.classList.add('drag-over');
            });
            
            this.uploadZone.addEventListener('dragleave', () => {
                this.uploadZone.classList.remove('drag-over');
            });
            
            this.uploadZone.addEventListener('drop', (e) => {
                e.preventDefault();
                this.uploadZone.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileSelection(files[0]);
                }
            });
            
            // Click to upload
            this.uploadZone.addEventListener('click', () => {
                if (this.fileInput) {
                    this.fileInput.click();
                }
            });
        }
    }
    
    handleFileSelection(file) {
        if (!file) return;
        
        this.currentFile = file;
        this.showFilePreview(file);
        
        // Enable and show submit button
        if (this.submitBtn) {
            this.submitBtn.disabled = false;
            this.submitBtn.style.display = 'inline-block';
        }
    }
    
    showFilePreview(file) {
        if (!this.filePreview) return;
        
        const fileIcon = this.getFileIcon(file.name);
        const fileSize = this.formatFileSize(file.size);
        
        this.filePreview.innerHTML = `
            <div class="file-preview-item">
                <div class="file-icon">${fileIcon}</div>
                <div class="file-details">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${fileSize}</div>
                </div>
                <button type="button" class="btn-remove" onclick="app.removeFile()" title="Remove file">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
        
        this.filePreview.style.display = 'block';
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const icons = {
            'png': '<i class="fas fa-image"></i>',
            'jpg': '<i class="fas fa-image"></i>',
            'jpeg': '<i class="fas fa-image"></i>',
            'pdf': '<i class="fas fa-file-pdf"></i>',
            'xml': '<i class="fas fa-file-code"></i>',
            'drawio': '<i class="fas fa-project-diagram"></i>',
            'vsdx': '<i class="fas fa-project-diagram"></i>',
            'svg': '<i class="fas fa-vector-square"></i>',
            'txt': '<i class="fas fa-file-alt"></i>'
        };
        
        return icons[ext] || '<i class="fas fa-file"></i>';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    removeFile() {
        this.currentFile = null;
        if (this.filePreview) {
            this.filePreview.style.display = 'none';
        }
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        if (this.submitBtn) {
            this.submitBtn.disabled = true;
            this.submitBtn.style.display = 'none';
        }
    }
    
    async handleFileUpload() {
        if (!this.currentFile || this.isProcessing) return;
        
        this.isProcessing = true;
        this.showProgress();
        
        try {
            const formData = new FormData();
            formData.append('file', this.currentFile);
            formData.append('environment', document.getElementById('environment')?.value || 'development');
            
            // Show processing simulation
            this.simulateProcessing();
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.handleUploadSuccess(result);
            } else {
                this.handleUploadError(result);
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.handleUploadError({message: 'Upload failed: ' + error.message});
        } finally {
            this.isProcessing = false;
        }
    }
    
    simulateProcessing() {
        // Simulate processing steps
        const steps = [
            'Analyzing architecture diagram...',
            'Checking policy compliance...',
            'Optimizing costs...',
            'Generating Bicep templates...',
            'Creating deployment package...'
        ];
        
        let currentStep = 0;
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                this.updateProgressStatus(steps[currentStep]);
                this.updateOverallProgress((currentStep + 1) * 20);
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 1000);
    }
    
    handleUploadSuccess(result) {
        console.log('Upload successful:', result);
        
        // Complete the progress
        this.updateOverallProgress(100);
        this.updateProgressStatus('Processing completed successfully!');
        
        // Store download URL
        this.downloadUrl = result.download_url;
        
        // Show results after a brief delay
        setTimeout(() => {
            this.showResults(result.download_url, result.processing_summary);
        }, 1000);
    }
    
    handleUploadError(error) {
        console.error('Upload error:', error);
        this.hideProgress();
        this.showError(error.message || 'Upload failed');
    }
    
    showProgress() {
        if (this.progressSection) {
            this.progressSection.style.display = 'block';
        }
        if (this.resultsSection) {
            this.resultsSection.style.display = 'none';
        }
    }
    
    hideProgress() {
        if (this.progressSection) {
            this.progressSection.style.display = 'none';
        }
    }
    
    updateOverallProgress(percentage) {
        if (this.overallProgress) {
            this.overallProgress.style.width = percentage + '%';
        }
        if (this.overallPercentage) {
            this.overallPercentage.textContent = Math.round(percentage) + '%';
        }
    }
    
    updateProgressStatus(status) {
        if (this.progressStatus) {
            this.progressStatus.textContent = status;
        }
    }
    
    showResults(downloadUrl, summary) {
        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
        }
        if (this.progressSection) {
            this.progressSection.style.display = 'none';
        }
        if (this.downloadBtn) {
            this.downloadBtn.style.display = 'inline-block';
        }
        
        // Update summary if elements exist
        if (summary) {
            this.updateResultsSummary(summary);
        }
    }
    
    updateResultsSummary(summary) {
        // Update architecture summary
        if (summary.architecture_summary) {
            const arch = summary.architecture_summary;
            console.log('Architecture components:', arch.components_count);
            console.log('Services identified:', arch.services_identified);
        }
        
        // Update policy compliance
        if (summary.policy_compliance) {
            const policy = summary.policy_compliance;
            console.log('Policy compliant:', policy.compliant);
            console.log('Violations:', policy.violations_count);
        }
        
        // Update cost optimization
        if (summary.cost_optimization) {
            const cost = summary.cost_optimization;
            console.log('Cost recommendations:', cost.recommendations_count);
            console.log('Estimated savings:', cost.estimated_savings);
        }
    }
    
    showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <div class="error-content">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentElement) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    resetForm() {
        this.removeFile();
        this.hideProgress();
        if (this.resultsSection) {
            this.resultsSection.style.display = 'none';
        }
        if (this.downloadBtn) {
            this.downloadBtn.style.display = 'none';
        }
        this.downloadUrl = null;
        this.isProcessing = false;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SimpleDigitalSupermanApp();
    console.log('Digital Superman app initialized (Simple Mode)');
});

// Add some basic CSS for error notifications
const style = document.createElement('style');
style.textContent = `
    .error-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid rgba(255, 0, 0, 0.3);
        border-radius: 8px;
        padding: 15px;
        color: #ff4444;
        backdrop-filter: blur(10px);
        z-index: 1000;
        max-width: 400px;
    }
    
    .error-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .error-content button {
        background: none;
        border: none;
        color: #ff4444;
        cursor: pointer;
        padding: 5px;
        border-radius: 4px;
        opacity: 0.7;
    }
    
    .error-content button:hover {
        opacity: 1;
        background: rgba(255, 0, 0, 0.1);
    }
    
    .drag-over {
        border-color: #007bff !important;
        background: rgba(0, 123, 255, 0.1) !important;
    }
    
    .btn-remove {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ff6b6b !important;
        padding: 8px 10px !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .btn-remove:hover {
        background: rgba(255, 107, 107, 0.1) !important;
        border-color: rgba(255, 107, 107, 0.3) !important;
        color: #ff5252 !important;
        transform: translateY(-1px) !important;
    }
    
    .file-preview-item {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        padding: 12px !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .file-icon {
        font-size: 24px !important;
        color: #007bff !important;
    }
    
    .file-details {
        flex: 1 !important;
    }
    
    .file-name {
        font-weight: 500 !important;
        margin-bottom: 4px !important;
    }
    
    .file-size {
        font-size: 12px !important;
        opacity: 0.7 !important;
    }
`;
document.head.appendChild(style);
