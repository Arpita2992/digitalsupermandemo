// ================================================
// DIGITAL SUPERMAN - GLASSY BLACK & WHITE APP
// Enhanced JavaScript with Glass Morphism Effects
// Updated: 4-Agent Pipeline with Cost Optimizer
// ================================================

class GlassyDigitalSupermanApp {
    constructor() {
        this.fileInput = document.getElementById('fileInput');
        this.uploadZone = document.getElementById('uploadZone');
        this.uploadForm = document.getElementById('uploadForm');
        this.filePreview = document.getElementById('filePreview');
        this.submitBtn = document.getElementById('submitBtn');
        this.fastModeCheckbox = document.getElementById('fastMode');
        
        this.agents = {
            agent1: {
                element: document.getElementById('agent1'),
                status: document.getElementById('agent1Status'),
                progress: document.getElementById('agent1Progress')
            },
            agent2: {
                element: document.getElementById('agent2'),
                status: document.getElementById('agent2Status'),
                progress: document.getElementById('agent2Progress')
            },
            agent3: {
                element: document.getElementById('agent3'),
                status: document.getElementById('agent3Status'),
                progress: document.getElementById('agent3Progress')
            },
            agent4: {
                element: document.getElementById('agent4'),
                status: document.getElementById('agent4Status'),
                progress: document.getElementById('agent4Progress')
            }
        };
        
        this.progressSection = document.getElementById('progressSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.overallProgress = document.getElementById('overallProgress');
        this.overallPercentage = document.getElementById('overallPercentage');
        this.progressETA = document.getElementById('progressETA');
        this.progressStatus = document.getElementById('progressStatus');
        
        this.downloadBtn = document.getElementById('downloadBtn');
        this.newAnalysisBtn = document.getElementById('newAnalysisBtn');
        
        this.currentFile = null;
        this.processingTimeout = null;
        this.startTime = null;
        
        this.initializeEventListeners();
        this.initializeGlassEffects();
    }
    
    initializeEventListeners() {
        // File upload events
        this.uploadZone.addEventListener('click', () => this.fileInput.click());
        this.uploadZone.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadZone.addEventListener('drop', this.handleDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Form submission
        this.uploadForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // File removal
        document.getElementById('removeFile').addEventListener('click', this.removeFile.bind(this));
        
        // Fast mode toggle
        this.fastModeCheckbox.addEventListener('change', this.handleFastModeToggle.bind(this));
        
        // New analysis button
        this.newAnalysisBtn.addEventListener('click', this.resetForm.bind(this));
        
        // Prevent default form submission
        this.uploadForm.addEventListener('submit', (e) => e.preventDefault());
    }
    
    initializeGlassEffects() {
        // Add hover effects to cards
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', this.addGlowEffect.bind(this));
            card.addEventListener('mouseleave', this.removeGlowEffect.bind(this));
        });
        
        // Add parallax effect to background
        this.initializeParallax();
        
        // Add ripple effect to buttons
        this.initializeRippleEffect();
    }
    
    addGlowEffect(e) {
        const card = e.currentTarget;
        card.style.boxShadow = `
            0 20px 40px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.3),
            0 0 20px rgba(255, 255, 255, 0.2)
        `;
    }
    
    removeGlowEffect(e) {
        const card = e.currentTarget;
        card.style.boxShadow = `
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2)
        `;
    }
    
