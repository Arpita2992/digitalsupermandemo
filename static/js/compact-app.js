// ================================================
// DIGITAL SUPERMAN - COMPACT BLACK & WHITE APP
// Minimal JavaScript for Streamlined Interface
// ================================================

class CompactDigitalSupermanApp {
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
        this.updateFastModeDescription();
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
        this.fastModeCheckbox.addEventListener('change', this.updateFastModeDescription.bind(this));
        
        // New analysis button
        this.newAnalysisBtn.addEventListener('click', this.resetForm.bind(this));
        
        // Prevent default form submission
        this.uploadForm.addEventListener('submit', (e) => e.preventDefault());
    }
    
    updateFastModeDescription() {
        // No description update needed in compact version
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadZone.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
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
            alert('File size must be less than 16MB');
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
            alert('Please upload a valid file type (PNG, JPG, PDF, XML, Draw.io, VSDX, SVG)');
            return;
        }
        
        this.currentFile = file;
        this.showFilePreview(file);
        this.submitBtn.style.display = 'block';
    }
    
    showFilePreview(file) {
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        this.filePreview.style.display = 'block';
        this.filePreview.classList.add('fade-in');
    }
    
    removeFile() {
        this.currentFile = null;
        this.fileInput.value = '';
        this.filePreview.style.display = 'none';
        this.submitBtn.style.display = 'none';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (!this.currentFile) {
            alert('Please select a file first');
            return;
        }
        
        const environment = document.getElementById('environment').value;
        if (!environment) {
            alert('Please select an environment');
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
                this.handleProcessingError(result.error || 'Processing failed');
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
        
        // Simulate processing progress
        this.simulateProgress();
    }
    
    simulateProgress() {
        const fastMode = this.fastModeCheckbox.checked;
        const totalTime = fastMode ? 15000 : 60000; // 15s or 60s
        const updateInterval = 500; // Update every 500ms
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
    }
    
    updateAgentProgress(overallProgress) {
        // Agent 1: Architecture Analyzer (0-40%)
        if (overallProgress <= 40) {
            const agent1Progress = (overallProgress / 40) * 100;
            this.updateAgentStatus('agent1', 'processing', agent1Progress);
        } else {
            this.updateAgentStatus('agent1', 'complete', 100);
        }
        
        // Agent 2: Policy Checker (40-70%)
        if (overallProgress > 40 && overallProgress <= 70) {
            const agent2Progress = ((overallProgress - 40) / 30) * 100;
            this.updateAgentStatus('agent2', 'processing', agent2Progress);
        } else if (overallProgress > 70) {
            this.updateAgentStatus('agent2', 'complete', 100);
        }
        
        // Agent 3: Bicep Generator (70-100%)
        if (overallProgress > 70) {
            const agent3Progress = ((overallProgress - 70) / 30) * 100;
            this.updateAgentStatus('agent3', 'processing', agent3Progress);
        }
        
        if (overallProgress >= 95) {
            this.updateAgentStatus('agent3', 'complete', 100);
        }
    }
    
    updateAgentStatus(agentId, status, progress) {
        const agent = this.agents[agentId];
        if (!agent) return;
        
        // Update status
        agent.status.className = `agent-status ${status}`;
        switch (status) {
            case 'waiting':
                agent.status.innerHTML = '<i class="fas fa-clock"></i>';
                break;
            case 'processing':
                agent.status.innerHTML = '<i class="fas fa-cog pulse"></i>';
                break;
            case 'complete':
                agent.status.innerHTML = '<i class="fas fa-check"></i>';
                break;
        }
        
        // Update progress bar
        agent.progress.style.width = `${progress}%`;
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
        
        // Complete all progress bars
        this.updateOverallProgress(100);
        Object.keys(this.agents).forEach(agentId => {
            this.updateAgentStatus(agentId, 'complete', 100);
        });
        
        // Show results
        setTimeout(() => {
            this.progressSection.style.display = 'none';
            this.resultsSection.style.display = 'block';
            this.resultsSection.classList.add('fade-in');
            
            if (result.download_url) {
                this.downloadBtn.style.display = 'inline-flex';
                this.downloadBtn.onclick = () => window.open(result.download_url, '_blank');
            }
        }, 1000);
    }
    
    handleProcessingError(error) {
        clearInterval(this.processingTimeout);
        
        this.progressStatus.textContent = `Error: ${error}`;
        this.progressStatus.style.background = '#ffebee';
        this.progressStatus.style.color = '#c62828';
        this.progressStatus.style.borderColor = '#c62828';
        
        setTimeout(() => {
            this.resetForm();
        }, 3000);
    }
    
    resetForm() {
        // Reset all elements
        this.removeFile();
        document.getElementById('environment').value = '';
        this.fastModeCheckbox.checked = false;
        
        // Hide sections
        this.progressSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        
        // Reset agent statuses
        Object.keys(this.agents).forEach(agentId => {
            this.updateAgentStatus(agentId, 'waiting', 0);
        });
        
        // Reset progress
        this.updateOverallProgress(0);
        this.progressETA.textContent = 'Estimating time...';
        this.progressStatus.textContent = 'Initializing analysis...';
        this.progressStatus.style.background = '#f0f0f0';
        this.progressStatus.style.color = '#333333';
        this.progressStatus.style.borderColor = '#000000';
        
        // Clear timeouts
        if (this.processingTimeout) {
            clearInterval(this.processingTimeout);
            this.processingTimeout = null;
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CompactDigitalSupermanApp();
});

// Export for potential external use
window.CompactDigitalSupermanApp = CompactDigitalSupermanApp;
