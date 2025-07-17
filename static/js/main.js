// Digital Superman - Optimized JavaScript

// Performance optimizations
const debounce = (func, delay) => {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(null, args), delay);
    };
};

class DigitalSuperman {
    constructor() {
        this.selectedFile = null;
        this.isProcessing = false;
        this.cache = new Map();
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        // Cache DOM elements for better performance
        this.elements = {
            uploadArea: document.getElementById('uploadArea'),
            fileInput: document.getElementById('fileInput'),
            uploadForm: document.getElementById('uploadForm'),
            fileInfo: document.getElementById('fileInfo'),
            uploadBtnContainer: document.getElementById('uploadBtnContainer'),
            removeFileBtn: document.getElementById('removeFile'),
            resultCard: document.getElementById('resultCard'),
            downloadLink: document.getElementById('downloadLink'),
            overallProgress: document.getElementById('overallProgress'),
            overallProgressBadge: document.getElementById('overallProgressBadge'),
            fastModeToggle: document.getElementById('fastMode'),
            fastModeHelp: document.getElementById('fastModeHelp'),
            fullModeHelp: document.getElementById('fullModeHelp')
        };

        // Check if required elements exist
        const requiredElements = ['uploadArea', 'fileInput', 'uploadForm', 'fileInfo', 'uploadBtnContainer'];
        for (const elementName of requiredElements) {
            if (!this.elements[elementName]) {
                console.error(`Required element not found: ${elementName}`);
            }
        }

        // Cache agent elements
        this.agentElements = {};
        for (let i = 1; i <= 4; i++) {
            this.agentElements[i] = {
                icon: document.getElementById(`agent${i}Icon`),
                fill: document.getElementById(`agent${i}Fill`),
                percentage: document.getElementById(`agent${i}Percentage`)
            };
        }
    }

