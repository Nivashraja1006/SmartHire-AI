/**
 * Premium AI Recruitment Platform - JavaScript
 * Handles animations, interactions, and dynamic UI updates
 */

// ============================================
// GSAP Animation Library Integration
// ============================================

if (typeof gsap !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

/**
 * Initialize all animations on page load
 */
function initializeAnimations() {
    // Animate elements on scroll
    animateOnScroll('.slide-up', { y: 20, opacity: 0 });
    animateOnScroll('.slide-down', { y: -20, opacity: 0 });
    animateOnScroll('.fade-in', { opacity: 0 });
    animateOnScroll('.bounce-in', { scale: 0.3, opacity: 0 });

    // Stagger animations for cards
    animateCardStagger('.card', 0.1);
    animateCardStagger('.feature-card', 0.1);
}

/**
 * Animate elements when they scroll into view
 */
function animateOnScroll(selector, fromVars = {}) {
    if (typeof gsap === 'undefined') return;

    document.querySelectorAll(selector).forEach((element, index) => {
        gsap.fromTo(
            element,
            { ...fromVars, delay: index * 0.1 },
            {
                opacity: 1,
                y: 0,
                x: 0,
                scale: 1,
                duration: 0.8,
                ease: 'power2.out',
                scrollTrigger: {
                    trigger: element,
                    start: 'top 80%',
                    end: 'top 20%',
                    toggleActions: 'play none none none',
                },
            }
        );
    });
}

/**
 * Stagger animations for multiple elements
 */
function animateCardStagger(selector, delay = 0.1) {
    if (typeof gsap === 'undefined') return;

    gsap.to(selector, {
        duration: 0.6,
        opacity: 1,
        y: 0,
        stagger: delay,
        ease: 'power2.out',
    });
}

// ============================================
// DOM READY & INIT
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeAnimations();
    initializeFormValidation();
    initializeModals();
    setupEventListeners();
    setupRealtimeUpdates();
    initializeAmbientCanvas();
    initializeLiveCharts();
    initializePageMotion();
    initializeCommandCenter();
    initializePricingToggle();
});

function initializeAmbientCanvas() {
    const canvas = document.getElementById('ambient-canvas');
    if (!canvas) return;
    const context = canvas.getContext('2d');
    const particles = Array.from({ length: 58 }, (_, index) => ({ x: Math.random(), y: Math.random(), radius: 0.7 + Math.random() * 1.7, speed: 0.000018 + Math.random() * 0.000035, phase: index * 1.7 }));
    const streaks = Array.from({ length: 8 }, (_, index) => ({ y: (index + 1) / 9, length: 80 + Math.random() * 180, speed: 0.000025 + Math.random() * 0.000025, offset: Math.random() }));
    let width = 0;
    let height = 0;
    let animationFrame;
    let pointerX = 0;
    let pointerY = 0;

    function resize() {
        const ratio = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
    }
    function draw(time) {
        context.clearRect(0, 0, width, height);
        const lightMode = document.documentElement.dataset.theme === 'light';
        const opacity = lightMode ? 0.32 : 1;
        const driftX = pointerX * 14;
        const driftY = pointerY * 10;
        const wave = context.createLinearGradient(0, height * .15, width, height * .85);
        wave.addColorStop(0, `rgba(30, 58, 138, ${.12 * opacity})`);
        wave.addColorStop(.5, `rgba(59, 130, 246, ${.045 * opacity})`);
        wave.addColorStop(1, 'rgba(15, 23, 42, 0)');
        context.fillStyle = wave;
        context.fillRect(0, 0, width, height);
        for (let waveIndex = 0; waveIndex < 3; waveIndex += 1) {
            context.beginPath();
            for (let x = -40; x <= width + 40; x += 24) {
                const y = height * (.28 + waveIndex * .2) + Math.sin(x * .004 + time * .00015 + waveIndex) * (24 + waveIndex * 8) + driftY;
                if (x === -40) context.moveTo(x + driftX, y); else context.lineTo(x + driftX, y);
            }
            context.strokeStyle = `rgba(59, 130, 246, ${.035 * opacity})`;
            context.lineWidth = 1.5;
            context.stroke();
        }
        particles.forEach((particle) => {
            const x = particle.x * width + driftX * particle.speed * 1000;
            const y = ((particle.y + time * particle.speed) % 1) * height + driftY * particle.speed * 1000;
            const glow = .16 + Math.sin(time * .001 + particle.phase) * .06;
            context.beginPath();
            context.fillStyle = `rgba(147, 197, 253, ${glow * opacity})`;
            context.arc(x, y, particle.radius, 0, Math.PI * 2);
            context.fill();
        });
        streaks.forEach((streak) => {
            const x = ((time * streak.speed + streak.offset) % 1.25) * width - streak.length;
            const gradient = context.createLinearGradient(x, 0, x + streak.length, 0);
            gradient.addColorStop(0, 'rgba(59,130,246,0)');
            gradient.addColorStop(.55, `rgba(96,165,250,${.08 * opacity})`);
            gradient.addColorStop(1, 'rgba(96,165,250,0)');
            context.fillStyle = gradient;
            context.fillRect(x, streak.y * height, streak.length, 1);
        });
        animationFrame = requestAnimationFrame(draw);
    }
    resize();
    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('pointermove', (event) => { pointerX = event.clientX / window.innerWidth - .5; pointerY = event.clientY / window.innerHeight - .5; document.documentElement.style.setProperty('--parallax-x', `${pointerX * 12}px`); document.documentElement.style.setProperty('--parallax-y', `${pointerY * 8}px`); }, { passive: true });
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) animationFrame = requestAnimationFrame(draw);
    window.addEventListener('beforeunload', () => cancelAnimationFrame(animationFrame), { once: true });
}

