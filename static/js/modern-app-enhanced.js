/**
 * Digital Superman - Modern Application JavaScript
 * Enhanced with 2025 Best Practices and Performance Optimizations
 */

class DigitalSupermanApp {
    constructor() {
        this.config = {
            maxFileSize: 16 * 1024 * 1024, // 16MB
            allowedExtensions: ['.png', '.jpg', '.jpeg', '.pdf', '.xml', '.drawio', '.vsdx', '.svg'],
            apiEndpoints: {
                upload: '/upload',
                download: '/download'
            },
            pollInterval: 1000,
            maxPollAttempts: 180 // 3 minutes
        };
        
        this.state = {
            isProcessing: false,
            currentFile: null,
            uploadProgress: 0,
            agents: {
                analyzer: { status: 'waiting', progress: 0 },
                policy: { status: 'waiting', progress: 0 },
                bicep: { status: 'waiting', progress: 0 }
            },
            pollAttempts: 0,
            results: null
        };
        
        this.elements = {};
        this.eventListeners = [];
        
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        this.cacheElements();
        this.bindEvents();
        this.setupFileUpload();
        this.setupModeToggle();
        this.updateUI();
    }

    /**
     * Cache DOM elements for better performance
     */
    cacheElements() {
        this.elements = {
            // Form elements
            uploadForm: document.getElementById('uploadForm'),
            fileInput: document.getElementById('fileInput'),
            uploadZone: document.getElementById('uploadZone'),
            environment: document.getElementById('environment'),
            fastMode: document.getElementById('fastMode'),
            
            // File preview
            filePreview: document.getElementById('filePreview'),
            fileName: document.getElementById('fileName'),
            fileSize: document.getElementById('fileSize'),
            removeFile: document.getElementById('removeFile'),
            
            // Form actions
            formActions: document.getElementById('formActions'),
            submitBtn: document.getElementById('submitBtn'),
            
            // Mode descriptions
            fastModeDesc: document.getElementById('fastModeDesc'),
            fullModeDesc: document.getElementById('fullModeDesc'),
            
            // Sections
            progressSection: document.getElementById('progressSection'),
            resultsSection: document.getElementById('resultsSection'),
            
            // Agent elements
            agent1: document.getElementById('agent1'),
            agent2: document.getElementById('agent2'),
            agent3: document.getElementById('agent3'),
            agent1Status: document.getElementById('agent1Status'),
            agent2Status: document.getElementById('agent2Status'),
            agent3Status: document.getElementById('agent3Status'),
            agent1Progress: document.getElementById('agent1Progress'),
            agent2Progress: document.getElementById('agent2Progress'),
            agent3Progress: document.getElementById('agent3Progress'),
            agent1ProgressText: document.getElementById('agent1ProgressText'),
            agent2ProgressText: document.getElementById('agent2ProgressText'),
            agent3ProgressText: document.getElementById('agent3ProgressText'),
            
            // Progress elements
            overallProgress: document.getElementById('overallProgress'),
            overallPercentage: document.getElementById('overallPercentage'),
            progressETA: document.getElementById('progressETA'),
            progressStatus: document.getElementById('progressStatus'),
            progressDescription: document.getElementById('progressDescription'),
            
            // Results elements
            resultsContent: document.getElementById('resultsContent'),
            downloadBtn: document.getElementById('downloadBtn'),
            newAnalysisBtn: document.getElementById('newAnalysisBtn')
        };
    }