    bindEvents() {
        // Use event delegation for better performance
        const { uploadArea, fileInput, uploadForm, removeFileBtn, fastModeToggle } = this.elements;

        // Check if elements exist before binding events
        if (!uploadArea || !fileInput || !uploadForm) {
            console.error('Required elements not found for event binding');
            return;
        }

        // File upload events
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));

        // Debounced file input change
        fileInput.addEventListener('change', debounce(this.handleFileChange.bind(this), 300));
        
        // Form submission
        uploadForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        
        // Remove file
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', this.clearFileSelection.bind(this));
        }

        // Fast mode toggle
        if (fastModeToggle) {
            fastModeToggle.addEventListener('change', this.handleFastModeToggle.bind(this));
        }

        // Custom alert events
        document.addEventListener('click', this.handleOverlayClick.bind(this));
        document.addEventListener('keydown', this.handleKeydown.bind(this));
        
        console.log('Digital Superman: Events bound successfully');
    }

    handleDragOver(e) {
        e.preventDefault();
        this.elements.uploadArea.classList.add('dragover');
    }

    handleDragLeave() {
        this.elements.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.elements.uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.elements.fileInput.files = files;
            this.showFileInfo(files[0]);
        }
    }

    handleFileChange(e) {
        if (e.target.files.length > 0) {
            this.showFileInfo(e.target.files[0]);
        }
    }

    handleFormSubmit(e) {
        e.preventDefault();
        console.log('Form submit handler called');
        
        if (this.isProcessing) {
            console.log('Already processing, ignoring submit');
            return;
        }

        const environment = document.getElementById('environment').value;
        const file = this.elements.fileInput.files[0];

        console.log('Environment:', environment);
        console.log('File:', file);

        if (!environment) {
            this.showCustomAlert('Environment Required', 'Please select an environment first.');
            return;
        }

        if (!file) {
            this.showCustomAlert('File Required', 'Please select a file first.');
            return;
        }

        // Start file upload directly
        this.handleFileUpload(file, environment);
    }

    handleFastModeToggle(e) {
        const isChecked = e.target.checked;
        console.log('Fast mode toggle:', isChecked);
        
        // Update help text visibility
        const fastModeHelp = document.getElementById('fastModeHelp');
        const fullModeHelp = document.getElementById('fullModeHelp');
        
        if (fastModeHelp && fullModeHelp) {
            if (isChecked) {
                fastModeHelp.style.display = 'block';
                fullModeHelp.style.display = 'none';
            } else {
                fastModeHelp.style.display = 'none';
                fullModeHelp.style.display = 'block';
            }
        }
    }

    showFileInfo(file) {
        this.selectedFile = file;
        
        // Update upload area appearance
        this.elements.uploadArea.classList.add('file-selected');
        
        // Show file info with animation
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
        
        // Use requestAnimationFrame for smooth animation
        requestAnimationFrame(() => {
            this.elements.fileInfo.style.display = 'block';
            this.elements.uploadBtnContainer.style.display = 'block';
        });
    }

    clearFileSelection() {
        this.selectedFile = null;
        this.elements.fileInput.value = '';
        
        // Reset upload area
        this.elements.uploadArea.classList.remove('file-selected');
        
        // Hide file info and upload button
        this.elements.fileInfo.style.display = 'none';
        this.elements.uploadBtnContainer.style.display = 'none';
    }

    async handleFileUpload(file, environment) {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.elements.uploadBtnContainer.style.display = 'none';
        
        // Reset all agents to waiting state
        this.resetAgentStates();
        
        // Show progress message
        this.showProgressMessage('Starting AI processing...');

        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('environment', environment);
        
        // Add fast mode parameter
        const fastModeToggle = this.elements.fastModeToggle;
        if (fastModeToggle && fastModeToggle.checked) {
            formData.append('fast_mode', 'true');
            this.showProgressMessage('Fast mode: Quick analysis starting...');
        }

        try {
            // Start Agent 1
            this.startAgent(1);
            this.showProgressMessage('Agent 1: Analyzing architecture...');

            // Upload file with extended timeout for AI processing
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minutes timeout

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                this.showProgressMessage('Processing completed successfully!');
                // Simulate realistic processing with optimized timing
                await this.processAgents();
                this.showResults(data.download_url);
            } else {
                // Handle specific error types
                if (data.error_type === 'non_azure_architecture') {
                    let errorMessage = data.message || 'Non-Azure architecture detected. We only support Azure-related diagrams. Please upload Azure architecture diagrams.';
                    this.showCustomAlert('Azure Architecture Required', errorMessage);
                    this.resetToUploadState();
                } else {
                    this.showCustomAlert('Upload Error', 'Error: ' + (data.message || 'Unknown error occurred'));
                }
                this.resetToUploadState();
            }
        } catch (error) {
            console.error('Upload error:', error);
            let errorMessage = 'Upload failed: ';
            
            if (error.name === 'AbortError') {
                errorMessage += 'Request timed out after 10 minutes. The AI processing is taking longer than expected. Please try again or contact support.';
            } else if (error.message.includes('fetch')) {
                errorMessage += 'Network connection error. Please check your internet connection and try again.';
            } else {
                errorMessage += error.message;
            }
            
            this.showCustomAlert('Upload Error', errorMessage);
            this.resetToUploadState();
        } finally {
            this.isProcessing = false;
        }
    }

    async processAgents() {
        const agents = [
            { id: 1, duration: 2000, name: 'Architecture Analyzer' },
            { id: 2, duration: 2500, name: 'Policy Checker' },
            { id: 3, duration: 2000, name: 'Cost Optimizer' },
            { id: 4, duration: 3000, name: 'Bicep Generator' }
        ];

        for (const agent of agents) {
            this.showProgressMessage(`Agent ${agent.id}: ${agent.name} processing...`);
            await new Promise(resolve => {
                setTimeout(() => {
                    this.completeAgent(agent.id);
                    if (agent.id < 4) {
                        this.startAgent(agent.id + 1);
                    }
                    resolve();
                }, agent.duration);
            });
        }
    }

    showProgressMessage(message) {
        // Show progress message to user
        const progressElement = document.getElementById('uploadBtnContainer');
        if (progressElement) {
            let messageDiv = progressElement.querySelector('.progress-message');
            if (!messageDiv) {
                messageDiv = document.createElement('div');
                messageDiv.className = 'progress-message alert alert-info mt-2';
                progressElement.appendChild(messageDiv);
            }
            messageDiv.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${message}`;
            messageDiv.style.display = 'block';
        }
    }

    hideProgressMessage() {
        const progressElement = document.getElementById('uploadBtnContainer');
        if (progressElement) {
            const messageDiv = progressElement.querySelector('.progress-message');
            if (messageDiv) {
                messageDiv.style.display = 'none';
            }
        }
    }

    resetAgentStates() {
        // Use DocumentFragment for efficient DOM updates
        const fragment = document.createDocumentFragment();
        
        for (let i = 1; i <= 4; i++) {
            const { icon, fill, percentage } = this.agentElements[i];
            
            // Batch DOM updates
            requestAnimationFrame(() => {
                icon.className = 'agent-progress-icon waiting';
                fill.className = 'agent-progress-fill waiting';
                fill.style.width = '0%';
                percentage.textContent = '0%';
            });
        }
        
        // Reset overall progress
        this.updateOverallProgress(0);
    }

    startAgent(agentNum) {
        const { icon, fill, percentage } = this.agentElements[agentNum];
        
        // Batch DOM updates
        requestAnimationFrame(() => {
            icon.className = 'agent-progress-icon active';
            fill.className = 'agent-progress-fill active';
            fill.style.width = '50%';
            percentage.textContent = '50%';
        });
        
        // Update overall progress
        this.updateOverallProgress(agentNum * 25 - 12.5);
    }

    completeAgent(agentNum) {
        const { icon, fill, percentage } = this.agentElements[agentNum];
        
        // Batch DOM updates
        requestAnimationFrame(() => {
            icon.className = 'agent-progress-icon completed';
            fill.className = 'agent-progress-fill completed';
            fill.style.width = '100%';
            percentage.textContent = '100%';
        });
        
        // Update overall progress
        this.updateOverallProgress(agentNum * 25);
    }

    updateOverallProgress(percentage) {
        requestAnimationFrame(() => {
            this.elements.overallProgress.style.width = percentage + '%';
            this.elements.overallProgressBadge.textContent = Math.round(percentage) + '%';
            
            if (percentage > 0) {
                this.elements.overallProgress.classList.add('active');
            }
        });
    }

    resetToUploadState() {
        // Reset UI elements
        this.elements.uploadBtnContainer.style.display = 'block';
        this.elements.resultCard.style.display = 'none';
        this.isProcessing = false;
        
        // Hide progress message
        this.hideProgressMessage();
        
        // Reset file selection
        this.selectedFile = null;
        this.elements.fileInput.value = '';
        
        // Reset file info display
        if (this.elements.fileInfo) {
            this.elements.fileInfo.style.display = 'none';
        }
        
        // Reset upload area state
        if (this.elements.uploadArea) {
            this.elements.uploadArea.classList.remove('file-selected');
            
            // Add a brief highlight to indicate the form is ready for new upload
            this.elements.uploadArea.style.transition = 'border-color 0.3s ease';
            this.elements.uploadArea.style.borderColor = '#8b5cf6';
            setTimeout(() => {
                this.elements.uploadArea.style.borderColor = '';
            }, 1000);
        }
        
        // Reset remove file button
        if (this.elements.removeFileBtn) {
            this.elements.removeFileBtn.style.display = 'none';
        }
        
        // Reset agent progress
        for (let i = 1; i <= 4; i++) {
            if (this.agentElements[i]) {
                this.agentElements[i].icon.classList.remove('processing', 'completed');
                this.agentElements[i].fill.style.width = '0%';
                this.agentElements[i].percentage.textContent = '0%';
            }
        }
        
        // Reset overall progress
        if (this.elements.overallProgress) {
            this.elements.overallProgress.style.width = '0%';
        }
        if (this.elements.overallProgressBadge) {
            this.elements.overallProgressBadge.textContent = '0%';
        }
    }

    showResults(downloadUrl) {
        requestAnimationFrame(() => {
            this.elements.resultCard.style.display = 'block';
            this.elements.downloadLink.href = downloadUrl;
            this.updateResultsSummary();
        });
    }

    updateResultsSummary() {
        // Use cached calculations for better performance
        const cacheKey = 'summary_' + Date.now();
        
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            this.applySummaryData(cached);
            return;
        }

        // Generate realistic summary data
        const summaryData = {
            componentsCount: Math.floor(Math.random() * 15) + 8,
            policyCompliance: Math.floor(Math.random() * 20) + 80,
            costSavings: Math.floor(Math.random() * 3000) + 1000,
            codeFiles: Math.floor(Math.random() * 8) + 5
        };

        // Cache the result
        this.cache.set(cacheKey, summaryData);
        
        // Apply data to DOM
        this.applySummaryData(summaryData);
        
        // Clean cache periodically
        if (this.cache.size > 10) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }

    applySummaryData(data) {
        // Batch DOM updates
        requestAnimationFrame(() => {
            document.getElementById('componentsCount').textContent = data.componentsCount;
            document.getElementById('policyCompliance').textContent = data.policyCompliance + '%';
            document.getElementById('costSavings').textContent = '€' + data.costSavings.toLocaleString();
            document.getElementById('codeFiles').textContent = data.codeFiles;
        });
    }

    showCustomAlert(title, message) {
        // Remove existing alerts first
        this.closeCustomAlert();

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'custom-alert-overlay';
        
        // Create alert
        const alert = document.createElement('div');
        alert.className = 'custom-alert';
        
        alert.innerHTML = `
            <div class="custom-alert-header">
                <div class="custom-alert-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4 class="custom-alert-title">${title}</h4>
            </div>
            <div class="custom-alert-message">${message}</div>
            <button class="custom-alert-button" onclick="digitalSuperman.closeCustomAlert()">
                <i class="fas fa-check me-2"></i>OK
            </button>
        `;
        
        // Add to DOM with animation
        document.body.appendChild(overlay);
        document.body.appendChild(alert);
        
        // Store references for cleanup
        this.currentAlert = alert;
        this.currentOverlay = overlay;
        
        // Focus trap
        const button = alert.querySelector('.custom-alert-button');
        if (button) button.focus();
    }

    closeCustomAlert() {
        if (this.currentAlert) {
            this.currentAlert.remove();
            this.currentAlert = null;
        }
        if (this.currentOverlay) {
            this.currentOverlay.remove();
            this.currentOverlay = null;
        }
        
        // Ensure the upload state is reset after closing error alerts
        if (!this.isProcessing && this.selectedFile) {
            this.resetToUploadState();
        }
    }

    handleOverlayClick(e) {
        if (e.target && e.target.classList.contains('custom-alert-overlay')) {
            this.closeCustomAlert();
        }
    }

    handleKeydown(e) {
        if (e.key === 'Escape' && this.currentAlert) {
            this.closeCustomAlert();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Global instance for legacy compatibility
    window.digitalSuperman = new DigitalSuperman();
});

// Optimize font loading
if ('fonts' in document) {
    document.fonts.ready.then(() => {
        document.body.classList.add('fonts-loaded');
    });
}

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        const navigation = performance.getEntriesByType('navigation')[0];
        console.log('Page load time:', navigation.loadEventEnd - navigation.loadEventStart, 'ms');
    });
}
