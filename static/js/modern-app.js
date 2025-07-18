/**
 * High-Performance JavaScript for Digital Superman
 * Optimized for speed and responsiveness
 */

// Performance optimization: Use requestAnimationFrame for smooth animations
const RAF = window.requestAnimationFrame || window.webkitRequestAnimationFrame;

// Debounce utility for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle utility for scroll events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Modern event system with passive listeners for better performance
class EventManager {
    constructor() {
        this.events = new Map();
    }

    on(element, event, handler, options = { passive: true }) {
        element.addEventListener(event, handler, options);
        
        if (!this.events.has(element)) {
            this.events.set(element, new Map());
        }
        
        const elementEvents = this.events.get(element);
        if (!elementEvents.has(event)) {
            elementEvents.set(event, new Set());
        }
        
        elementEvents.get(event).add(handler);
    }

    off(element, event, handler) {
        element.removeEventListener(event, handler);
        
        const elementEvents = this.events.get(element);
        if (elementEvents && elementEvents.has(event)) {
            elementEvents.get(event).delete(handler);
        }
    }

    cleanup() {
        for (const [element, events] of this.events) {
            for (const [eventName, handlers] of events) {
                for (const handler of handlers) {
                    element.removeEventListener(eventName, handler);
                }
            }
        }
        this.events.clear();
    }
}

// High-performance upload manager
class UploadManager {
    constructor() {
        this.eventManager = new EventManager();
        this.selectedFile = null;
        this.maxFileSize = 16 * 1024 * 1024; // 16MB
        this.allowedTypes = [
            'image/png', 'image/jpeg', 'image/jpg',
            'application/pdf', 'text/xml', 'application/xml',
            'image/svg+xml'
        ];
        
        this.init();
    }

    init() {
        // Cache DOM elements
        this.elements = {
            uploadArea: document.getElementById('uploadArea'),
            fileInput: document.getElementById('fileInput'),
            fileInfo: document.getElementById('fileInfo'),
            fileName: document.getElementById('fileName'),
            fileSize: document.getElementById('fileSize'),
            removeFile: document.getElementById('removeFile'),
            uploadBtnContainer: document.getElementById('uploadBtnContainer'),
            uploadForm: document.getElementById('uploadForm')
        };

        this.setupEventListeners();
        this.setupFileValidation();
        this.setupModeToggle();
    }

    setupEventListeners() {
        const { uploadArea, fileInput, removeFile, uploadForm } = this.elements;

        // High-performance drag and drop
        this.eventManager.on(uploadArea, 'click', () => fileInput.click());
        this.eventManager.on(fileInput, 'change', (e) => this.handleFileSelect(e));
        this.eventManager.on(removeFile, 'click', () => this.removeFile());

        // Optimized drag events with throttling
        const dragEvents = ['dragenter', 'dragover', 'dragleave', 'drop'];
        dragEvents.forEach(eventName => {
            this.eventManager.on(uploadArea, eventName, throttle((e) => {
                e.preventDefault();
                e.stopPropagation();
            }, 16)); // ~60fps
        });

        this.eventManager.on(uploadArea, 'dragover', () => {
            uploadArea.classList.add('dragover');
        });

        this.eventManager.on(uploadArea, 'dragleave', (e) => {
            if (!uploadArea.contains(e.relatedTarget)) {
                uploadArea.classList.remove('dragover');
            }
        });

        this.eventManager.on(uploadArea, 'drop', (e) => {
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });

        // Form submission with loading state
        this.eventManager.on(uploadForm, 'submit', (e) => this.handleSubmit(e));
    }

    setupFileValidation() {
        // Pre-compile validation patterns for performance
        this.validationPatterns = {
            extensions: /\.(png|jpe?g|pdf|xml|drawio|vsdx|svg)$/i,
            imageTypes: /^image\/(png|jpe?g|svg\+xml)$/,
            documentTypes: /^(application\/(pdf|xml)|text\/xml)$/
        };
    }

    setupModeToggle() {
        const fastModeToggle = document.getElementById('fastMode');
        const fastModeHelp = document.getElementById('fastModeHelp');
        const fullModeHelp = document.getElementById('fullModeHelp');

        if (fastModeToggle) {
            this.eventManager.on(fastModeToggle, 'change', () => {
                if (fastModeToggle.checked) {
                    fastModeHelp.style.display = 'block';
                    fullModeHelp.style.display = 'none';
                } else {
                    fastModeHelp.style.display = 'none';
                    fullModeHelp.style.display = 'block';
                }
            });
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        // Fast validation
        if (!this.validateFile(file)) {
            return;
        }

        this.selectedFile = file;
        this.displayFileInfo(file);
        this.showUploadButton();
    }

    validateFile(file) {
        // Size validation
        if (file.size > this.maxFileSize) {
            this.showError(`File size must be less than ${this.maxFileSize / (1024 * 1024)}MB`);
            return false;
        }

        // Type validation using pre-compiled patterns
        const isValidExtension = this.validationPatterns.extensions.test(file.name);
        const isValidType = this.allowedTypes.includes(file.type) || 
                           this.validationPatterns.imageTypes.test(file.type) ||
                           this.validationPatterns.documentTypes.test(file.type);

        if (!isValidExtension || !isValidType) {
            this.showError('Please select a valid file type (PNG, JPG, PDF, XML, Draw.io, VSDX, SVG)');
            return false;
        }

        return true;
    }

    displayFileInfo(file) {
        const { fileInfo, fileName, fileSize } = this.elements;
        
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);
        
        // Smooth show animation
        RAF(() => {
            fileInfo.style.display = 'block';
            fileInfo.style.opacity = '0';
            fileInfo.style.transform = 'translateY(-10px)';
            
            RAF(() => {
                fileInfo.style.transition = 'all 0.3s ease';
                fileInfo.style.opacity = '1';
                fileInfo.style.transform = 'translateY(0)';
            });
        });
    }