function initializePageMotion() {
    const selectors = '.dashboard-card, .command-kpi, .command-panel, .analytics-panel, .card, .match-candidate-card, .detail-card, .editor-main, .analysis-panel';
    document.querySelectorAll(selectors).forEach((element, index) => {
        element.classList.add('live-card');
        element.style.setProperty('--live-delay', `${Math.min(index, 8) * 55}ms`);
    });
}

function initializePricingToggle() {
    const pricingToggle = document.querySelector('[data-pricing-toggle]');
    const toggleButton = pricingToggle?.querySelector('[data-billing-toggle]');
    if (!pricingToggle || !toggleButton) return;

    const values = pricingToggle.querySelectorAll('.price-value');
    const labels = pricingToggle.querySelectorAll('[data-billing-label]');

    toggleButton.addEventListener('click', () => {
        const yearly = toggleButton.getAttribute('aria-pressed') !== 'true';
        toggleButton.setAttribute('aria-pressed', String(yearly));
        toggleButton.classList.toggle('is-yearly', yearly);
        labels.forEach(label => label.classList.toggle('is-active', label.dataset.billingLabel === (yearly ? 'yearly' : 'monthly')));
        values.forEach(value => {
            value.style.opacity = '0';
            value.style.transform = 'translateY(5px)';
            window.setTimeout(() => {
                value.textContent = value.dataset[yearly ? 'yearly' : 'monthly'];
                value.style.opacity = '1';
                value.style.transform = 'translateY(0)';
            }, 140);
        });
    });
}

function initializeLiveCharts() {
    if (typeof Chart === 'undefined') return;
    setInterval(() => {
        const charts = Chart.instances instanceof Map ? Chart.instances.values() : Object.values(Chart.instances || {});
        Array.from(charts).forEach(chart => {
            chart.data.datasets.forEach(dataset => {
                if (!Array.isArray(dataset.data)) return;
                dataset.data = dataset.data.map(value => {
                    const numeric = Number(value);
                    if (!Number.isFinite(numeric) || numeric === 0) return value;
                    return Math.max(0, numeric + (Math.random() - 0.5) * Math.max(1, numeric * 0.025));
                });
            });
            chart.update('none');
        });
    }, 4000);
}