    initializeParallax() {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = document.querySelector('body::before');
            // Subtle parallax effect for background
        });
    }
    
    initializeRippleEffect() {
        const buttons = document.querySelectorAll('.btn-primary, .btn-success, .btn-secondary');
        buttons.forEach(button => {
            button.addEventListener('click', this.createRipple.bind(this));
        });
    }
    
    createRipple(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        // Add ripple styles
        ripple.style.position = 'absolute';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'rgba(255, 255, 255, 0.6)';
        ripple.style.transform = 'scale(0)';
        ripple.style.animation = 'ripple 0.6s ease-out';
        ripple.style.pointerEvents = 'none';
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    handleFastModeToggle() {
        const checkbox = this.fastModeCheckbox;
        const label = checkbox.closest('.checkbox-label');
        
        if (checkbox.checked) {
            label.style.background = 'rgba(0, 0, 0, 0.1)';
            label.style.color = '#000000';
        } else {
            label.style.background = 'rgba(255, 255, 255, 0.3)';
            label.style.color = 'inherit';
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadZone.classList.add('dragover');
        this.addUploadZoneGlow();
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('dragover');
        this.removeUploadZoneGlow();
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('dragover');
        this.removeUploadZoneGlow();
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    addUploadZoneGlow() {
        this.uploadZone.style.boxShadow = '0 0 30px rgba(255, 255, 255, 0.5), 0 10px 30px rgba(0, 0, 0, 0.1)';
    }
    
    removeUploadZoneGlow() {
        this.uploadZone.style.boxShadow = '';
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }
    
    processFile(file) {
        // File size validation
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            this.showNotification('File size must be less than 16MB', 'error');
            return;
        }
        
        // File type validation
        const allowedTypes = [
            'image/png', 'image/jpeg', 'image/jpg',
            'application/pdf', 'text/xml', 'application/xml',
            'application/vnd.visio', 'image/svg+xml'
        ];
        
        const allowedExtensions = ['.drawio', '.vsdx'];
        const isValidType = allowedTypes.includes(file.type) || 
                           allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValidType) {
            this.showNotification('Please upload a valid file type (PNG, JPG, PDF, XML, Draw.io, VSDX, SVG)', 'error');
            return;
        }
        
        // Quick pre-check for obvious AWS file names - STOP processing if detected
        if (!this.preCheckForNonAzureContent(file)) {
            // Clear the file input to prevent further processing
            this.fileInput.value = '';
            return;
        }
        
        this.currentFile = file;
        this.showFilePreview(file);
        this.submitBtn.style.display = 'block';
        this.submitBtn.classList.add('fade-in');
    }
    
    preCheckForNonAzureContent(file) {
        const fileName = file.name.toLowerCase();
        const awsIndicators = ['aws', 'amazon', 'ec2', 's3', 'lambda', 'cloudformation', 'cloudwatch'];
        const gcpIndicators = ['gcp', 'google-cloud', 'compute-engine', 'cloud-storage'];
        
        // Check filename for obvious non-Azure indicators
        if (awsIndicators.some(indicator => fileName.includes(indicator))) {
            this.showAzureOnlyModal('AWS');
            return false;
        }
        
        if (gcpIndicators.some(indicator => fileName.includes(indicator))) {
            this.showAzureOnlyModal('Google Cloud Platform');
            return false;
        }
        
        return true;
    }
    
    showAzureOnlyModal(detectedPlatform = 'Non-Azure') {
        const modal = this.createAzureOnlyModal(detectedPlatform);
        document.body.appendChild(modal);
        
        // Animate in
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.querySelector('.modal-content').style.transform = 'translateY(0) scale(1)';
        }, 10);
        
        // Auto remove after 8 seconds
        setTimeout(() => {
            this.closeAzureOnlyModal(modal);
        }, 8000);
    }
    
    createAzureOnlyModal(detectedPlatform) {
        const modal = document.createElement('div');
        modal.className = 'azure-only-modal';
        
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h3>Azure Architecture Only</h3>
                    <button class="modal-close" onclick="this.closest('.azure-only-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="platform-detected">
                        <strong>Detected Platform:</strong> ${detectedPlatform}
                    </div>
                    <p class="modal-message">
                        <strong>Digital Superman</strong> is specifically designed for <strong>Azure architecture diagrams</strong> only.
                    </p>
                    <div class="azure-info">
                        <h4><i class="fab fa-microsoft"></i> Digital Superman Supports Azure Only</h4>
                        <p class="azure-description">
                            Our AI agents are specifically trained to analyze and generate infrastructure code 
                            for <strong>Microsoft Azure</strong> services only.
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <div class="modal-actions">
                        <button class="btn-modal-primary" onclick="this.closest('.azure-only-modal').remove()">
                            <i class="fas fa-check"></i>
                            I Understand
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal styles
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        return modal;
    }
    
    closeAzureOnlyModal(modal) {
        modal.style.opacity = '0';
        modal.querySelector('.modal-content').style.transform = 'translateY(-20px) scale(0.95)';
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
    
    showFilePreview(file) {
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        this.filePreview.style.display = 'block';
        this.filePreview.classList.add('fade-in');
        
        // Add glass effect to file preview
        setTimeout(() => {
            this.filePreview.style.background = 'rgba(255, 255, 255, 0.6)';
            this.filePreview.style.backdropFilter = 'blur(15px)';
        }, 100);
    }
    
    removeFile() {
        this.currentFile = null;
        this.fileInput.value = '';
        this.filePreview.style.display = 'none';
        this.filePreview.classList.remove('fade-in');
        this.submitBtn.style.display = 'none';
        this.submitBtn.classList.remove('fade-in');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            border-radius: 12px;
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            font-size: 14px;
            font-weight: 500;
            max-width: 300px;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        if (type === 'error') {
            notification.style.background = 'rgba(255, 235, 238, 0.9)';
            notification.style.color = '#c62828';
            notification.style.borderColor = 'rgba(198, 40, 40, 0.2)';
        }
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.currentFile) {
            this.showNotification('Please select a file first', 'error');
            return;
        }
        
        const environment = document.getElementById('environment').value;
        if (!environment) {
            this.showNotification('Please select an environment', 'error');
            return;
        }
        
        // Double-check for non-Azure content before submitting
        if (!this.preCheckForNonAzureContent(this.currentFile)) {
            // Don't proceed with upload if pre-check fails
            return;
        }
        
        this.startProcessing();
        
        try {
            const formData = new FormData();
            formData.append('file', this.currentFile);
            formData.append('environment', environment);
            formData.append('fast_mode', this.fastModeCheckbox.checked);
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.handleProcessingSuccess(result);
            } else {
                // Check for specific Azure-only error
                if (result.error_type === 'non_azure_architecture') {
                    this.handleNonAzureError(result);
                } else {
                    this.handleProcessingError(result.message || 'Processing failed');
                }
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.handleProcessingError('Network error or server unavailable');
        }
    }
    
    startProcessing() {
        this.startTime = Date.now();
        this.submitBtn.style.display = 'none';
        this.progressSection.style.display = 'block';
        this.progressSection.classList.add('fade-in');
        
        // Enhanced glass effect for progress section
        this.progressSection.style.background = 'rgba(255, 255, 255, 0.3)';
        this.progressSection.style.backdropFilter = 'blur(20px)';
        
        // Simulate processing progress with enhanced animations
        this.simulateProgress();
    }
    
    simulateProgress() {
        const fastMode = this.fastModeCheckbox.checked;
        const totalTime = fastMode ? 15000 : 60000; // 15s or 60s
        const updateInterval = 300; // Update every 300ms for smoother animation
        const totalUpdates = totalTime / updateInterval;
        let currentUpdate = 0;
        
        const progressInterval = setInterval(() => {
            currentUpdate++;
            const progress = Math.min((currentUpdate / totalUpdates) * 100, 95);
            
            this.updateOverallProgress(progress);
            this.updateAgentProgress(progress);
            this.updateETA(totalTime, currentUpdate * updateInterval);
            
            if (currentUpdate >= totalUpdates) {
                clearInterval(progressInterval);
            }
        }, updateInterval);
        
        this.processingTimeout = progressInterval;
    }
    
    updateOverallProgress(percentage) {
        this.overallProgress.style.width = `${percentage}%`;
        this.overallPercentage.textContent = `${Math.round(percentage)}%`;
        
        // Add shimmer effect
        if (percentage < 100) {
            this.overallProgress.style.background = `
                linear-gradient(90deg, 
                    #000000 0%, 
                    #333333 50%, 
                    #000000 100%)
            `;
            this.overallProgress.style.backgroundSize = '200% 100%';
            this.overallProgress.style.animation = 'shimmer 2s infinite';
        }
    }
    
    updateAgentProgress(overallProgress) {
        // Agent 1: Architecture Analyzer (0-30%)
        if (overallProgress <= 30) {
            const agent1Progress = (overallProgress / 30) * 100;
            this.updateAgentStatus('agent1', 'processing', agent1Progress);
        } else {
            this.updateAgentStatus('agent1', 'complete', 100);
        }
        
        // Agent 2: Policy Checker (30-55%)
        if (overallProgress > 30 && overallProgress <= 55) {
            const agent2Progress = ((overallProgress - 30) / 25) * 100;
            this.updateAgentStatus('agent2', 'processing', agent2Progress);
        } else if (overallProgress > 55) {
            this.updateAgentStatus('agent2', 'complete', 100);
        }
        
        // Agent 3: Cost Optimizer (55-80%)
        if (overallProgress > 55 && overallProgress <= 80) {
            const agent3Progress = ((overallProgress - 55) / 25) * 100;
            this.updateAgentStatus('agent3', 'processing', agent3Progress);
        } else if (overallProgress > 80) {
            this.updateAgentStatus('agent3', 'complete', 100);
        }
        
        // Agent 4: Bicep Generator (80-100%)
        if (overallProgress > 80) {
            const agent4Progress = ((overallProgress - 80) / 20) * 100;
            this.updateAgentStatus('agent4', 'processing', agent4Progress);
        }
        
        if (overallProgress >= 95) {
            this.updateAgentStatus('agent4', 'complete', 100);
        }
    }
    
    updateAgentStatus(agentId, status, progress) {
        const agent = this.agents[agentId];
        if (!agent) return;
        
        // Update status with enhanced animations
        agent.status.className = `agent-status ${status}`;
        switch (status) {
            case 'waiting':
                agent.status.innerHTML = '<i class="fas fa-clock"></i>';
                break;
            case 'processing':
                agent.status.innerHTML = '<i class="fas fa-cog pulse"></i>';
                agent.element.style.background = 'rgba(255, 255, 255, 0.4)';
                break;
            case 'complete':
                agent.status.innerHTML = '<i class="fas fa-check"></i>';
                agent.element.style.background = 'rgba(255, 255, 255, 0.5)';
                this.addCompleteGlow(agent.element);
                break;
        }
        
        // Update progress bar with smooth animation
        agent.progress.style.width = `${progress}%`;
        
        if (progress === 100) {
            agent.progress.style.background = 'linear-gradient(90deg, #000000, #333333)';
            agent.progress.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.3)';
        }
    }
    
    addCompleteGlow(element) {
        element.style.boxShadow = '0 0 20px rgba(255, 255, 255, 0.4), 0 8px 25px rgba(0, 0, 0, 0.1)';
        setTimeout(() => {
            element.style.boxShadow = '';
        }, 2000);
    }
    
    updateETA(totalTime, elapsed) {
        const remaining = totalTime - elapsed;
        const minutes = Math.floor(remaining / 60000);
        const seconds = Math.floor((remaining % 60000) / 1000);
        
        if (remaining > 0) {
            this.progressETA.textContent = `ETA: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            this.progressETA.textContent = 'Finalizing...';
        }
    }
    
    handleProcessingSuccess(result) {
        clearInterval(this.processingTimeout);
        
        // Complete all progress bars with celebration effect
        this.updateOverallProgress(100);
        Object.keys(this.agents).forEach(agentId => {
            this.updateAgentStatus(agentId, 'complete', 100);
        });
        
        // Show success notification
        this.showNotification('Analysis completed successfully!', 'success');
        
        // Show results with enhanced animation
        setTimeout(() => {
            this.progressSection.style.display = 'none';
            this.resultsSection.style.display = 'block';
            this.resultsSection.classList.add('fade-in');
            
            // Enhanced glass effect for results
            this.resultsSection.style.background = 'rgba(255, 255, 255, 0.4)';
            this.resultsSection.style.backdropFilter = 'blur(25px)';
            
            if (result.download_url) {
                this.downloadBtn.style.display = 'inline-flex';
                this.downloadBtn.onclick = () => {
                    window.open(result.download_url, '_blank');
                    this.showNotification('Download started!', 'success');
                };
            }
        }, 1000);
    }
    
    handleNonAzureError(result) {
        clearInterval(this.processingTimeout);
        
        // Hide progress section
        this.progressSection.style.display = 'none';
        
        // Show detailed Azure-only modal with server-detected information
        const detectedPlatforms = result.detected_platforms || [];
        const nonAzureServices = result.non_azure_services || [];
        
        let detectedText = 'Non-Azure Services';
        if (detectedPlatforms.length > 0) {
            detectedText = detectedPlatforms.join(', ');
        }
        
        const modal = this.createDetailedAzureOnlyModal(detectedText, nonAzureServices, result.message);
        document.body.appendChild(modal);
        
        // Animate in
        setTimeout(() => {
            modal.style.opacity = '1';
            modal.querySelector('.modal-content').style.transform = 'translateY(0) scale(1)';
        }, 10);
        
        // Reset form after modal is shown
        setTimeout(() => {
            this.resetForm();
        }, 1000);
    }
    
    createDetailedAzureOnlyModal(detectedPlatform, nonAzureServices, serverMessage) {
        const modal = document.createElement('div');
        modal.className = 'azure-only-modal detailed';
        
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-icon error-icon">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <h3>Architecture Analysis Failed</h3>
                    <button class="modal-close" onclick="this.closest('.azure-only-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="platform-detected error">
                        <strong>Detected Platform:</strong> ${detectedPlatform}
                    </div>
                    
                    <div class="server-message">
                        ${serverMessage}
                    </div>
                    
                    <div class="azure-info">
                        <h4><i class="fab fa-microsoft"></i> Digital Superman Supports Azure Only</h4>
                        <p class="azure-description">
                            Our AI agents are specifically trained to analyze and generate infrastructure code 
                            for <strong>Microsoft Azure</strong> services only.
                        </p>
                    </div>
                </div>
                <div class="modal-footer">
                    <div class="modal-actions">
                        <button class="btn-modal-primary" onclick="this.closest('.azure-only-modal').remove()">
                            <i class="fas fa-check"></i>
                            I Understand
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal styles
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        return modal;
    }
    
    handleProcessingError(error) {
        clearInterval(this.processingTimeout);
        
        this.progressStatus.textContent = `Error: ${error}`;
        this.progressStatus.style.background = 'rgba(255, 235, 238, 0.9)';
        this.progressStatus.style.color = '#c62828';
        this.progressStatus.style.borderColor = 'rgba(198, 40, 40, 0.2)';
        
        this.showNotification(`Error: ${error}`, 'error');
        
        setTimeout(() => {
            this.resetForm();
        }, 3000);
    }
    
    resetForm() {
        // Reset all elements with smooth transitions
        this.removeFile();
        document.getElementById('environment').value = '';
        this.fastModeCheckbox.checked = false;
        this.handleFastModeToggle();
        
        // Hide sections with fade out
        this.progressSection.style.opacity = '0';
        this.resultsSection.style.opacity = '0';
        
        setTimeout(() => {
            this.progressSection.style.display = 'none';
            this.resultsSection.style.display = 'none';
            this.progressSection.style.opacity = '1';
            this.resultsSection.style.opacity = '1';
        }, 300);
        
        // Reset agent statuses
        Object.keys(this.agents).forEach(agentId => {
            this.updateAgentStatus(agentId, 'waiting', 0);
            this.agents[agentId].element.style.background = 'rgba(255, 255, 255, 0.3)';
        });
        
        // Reset progress
        this.updateOverallProgress(0);
        this.progressETA.textContent = 'Estimating time...';
        this.progressStatus.textContent = 'Initializing analysis...';
        this.progressStatus.style.background = 'rgba(255, 255, 255, 0.4)';
        this.progressStatus.style.color = '#333333';
        this.progressStatus.style.borderColor = 'rgba(255, 255, 255, 0.3)';
        
        // Clear timeouts
        if (this.processingTimeout) {
            clearInterval(this.processingTimeout);
            this.processingTimeout = null;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GlassyDigitalSupermanApp();
    
    // Add CSS for ripple effect
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        @keyframes shimmer {
            0% { background-position: -200px 0; }
            100% { background-position: calc(200px + 100%) 0; }
        }
    `;
    document.head.appendChild(style);
});

// Export for potential external use
window.GlassyDigitalSupermanApp = GlassyDigitalSupermanApp;