    showUploadButton() {
        const { uploadBtnContainer } = this.elements;
        
        RAF(() => {
            uploadBtnContainer.style.display = 'block';
            uploadBtnContainer.style.opacity = '0';
            uploadBtnContainer.style.transform = 'scale(0.9)';
            
            RAF(() => {
                uploadBtnContainer.style.transition = 'all 0.3s ease';
                uploadBtnContainer.style.opacity = '1';
                uploadBtnContainer.style.transform = 'scale(1)';
            });
        });
    }

    removeFile() {
        const { fileInfo, uploadBtnContainer, fileInput } = this.elements;
        
        this.selectedFile = null;
        fileInput.value = '';
        
        // Smooth hide animation
        const hideElements = [fileInfo, uploadBtnContainer];
        hideElements.forEach(element => {
            element.style.transition = 'all 0.2s ease';
            element.style.opacity = '0';
            element.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                element.style.display = 'none';
            }, 200);
        });
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    showError(message) {
        // Create error toast with better UX
        const toast = document.createElement('div');
        toast.className = 'error-toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--danger);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            z-index: 10000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            font-weight: 600;
        `;
        
        document.body.appendChild(toast);
        
        RAF(() => {
            toast.style.transform = 'translateX(0)';
        });
        
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    async handleSubmit(event) {
        event.preventDefault();
        
        if (!this.selectedFile) {
            this.showError('Please select a file first');
            return;
        }

        // Show processing state
        this.showProcessing();
        
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        
        const fastMode = document.getElementById('fastMode');
        if (fastMode && fastMode.checked) {
            formData.append('fast_mode', 'true');
        }

        try {
            const response = await this.submitWithProgress(formData);
            
            if (response.success) {
                this.showResults(response);
            } else {
                throw new Error(response.message || 'Processing failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message || 'An error occurred during processing');
            this.hideProcessing();
        }
    }

    async submitWithProgress(formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            // Progress tracking
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateUploadProgress(percentComplete);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (e) {
                        reject(new Error('Invalid response format'));
                    }
                } else {
                    reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Network error occurred'));
            });

            xhr.addEventListener('timeout', () => {
                reject(new Error('Request timed out'));
            });

            xhr.timeout = 120000; // 2 minutes timeout
            xhr.open('POST', '/upload');
            xhr.send(formData);
        });
    }

    showProcessing() {
        const processingHtml = `
            <div class="processing-container" id="processingContainer">
                <div class="processing-spinner"></div>
                <h4>Processing Your Architecture</h4>
                <p class="text-muted">AI agents are analyzing your diagram...</p>
                <div class="upload-progress-bar">
                    <div class="upload-progress-fill" id="uploadProgressFill"></div>
                </div>
                <div class="upload-progress-text" id="uploadProgressText">Uploading...</div>
            </div>
        `;
        
        const mainContainer = document.querySelector('.main-container');
        mainContainer.insertAdjacentHTML('beforeend', processingHtml);
        
        // Smooth show animation
        RAF(() => {
            const container = document.getElementById('processingContainer');
            container.style.display = 'block';
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
            
            RAF(() => {
                container.style.transition = 'all 0.4s ease';
                container.style.opacity = '1';
                container.style.transform = 'translateY(0)';
            });
        });

        // Start agent monitoring
        this.startAgentMonitoring();
    }

    updateUploadProgress(percent) {
        const progressFill = document.getElementById('uploadProgressFill');
        const progressText = document.getElementById('uploadProgressText');
        
        if (progressFill && progressText) {
            progressFill.style.width = `${percent}%`;
            progressText.textContent = `Uploading... ${Math.round(percent)}%`;
            
            if (percent >= 100) {
                progressText.textContent = 'Upload complete, processing...';
            }
        }
    }

    startAgentMonitoring() {
        // Simulate agent progress for better UX
        const agents = ['agent1', 'agent2', 'agent3'];
        let currentAgent = 0;
        
        const updateAgentProgress = () => {
            if (currentAgent < agents.length) {
                const agentId = agents[currentAgent];
                const icon = document.getElementById(`${agentId}Icon`);
                const fill = document.getElementById(`${agentId}Fill`);
                const percentage = document.getElementById(`${agentId}Percentage`);
                
                if (icon && fill && percentage) {
                    // Set to processing state
                    icon.className = 'agent-progress-icon processing';
                    fill.className = 'agent-progress-fill processing';
                    
                    // Animate progress
                    let progress = 0;
                    const progressInterval = setInterval(() => {
                        progress += Math.random() * 15;
                        if (progress > 100) progress = 100;
                        
                        fill.style.width = `${progress}%`;
                        percentage.textContent = `${Math.round(progress)}%`;
                        
                        if (progress >= 100) {
                            clearInterval(progressInterval);
                            icon.className = 'agent-progress-icon completed';
                            fill.className = 'agent-progress-fill completed';
                            currentAgent++;
                            setTimeout(updateAgentProgress, 500);
                        }
                    }, 200);
                }
            }
        };
        
        setTimeout(updateAgentProgress, 1000);
    }

    showResults(response) {
        const processingContainer = document.getElementById('processingContainer');
        if (processingContainer) {
            processingContainer.remove();
        }

        const resultsHtml = `
            <div class="results-container glass-card" id="resultsContainer">
                <div class="card-header">
                    <div class="card-icon success-icon">
                        <i class="fas fa-check"></i>
                    </div>
                    <div>
                        <h3 class="card-title">Processing Complete!</h3>
                        <p class="card-subtitle">Your infrastructure code is ready</p>
                    </div>
                </div>
                <div class="text-center">
                    <a href="${response.download_url}" class="download-btn">
                        <i class="fas fa-download"></i>
                        Download Infrastructure Package
                    </a>
                </div>
                <div class="mt-3 small text-muted text-center">
                    Package includes Bicep templates, Azure DevOps pipelines, and documentation
                </div>
            </div>
        `;
        
        const mainContainer = document.querySelector('.main-container');
        mainContainer.insertAdjacentHTML('beforeend', resultsHtml);
        
        // Smooth show animation
        RAF(() => {
            const container = document.getElementById('resultsContainer');
            container.style.display = 'block';
            container.style.opacity = '0';
            container.style.transform = 'scale(0.9)';
            
            RAF(() => {
                container.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                container.style.opacity = '1';
                container.style.transform = 'scale(1)';
            });
        });

        // Add success icon style
        const style = document.createElement('style');
        style.textContent = `
            .success-icon {
                background: linear-gradient(135deg, var(--success), #38a169);
                color: white;
            }
        `;
        document.head.appendChild(style);
    }

    hideProcessing() {
        const processingContainer = document.getElementById('processingContainer');
        if (processingContainer) {
            processingContainer.style.transition = 'all 0.3s ease';
            processingContainer.style.opacity = '0';
            processingContainer.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                processingContainer.remove();
            }, 300);
        }
    }

    cleanup() {
        this.eventManager.cleanup();
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoad: 0,
            firstContentfulPaint: 0,
            domContentLoaded: 0
        };
        
        this.init();
    }

    init() {
        // Page load timing
        window.addEventListener('load', () => {
            this.metrics.pageLoad = performance.now();
        });

        // DOM content loaded timing
        document.addEventListener('DOMContentLoaded', () => {
            this.metrics.domContentLoaded = performance.now();
        });

        // First contentful paint (if supported)
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.name === 'first-contentful-paint') {
                        this.metrics.firstContentfulPaint = entry.startTime;
                    }
                }
            });
            
            try {
                observer.observe({ entryTypes: ['paint'] });
            } catch (e) {
                // Silently fail if not supported
            }
        }
    }

    getMetrics() {
        return { ...this.metrics };
    }

    logMetrics() {
        console.log('Performance Metrics:', this.getMetrics());
    }
}

// Intersection Observer for lazy loading and animations
class AnimationManager {
    constructor() {
        this.observers = new Map();
        this.init();
    }

    init() {
        // Create intersection observer for fade-in animations
        const fadeObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-visible');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '20px'
        });

        // Observe elements with fade-in class
        document.querySelectorAll('.fade-in').forEach(el => {
            fadeObserver.observe(el);
        });

        this.observers.set('fade', fadeObserver);
    }

    cleanup() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
    }
}

// Initialize application when DOM is ready
let uploadManager;
let performanceMonitor;
let animationManager;

function initializeApp() {
    try {
        uploadManager = new UploadManager();
        performanceMonitor = new PerformanceMonitor();
        animationManager = new AnimationManager();
        
        // Log performance metrics after a delay
        setTimeout(() => {
            performanceMonitor.logMetrics();
        }, 2000);
        
    } catch (error) {
        console.error('Error initializing app:', error);
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (uploadManager) uploadManager.cleanup();
    if (animationManager) animationManager.cleanup();
});

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Add fade-in styles
const fadeStyles = document.createElement('style');
fadeStyles.textContent = `
    .fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .fade-in-visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .upload-progress-bar {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .upload-progress-fill {
        height: 100%;
        width: 0%;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .upload-progress-text {
        color: var(--text-secondary);
        font-size: 0.9rem;
        text-align: center;
    }
    
    .error-toast {
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
    }
`;
document.head.appendChild(fadeStyles);