    /**
     * Bind event listeners with proper cleanup
     */
    bindEvents() {
        // Form submission
        if (this.elements.uploadForm) {
            const formHandler = (e) => this.handleFormSubmit(e);
            this.elements.uploadForm.addEventListener('submit', formHandler);
            this.eventListeners.push(() => this.elements.uploadForm.removeEventListener('submit', formHandler));
        }

        // File input change
        if (this.elements.fileInput) {
            const fileHandler = (e) => this.handleFileSelect(e);
            this.elements.fileInput.addEventListener('change', fileHandler);
            this.eventListeners.push(() => this.elements.fileInput.removeEventListener('change', fileHandler));
        }

        // Upload zone interactions
        if (this.elements.uploadZone) {
            const clickHandler = () => this.elements.fileInput?.click();
            const dragoverHandler = (e) => this.handleDragOver(e);
            const dragleaveHandler = (e) => this.handleDragLeave(e);
            const dropHandler = (e) => this.handleDrop(e);
            const keyHandler = (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.elements.fileInput?.click(); } };

            this.elements.uploadZone.addEventListener('click', clickHandler);
            this.elements.uploadZone.addEventListener('dragover', dragoverHandler);
            this.elements.uploadZone.addEventListener('dragleave', dragleaveHandler);
            this.elements.uploadZone.addEventListener('drop', dropHandler);
            this.elements.uploadZone.addEventListener('keydown', keyHandler);

            this.eventListeners.push(() => {
                this.elements.uploadZone.removeEventListener('click', clickHandler);
                this.elements.uploadZone.removeEventListener('dragover', dragoverHandler);
                this.elements.uploadZone.removeEventListener('dragleave', dragleaveHandler);
                this.elements.uploadZone.removeEventListener('drop', dropHandler);
                this.elements.uploadZone.removeEventListener('keydown', keyHandler);
            });
        }

        // Remove file button
        if (this.elements.removeFile) {
            const removeHandler = () => this.removeFile();
            this.elements.removeFile.addEventListener('click', removeHandler);
            this.eventListeners.push(() => this.elements.removeFile.removeEventListener('click', removeHandler));
        }

        // Mode toggle
        if (this.elements.fastMode) {
            const modeHandler = () => this.handleModeToggle();
            this.elements.fastMode.addEventListener('change', modeHandler);
            this.eventListeners.push(() => this.elements.fastMode.removeEventListener('change', modeHandler));
        }

        // Download button
        if (this.elements.downloadBtn) {
            const downloadHandler = () => this.handleDownload();
            this.elements.downloadBtn.addEventListener('click', downloadHandler);
            this.eventListeners.push(() => this.elements.downloadBtn.removeEventListener('click', downloadHandler));
        }