function initializeCommandCenter() {
    const dashboard = document.querySelector('.command-center[data-dashboard-url]');
    const canvas = document.getElementById('candidate-doughnut');
    if (!dashboard || !canvas || typeof Chart === 'undefined') return;
    const root = document.documentElement;
    let latest = { total_candidates: 0, analyzed_candidates: 0, shortlisted_candidates: 0, total_jobs: 0 };
    const chart = new Chart(canvas, {
        type: 'doughnut',
        data: { labels: ['New profiles', 'Analyzed', 'Shortlisted'], datasets: [{ data: [0, 0, 0], backgroundColor: ['#5b8cff', '#27c7d9', '#37d39a'], borderWidth: 0, hoverOffset: 8 }] },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '76%',
            animation: { duration: 1500, easing: 'easeOutQuart' },
            interaction: { intersect: false, mode: 'nearest' },
            plugins: { legend: { display: false }, tooltip: { displayColors: false, padding: 10, cornerRadius: 8, animation: { duration: 300 } } },
        },
    });

    function updateTheme() {
        chart.options.plugins.tooltip.backgroundColor = root.dataset.theme === 'light' ? '#0f172a' : '#e2e8f0';
        chart.options.plugins.tooltip.titleColor = root.dataset.theme === 'light' ? '#fff' : '#0f172a';
        chart.options.plugins.tooltip.bodyColor = root.dataset.theme === 'light' ? '#cbd5e1' : '#334155';
        chart.update('none');
    }
    function setFunnelValue(name, value, percent) {
        const label = document.querySelector(`[data-funnel="${name}"]`);
        const bar = document.querySelector(`[data-funnel-bar="${name}"]`);
        if (label) label.textContent = value;
        if (bar) requestAnimationFrame(() => { bar.style.width = `${Math.max(0, Math.min(100, percent))}%`; });
    }
    function render(data, animate = true) {
        latest = data;
        const total = Number(data.total_candidates || 0);
        const analyzed = Number(data.analyzed_candidates || 0);
        const shortlisted = Number(data.shortlisted_candidates || 0);
        const jobs = Number(data.total_jobs || 0);
        document.getElementById('candidate-total').textContent = total;
        chart.data.datasets[0].data = [Math.max(total - analyzed, 0), analyzed, shortlisted];
        chart.update(animate ? undefined : 'none');
        setFunnelValue('candidates', total, 100);
        setFunnelValue('analyzed', analyzed, total ? analyzed / total * 100 : 0);
        setFunnelValue('shortlisted', shortlisted, total ? shortlisted / total * 100 : 0);
        setFunnelValue('jobs', jobs, total ? Math.min(100, jobs / total * 100) : 0);
    }
    function refresh() {
        fetch(dashboard.dataset.dashboardUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.ok ? response.json() : Promise.reject(new Error('Dashboard unavailable')))
            .then(data => render(data))
            .catch(() => {});
    }
    updateTheme();
    refresh();
    setInterval(refresh, 5000);
    root.addEventListener('themechange', updateTheme);
}

// ============================================
// FORM HANDLING
// ============================================

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-action]');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const action = form.getAttribute('data-action') || form.getAttribute('action');

    // Show loading state
    const submitBtn = form.querySelector('[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    submitBtn.disabled = true;

    try {
        const response = await fetch(action, {
            method: form.method || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Success!', data.message || 'Operation completed', 'success');
            form.reset();
            if (form.closest('.modal')) {
                closeModal(form.closest('.modal'));
            }
            // Reload page after short delay
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Error', data.error || 'Something went wrong', 'error');
        }
    } catch (error) {
        console.error('Form submission error:', error);
        showNotification('Error', error.message, 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// ============================================
// MODAL HANDLING
// ============================================

/**
 * Initialize modal functionality
 */
function initializeModals() {
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        const closeBtn = modal.querySelector('[data-modal-close]');
        const overlay = modal.querySelector('.modal-overlay');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => closeModal(modal));
        }

        if (overlay) {
            overlay.addEventListener('click', () => closeModal(modal));
        }
    });

    // Handle modal open buttons
    document.querySelectorAll('[data-modal-open]').forEach(btn => {
        btn.addEventListener('click', () => {
            const modalId = btn.getAttribute('data-modal-open');
            const modal = document.getElementById(modalId);
            if (modal) openModal(modal);
        });
    });
}

/**
 * Open a modal with animation
 */
function openModal(modal) {
    modal.classList.add('active');
    if (typeof gsap !== 'undefined') {
        gsap.fromTo(
            modal,
            { opacity: 0 },
            { opacity: 1, duration: 0.3 }
        );
    }
}

/**
 * Close a modal with animation
 */
function closeModal(modal) {
    if (typeof gsap !== 'undefined') {
        gsap.to(modal, {
            opacity: 0,
            duration: 0.2,
            onComplete: () => {
                modal.classList.remove('active');
            },
        });
    } else {
        modal.classList.remove('active');
    }
}

// ============================================
// NOTIFICATIONS
// ============================================

/**
 * Show a notification toast
 */