        // New analysis button
        if (this.elements.newAnalysisBtn) {
            const newHandler = () => this.resetApplication();
            this.elements.newAnalysisBtn.addEventListener('click', newHandler);
            this.eventListeners.push(() => this.elements.newAnalysisBtn.removeEventListener('click', newHandler));
        }
    }

    /**
     * Setup file upload functionality
     */
    setupFileUpload() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
    }

    /**
     * Setup mode toggle functionality
     */
    setupModeToggle() {
        this.handleModeToggle();
    }

    /**
     * Handle mode toggle change
     */
    handleModeToggle() {
        if (!this.elements.fastMode || !this.elements.fastModeDesc || !this.elements.fullModeDesc) return;

        const isFastMode = this.elements.fastMode.checked;
        
        if (isFastMode) {
            this.elements.fastModeDesc.style.display = 'block';
            this.elements.fullModeDesc.style.display = 'none';
        } else {
            this.elements.fastModeDesc.style.display = 'none';
            this.elements.fullModeDesc.style.display = 'block';
        }
    }

    /**
     * Handle file selection
     */
    handleFileSelect(event) {
        const files = event.target.files;
        if (files && files.length > 0) {
            this.processFile(files[0]);
        }
    }

    /**
     * Handle drag over
     */
    handleDragOver(event) {
        event.preventDefault();
        if (this.elements.uploadZone && !this.state.isProcessing) {
            this.elements.uploadZone.classList.add('dragover');
        }
    }

    /**
     * Handle drag leave
     */
    handleDragLeave(event) {
        event.preventDefault();
        if (this.elements.uploadZone) {
            this.elements.uploadZone.classList.remove('dragover');
        }
    }

    /**
     * Handle file drop
     */
    handleDrop(event) {
        event.preventDefault();
        if (this.elements.uploadZone) {
            this.elements.uploadZone.classList.remove('dragover');
        }

        if (this.state.isProcessing) return;

        const files = event.dataTransfer.files;
        if (files && files.length > 0) {
            this.processFile(files[0]);
        }
    }

    /**
     * Process uploaded file
     */
    processFile(file) {
        // Validate file
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.showError(validation.message);
            return;
        }

        // Update state
        this.state.currentFile = file;

        // Update UI
        this.showFilePreview(file);
        this.updateUI();
    }

    /**
     * Validate file
     */
    validateFile(file) {
        // Check file size
        if (file.size > this.config.maxFileSize) {
            return {
                valid: false,
                message: `File size (${this.formatFileSize(file.size)}) exceeds maximum allowed size (${this.formatFileSize(this.config.maxFileSize)})`
            };
        }

        // Check file extension
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.config.allowedExtensions.includes(extension)) {
            return {
                valid: false,
                message: `File type not supported. Allowed types: ${this.config.allowedExtensions.join(', ')}`
            };
        }

        return { valid: true };
    }

    /**
     * Show file preview
     */
    showFilePreview(file) {
        if (!this.elements.filePreview || !this.elements.fileName || !this.elements.fileSize) return;

        this.elements.fileName.textContent = file.name;
        this.elements.fileSize.textContent = this.formatFileSize(file.size);
        this.elements.filePreview.style.display = 'block';
    }

    /**
     * Remove file
     */
    removeFile() {
        this.state.currentFile = null;
        
        if (this.elements.fileInput) {
            this.elements.fileInput.value = '';
        }
        
        if (this.elements.filePreview) {
            this.elements.filePreview.style.display = 'none';
        }
        
        this.updateUI();
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(event) {
        event.preventDefault();

        if (!this.state.currentFile) {
            this.showError('Please select a file to upload');
            return;
        }

        if (!this.elements.environment?.value) {
            this.showError('Please select an environment');
            return;
        }

        try {
            this.state.isProcessing = true;
            this.updateUI();
            
            await this.uploadFile();
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message || 'Upload failed. Please try again.');
            this.state.isProcessing = false;
            this.updateUI();
        }
    }

    /**
     * Upload file to server
     */
    async uploadFile() {
        const formData = new FormData();
        formData.append('file', this.state.currentFile);
        formData.append('environment', this.elements.environment.value);
        formData.append('fast_mode', this.elements.fastMode?.checked || false);

        try {
            this.showProgressSection();
            this.updateProgressStatus('Uploading file...', 10);

            const response = await fetch(this.config.apiEndpoints.upload, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Upload failed' }));
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            // Start polling for progress
            this.startProgressPolling(result.task_id || 'default');
            
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    /**
     * Start polling for progress updates
     */
    startProgressPolling(taskId) {
        this.state.pollAttempts = 0;
        this.pollProgress(taskId);
    }

    /**
     * Poll for progress updates
     */
    async pollProgress(taskId) {
        if (this.state.pollAttempts >= this.config.maxPollAttempts) {
            this.showError('Processing timeout. Please try again.');
            this.state.isProcessing = false;
            this.updateUI();
            return;
        }

        this.state.pollAttempts++;

        try {
            // Simulate progress updates (replace with actual API call)
            await this.simulateProgress();
            
            // Continue polling if not complete
            if (this.state.isProcessing) {
                setTimeout(() => this.pollProgress(taskId), this.config.pollInterval);
            }
        } catch (error) {
            console.error('Progress polling error:', error);
            this.showError('Failed to get progress updates');
            this.state.isProcessing = false;
            this.updateUI();
        }
    }

    /**
     * Simulate progress for demonstration
     */
    async simulateProgress() {
        const isFastMode = this.elements.fastMode?.checked || false;
        const totalSteps = isFastMode ? 20 : 60; // Fast mode: 20 seconds, Full mode: 60 seconds
        const currentStep = Math.min(this.state.pollAttempts, totalSteps);
        const progress = (currentStep / totalSteps) * 100;

        // Update overall progress
        this.updateProgressStatus(`Processing... (Step ${currentStep}/${totalSteps})`, progress);

        // Update agent progress
        if (currentStep <= 10) {
            // Agent 1: Architecture Analyzer
            const agent1Progress = Math.min((currentStep / 10) * 100, 100);
            this.updateAgentProgress('analyzer', agent1Progress < 100 ? 'processing' : 'complete', agent1Progress);
            
            if (agent1Progress >= 100) {
                this.updateAgentProgress('policy', 'processing', 0);
            }
        } else if (currentStep <= 20) {
            // Agent 2: Policy Checker (if not fast mode)
            this.updateAgentProgress('analyzer', 'complete', 100);
            
            if (!isFastMode) {
                const agent2Progress = Math.min(((currentStep - 10) / 10) * 100, 100);
                this.updateAgentProgress('policy', agent2Progress < 100 ? 'processing' : 'complete', agent2Progress);
                
                if (agent2Progress >= 100) {
                    this.updateAgentProgress('bicep', 'processing', 0);
                }
            } else {
                // In fast mode, skip to bicep generator
                this.updateAgentProgress('bicep', 'processing', 0);
            }
        } else {
            // Agent 3: Bicep Generator
            this.updateAgentProgress('analyzer', 'complete', 100);
            if (!isFastMode) {
                this.updateAgentProgress('policy', 'complete', 100);
            }
            
            const agent3Progress = Math.min(((currentStep - 20) / (totalSteps - 20)) * 100, 100);
            this.updateAgentProgress('bicep', agent3Progress < 100 ? 'processing' : 'complete', agent3Progress);
        }

        // Complete processing
        if (currentStep >= totalSteps) {
            this.completeProcessing();
        }
    }

    /**
     * Update agent progress
     */
    updateAgentProgress(agent, status, progress) {
        this.state.agents[agent] = { status, progress };

        const agentMap = {
            analyzer: '1',
            policy: '2',
            bicep: '3'
        };

        const agentNum = agentMap[agent];
        const statusElement = this.elements[`agent${agentNum}Status`];
        const progressElement = this.elements[`agent${agentNum}Progress`];
        const progressTextElement = this.elements[`agent${agentNum}ProgressText`];

        if (statusElement) {
            statusElement.className = `agent-status ${status}`;
            const statusText = status.charAt(0).toUpperCase() + status.slice(1);
            const statusIcon = status === 'processing' ? 'fa-cog fa-spin' : 
                              status === 'complete' ? 'fa-check' : 'fa-clock';
            statusElement.innerHTML = `<i class="fas ${statusIcon}" aria-hidden="true"></i><span>${statusText}</span>`;
        }

        if (progressElement) {
            progressElement.style.width = `${progress}%`;
        }

        if (progressTextElement) {
            progressTextElement.textContent = `${Math.round(progress)}%`;
        }
    }

    /**
     * Update overall progress
     */
    updateProgressStatus(message, progress) {
        this.state.uploadProgress = progress;

        if (this.elements.overallProgress) {
            this.elements.overallProgress.style.width = `${progress}%`;
        }

        if (this.elements.overallPercentage) {
            this.elements.overallPercentage.textContent = `${Math.round(progress)}%`;
        }

        if (this.elements.progressDescription) {
            this.elements.progressDescription.textContent = message;
        }

        // Update ETA
        if (this.elements.progressETA && progress > 0) {
            const remainingTime = Math.ceil((100 - progress) * (this.state.pollAttempts / progress));
            this.elements.progressETA.textContent = `~${remainingTime} seconds remaining`;
        }

        // Update status
        if (this.elements.progressStatus) {
            this.elements.progressStatus.innerHTML = `
                <div class="status-item active">
                    <i class="fas fa-cog fa-spin" aria-hidden="true"></i>
                    <span>${message}</span>
                </div>
            `;
        }
    }

    /**
     * Complete processing and show results
     */
    completeProcessing() {
        this.state.isProcessing = false;
        this.state.results = {
            downloadUrl: '/download/sample-package.zip',
            summary: 'Analysis completed successfully'
        };

        this.showResultsSection();
        this.updateUI();
    }

    /**
     * Show progress section
     */
    showProgressSection() {
        if (this.elements.progressSection) {
            this.elements.progressSection.style.display = 'block';
            this.elements.progressSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    /**
     * Show results section
     */
    showResultsSection() {
        if (this.elements.resultsSection) {
            this.elements.resultsSection.style.display = 'block';
            this.elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
        }

        if (this.elements.downloadBtn) {
            this.elements.downloadBtn.style.display = 'inline-flex';
        }

        if (this.elements.progressSection) {
            this.elements.progressSection.style.display = 'none';
        }
    }

    /**
     * Handle download
     */
    handleDownload() {
        if (this.state.results?.downloadUrl) {
            window.location.href = this.state.results.downloadUrl;
        }
    }

    /**
     * Reset application to initial state
     */
    resetApplication() {
        this.state = {
            isProcessing: false,
            currentFile: null,
            uploadProgress: 0,
            agents: {
                analyzer: { status: 'waiting', progress: 0 },
                policy: { status: 'waiting', progress: 0 },
                bicep: { status: 'waiting', progress: 0 }
            },
            pollAttempts: 0,
            results: null
        };

        this.removeFile();

        if (this.elements.environment) {
            this.elements.environment.value = '';
        }

        if (this.elements.fastMode) {
            this.elements.fastMode.checked = false;
        }

        if (this.elements.progressSection) {
            this.elements.progressSection.style.display = 'none';
        }

        if (this.elements.resultsSection) {
            this.elements.resultsSection.style.display = 'none';
        }

        // Reset agent displays
        ['1', '2', '3'].forEach(num => {
            this.updateAgentProgress(
                num === '1' ? 'analyzer' : num === '2' ? 'policy' : 'bicep',
                'waiting',
                0
            );
        });

        this.handleModeToggle();
        this.updateUI();

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Update UI based on current state
     */
    updateUI() {
        // Update form actions visibility
        if (this.elements.formActions) {
            this.elements.formActions.style.display = 
                (this.state.currentFile && !this.state.isProcessing) ? 'flex' : 'none';
        }

        // Update submit button state
        if (this.elements.submitBtn) {
            this.elements.submitBtn.disabled = this.state.isProcessing;
            if (this.state.isProcessing) {
                this.elements.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin" aria-hidden="true"></i><span>Processing...</span>';
            } else {
                this.elements.submitBtn.innerHTML = '<i class="fas fa-rocket" aria-hidden="true"></i><span>Start AI Processing</span>';
            }
        }

        // Update upload zone state
        if (this.elements.uploadZone) {
            if (this.state.isProcessing) {
                this.elements.uploadZone.style.pointerEvents = 'none';
                this.elements.uploadZone.style.opacity = '0.5';
            } else {
                this.elements.uploadZone.style.pointerEvents = 'auto';
                this.elements.uploadZone.style.opacity = '1';
            }
        }

        // Update form elements
        [this.elements.environment, this.elements.fastMode].forEach(element => {
            if (element) {
                element.disabled = this.state.isProcessing;
            }
        });
    }

    /**
     * Show error message
     */
    showError(message) {
        // Create a simple error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;
        errorDiv.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 18px;"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; margin-left: auto;">×</button>
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

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;

        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }

        return `${size.toFixed(unitIndex > 0 ? 1 : 0)} ${units[unitIndex]}`;
    }

    /**
     * Cleanup event listeners
     */
    destroy() {
        this.eventListeners.forEach(cleanup => cleanup());
        this.eventListeners = [];
    }
}

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.digitalSupermanApp = new DigitalSupermanApp();
    });
} else {
    window.digitalSupermanApp = new DigitalSupermanApp();
}

// Add CSS animation for error notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
// Cache bust 20250718-160805