function showNotification(title, message, type = 'info') {
    const container = document.getElementById('notification-container') || createNotificationContainer();

    const notification = document.createElement('div');
    notification.className = `notification notification-${type} slide-down`;
    notification.innerHTML = `
        <div class="notification-icon">
            ${getNotificationIcon(type)}
        </div>
        <div class="notification-content">
            <h4>${title}</h4>
            <p>${message}</p>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Get icon for notification type
 */
function getNotificationIcon(type) {
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-times-circle"></i>',
        warning: '<i class="fas fa-exclamation-circle"></i>',
        info: '<i class="fas fa-info-circle"></i>',
    };
    return icons[type] || icons.info;
}

/**
 * Create notification container if it doesn't exist
 */
function createNotificationContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.className = 'notification-container fixed top-4 right-4 z-50';
    document.body.appendChild(container);
    return container;
}

// ============================================
// API CALLS
// ============================================

/**
 * Make API call with error handling
 */
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
    };

    const mergedOptions = { ...defaultOptions, ...options };

    try {
        const response = await fetch(endpoint, mergedOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Upload file to API
 */
async function uploadFile(endpoint, file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Upload Error:', error);
        throw error;
    }
}

// ============================================
// FILE UPLOAD WITH DRAG & DROP
// ============================================

/**
 * Setup drag-drop file upload
 */
function setupFileUpload(dropZoneSelector, fileInputSelector) {
    const dropZone = document.querySelector(dropZoneSelector);
    const fileInput = document.querySelector(fileInputSelector);

    if (!dropZone || !fileInput) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    // Handle file input change
    fileInput.addEventListener('change', () => {
        handleFiles(fileInput.files);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('highlight');
    }

    function unhighlight(e) {
        dropZone.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        handleFiles(files);
    }

    function handleFiles(files) {
        // Process files
        for (let i = 0; i < files.length; i++) {
            processFile(files[i]);
        }
    }
}

/**
 * Process individual file
 */
function processFile(file) {
    console.log('Processing file:', file.name);
    // File processing logic here
}

// ============================================
// REAL-TIME UPDATES (WebSocket)
// ============================================

/**
 * Setup real-time updates via WebSocket
 */
function setupRealtimeUpdates() {
    // Initialize Socket.IO if available
    if (typeof io !== 'undefined') {
        const socket = io();

        socket.on('connect', () => {
            console.log('Connected to real-time server');
        });

        socket.on('score_updated', (data) => {
            updateCandidateScore(data);
        });

        socket.on('job_updated', (data) => {
            updateJobDisplay(data);
        });

        socket.on('notification', (data) => {
            showNotification(data.title, data.message, data.type);
        });
    }
}

/**
 * Update candidate score in UI
 */
function updateCandidateScore(data) {
    const element = document.querySelector(`[data-candidate-id="${data.candidate_id}"]`);
    if (element) {
        const scoreEl = element.querySelector('.score-value');
        if (scoreEl) {
            // Animate score change
            const oldScore = parseFloat(scoreEl.textContent);
            const newScore = data.score;

            if (typeof gsap !== 'undefined') {
                gsap.to(scoreEl, {
                    duration: 0.6,
                    textContent: newScore,
                    snap: { textContent: 1 },
                    ease: 'power2.out',
                });
            } else {
                scoreEl.textContent = newScore;
            }
        }
    }
}

/**
 * Update job display in UI
 */
function updateJobDisplay(data) {
    // Update job information
    console.log('Job updated:', data);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Debounce function
 */
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

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format number as percentage
 */
function formatPercentage(value, decimals = 1) {
    return (parseFloat(value) || 0).toFixed(decimals) + '%';
}

/**
 * Format large numbers
 */
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Copy to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied', 'Text copied to clipboard', 'success');
    });
}

// ============================================
// EVENT LISTENERS
// ============================================

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Smooth scroll links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Copy buttons
    document.querySelectorAll('[data-copy]').forEach(btn => {
        btn.addEventListener('click', () => {
            const text = btn.getAttribute('data-copy');
            copyToClipboard(text);
        });
    });

    // Dropdown menus
    document.querySelectorAll('[data-dropdown]').forEach(dropdown => {
        const toggle = dropdown.querySelector('[data-dropdown-toggle]');
        const menu = dropdown.querySelector('[data-dropdown-menu]');

        if (toggle && menu) {
            toggle.addEventListener('click', () => {
                menu.classList.toggle('hidden');
            });

            document.addEventListener('click', (e) => {
                if (!dropdown.contains(e.target)) {
                    menu.classList.add('hidden');
                }
            });
        }
    });
}

// ============================================
// EXPORT FUNCTIONS
// ============================================

window.SmartHireUI = {
    showNotification,
    openModal,
    closeModal,
    apiCall,
    uploadFile,
    setupFileUpload,
    formatPercentage,
    formatNumber,
    copyToClipboard,
    initializeAnimations,
};
