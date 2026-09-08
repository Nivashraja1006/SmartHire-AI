(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        try { initAssistantPanel(); } catch (error) { console.error('SmartHire assistant failed to initialize', error); }
        initReveal();
        initSmoothScroll();
        initMobileNav();
        initPasswordToggles();
        initThemeToggle();
        initFormLoading();
        initSecurity();
        initRealtime();
    });

    function initThemeToggle() {
        var toggle = document.querySelector('[data-theme-toggle]');
        if (!toggle) return;
        var root = document.documentElement;
        function updateToggle() {
            var light = root.dataset.theme === 'light';
            toggle.setAttribute('aria-label', light ? 'Switch to dark mode' : 'Switch to light mode');
            toggle.title = light ? 'Switch to dark mode' : 'Switch to light mode';
            toggle.innerHTML = light ? '<i class="fas fa-moon"></i><span>Dark</span>' : '<i class="fas fa-sun"></i><span>Light</span>';
        }
        updateToggle();
        toggle.addEventListener('click', function () {
            root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
            localStorage.setItem('smarthire-theme', root.dataset.theme);
            root.dispatchEvent(new CustomEvent('themechange'));
            updateToggle();
        });
    }

    function initSecurity() {
        var token = document.querySelector('meta[name="csrf-token"]');
        if (!token) return;
        document.querySelectorAll('form[method="post"], form[method="POST"]').forEach(function (form) {
            if (!form.querySelector('input[name="csrf_token"]')) {
                var field = document.createElement('input');
                field.type = 'hidden'; field.name = 'csrf_token'; field.value = token.content;
                form.appendChild(field);
            }
        });
        var originalFetch = window.fetch;
        window.fetch = function (input, init) {
            init = init || {};
            var method = (init.method || 'GET').toUpperCase();
            if (method !== 'GET' && method !== 'HEAD' && method !== 'OPTIONS') {
                var headers = new Headers(init.headers || {});
                headers.set('X-CSRFToken', token.content);
                init.headers = headers;
            }
            return originalFetch(input, init);
        };
    }

    function initReveal() {
        var els = document.querySelectorAll('.reveal');
        if (!('IntersectionObserver' in window) || !els.length) {
            els.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    var el = entry.target;
                    var delay = Math.min(([].indexOf.call(els, el) % 6) * 70, 350);
                    setTimeout(function () { el.classList.add('is-visible'); }, delay);
                    io.unobserve(el);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        els.forEach(function (el) { io.observe(el); });
    }

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (a) {
            a.addEventListener('click', function (e) {
                var id = a.getAttribute('href');
                if (id.length <= 1) return;
                var target = document.querySelector(id);
                if (!target) return;
                e.preventDefault();
                var nav = document.querySelector('.navbar');
                var offset = nav ? nav.offsetHeight + 10 : 70;
                var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top: top, behavior: 'smooth' });
                var links = document.querySelector('.nav-links');
                if (links && links.classList.contains('open')) {
                    links.classList.remove('open');
                }
            });
        });
    }

    function initMobileNav() {
        var btn = document.querySelector('.nav-toggle');
        var links = document.querySelector('.nav-links');
        if (!btn || !links) return;
        btn.addEventListener('click', function () {
            links.classList.toggle('open');
            var icon = btn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-xmark');
            }
        });
    }

    function initPasswordToggles() {
        document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
            button.addEventListener('click', function () {
                var input = document.getElementById(button.dataset.passwordToggle);
                if (!input) return;
                var visible = input.type === 'text';
                input.type = visible ? 'password' : 'text';
                button.textContent = visible ? 'Show' : 'Hide';
            });
        });
    }

    function initAssistantPanel() {
        var fab = document.getElementById('assistant-fab');
        var panel = document.getElementById('assistant-panel');
        var closeButton = document.querySelector('[data-assistant-close]');
        var form = document.querySelector('[data-assistant-form]');
        var messagesNode = document.getElementById('assistant-messages');
        var emptyState = document.querySelector('[data-assistant-empty]');
        var typing = document.querySelector('[data-assistant-typing]');
        var sendButton = document.querySelector('[data-assistant-send]');
        var textarea = form ? form.querySelector('textarea') : null;
        var endpoint = document.querySelector('[data-chat-endpoint]')?.dataset.chatEndpoint || '';
        var storageKey = 'smarthire-assistant-messages';
        if (!fab || !panel) return;
        panel.hidden = true;
        panel.setAttribute('aria-hidden', 'true');

        function setOpen(open) {
            panel.hidden = !open;
            panel.setAttribute('aria-hidden', String(!open));
            fab.setAttribute('aria-expanded', String(open));
            fab.setAttribute('aria-label', open ? 'Close AI assistant' : 'Open AI assistant');
            if (open && textarea) window.setTimeout(function () { textarea.focus(); }, 120);
        }

        fab.addEventListener('click', function () {
            setOpen(panel.hidden);
        });

        if (closeButton) {
            closeButton.addEventListener('click', function () {
                setOpen(false);
            });
        }

        document.addEventListener('click', function (event) {
            if (panel.hidden) return;
            if (!panel.contains(event.target) && !fab.contains(event.target)) {
                setOpen(false);
            }
        });

        function loadMessages() {
            try { return JSON.parse(sessionStorage.getItem(storageKey) || '[]'); } catch (error) { return []; }
        }
        function saveMessages(items) {
            try { sessionStorage.setItem(storageKey, JSON.stringify(items.slice(-40))); } catch (error) { /* Storage may be unavailable. */ }
        }
        function renderMessage(item) {
            var message = document.createElement('div');
            message.className = 'assistant-message ' + (item.sender === 'user' ? 'assistant-user' : 'assistant-bot');
            var bubble = document.createElement('p');
            bubble.textContent = item.text;
            message.appendChild(bubble);
            messagesNode.insertBefore(message, typing);
        }
        function renderHistory() {
            if (!messagesNode) return;
            loadMessages().forEach(renderMessage);
            if (emptyState) emptyState.hidden = messagesNode.querySelectorAll('.assistant-message').length > 0;
            messagesNode.scrollTop = messagesNode.scrollHeight;
        }
        function setLoading(isLoading) {
            if (typing) typing.hidden = !isLoading;
            if (sendButton) sendButton.disabled = isLoading;
            if (textarea) textarea.disabled = isLoading;
            if (isLoading && messagesNode) messagesNode.scrollTop = messagesNode.scrollHeight;
        }
        function mockReply(value) {
            return new Promise(function (resolve) {
                window.setTimeout(function () {
                    resolve('I can help you review hiring signals for "' + value.slice(0, 80) + '". Connect a recruiter workspace to get live candidate and pipeline analysis.');
                }, 650);
            });
        }
        async function getReply(value) {
            if (!endpoint) return mockReply(value);
            try {
                var response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                    body: JSON.stringify({ message: value })
                });
                var payload = await response.json();
                if (!response.ok || !payload.success) throw new Error(payload.error || 'Assistant request failed');
                return payload.response || 'I received your question, but there was no response text.';
            } catch (error) {
                return 'I could not reach the live hiring workspace, so I am in preview mode. Try again in a moment or open the recruiter Copilot page.';
            }
        }
        async function submitMessage(value) {
            var history = loadMessages();
            var userItem = { sender: 'user', text: value };
            history.push(userItem); saveMessages(history); renderMessage(userItem);
            if (emptyState) emptyState.hidden = true;
            if (textarea) textarea.value = '';
            setLoading(true);
            try {
                var reply = await getReply(value);
                var botItem = { sender: 'assistant', text: reply };
                history = loadMessages(); history.push(botItem); saveMessages(history); renderMessage(botItem);
            } finally {
                setLoading(false);
                if (messagesNode) messagesNode.scrollTop = messagesNode.scrollHeight;
                if (textarea) textarea.focus();
            }
        }
        renderHistory();
        if (form && textarea) {
            form.addEventListener('submit', function (event) {
                event.preventDefault();
                var value = textarea.value.trim();
                if (value && !sendButton.disabled) submitMessage(value);
            });
            textarea.addEventListener('keydown', function (event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    form.requestSubmit();
                }
            });
        }
    }

    function initFormLoading() {
        document.querySelectorAll('.auth-form').forEach(function (form) {
            form.addEventListener('submit', function () {
                var button = form.querySelector('.auth-submit');
                if (!button) return;
                button.disabled = true;
                button.classList.add('is-loading');
                button.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Working...';
            });
        });
    }

    function initRealtime() {
        var bell = document.getElementById('notification-button');
        if (!bell || typeof io !== 'function') return;
        var count = document.getElementById('notification-count');
        var panel = document.getElementById('notification-panel');
        var list = document.getElementById('notification-list');
        var socket = io({ transports: ['websocket', 'polling'] });
        var live = document.querySelectorAll('[data-live-status]');
        function setLive(text, connected) { live.forEach(function (node) { var label = node.querySelector('em'); if (label) label.textContent = text; node.classList.toggle('is-offline', !connected); }); }
        function renderNotification(item) {
            var row = document.createElement('div'); row.className = 'notification-item' + (item.is_read ? '' : ' unread');
            row.innerHTML = '<strong></strong><p></p><small></small>'; row.querySelector('strong').textContent = item.title; row.querySelector('p').textContent = item.message; row.querySelector('small').textContent = new Date(item.created_at).toLocaleString();
            row.addEventListener('click', function () { fetch('/api/notifications/' + item.id + '/read', {method: 'POST'}); row.classList.remove('unread'); }); return row;
        }
        function loadNotifications() { fetch('/api/notifications').then(function (response) { if (!response.ok) throw new Error('Notifications unavailable'); return response.json(); }).then(function (data) { count.textContent = data.unread_count; count.hidden = !data.unread_count; list.innerHTML = ''; data.notifications.forEach(function (item) { list.appendChild(renderNotification(item)); }); if (!data.notifications.length) list.innerHTML = '<p class="notification-empty">No notifications yet.</p>'; }).catch(function () { list.innerHTML = '<p class="notification-empty">Notifications are temporarily unavailable.</p>'; }); }
        bell.addEventListener('click', function () { panel.hidden = !panel.hidden; if (!panel.hidden) loadNotifications(); });
        document.getElementById('mark-all-read')?.addEventListener('click', function () { fetch('/api/notifications/read-all', {method: 'POST'}).then(loadNotifications); });
        socket.on('connect', function () { setLive('Live', true); socket.emit('join_recruiter_room', {}); }); socket.on('disconnect', function () { setLive('Reconnecting...', false); }); socket.on('notification_created', function (item) { count.textContent = Number(count.textContent || 0) + 1; count.hidden = false; showToast(item.title, item.message); }); socket.on('activity_created', refreshDashboard); socket.on('analytics_updated', function () { document.dispatchEvent(new CustomEvent('analytics-updated')); }); socket.on('candidate_score_updated', refreshDashboard); socket.on('ranking_completed', refreshDashboard); socket.on('candidate_shortlisted', refreshDashboard); socket.on('candidate_unshortlisted', refreshDashboard);
        loadNotifications(); refreshDashboard();
        function refreshDashboard() { var dashboard = document.querySelector('[data-dashboard-url]'); if (!dashboard) return; fetch(dashboard.dataset.dashboardUrl).then(function (response) { return response.json(); }).then(function (data) { Object.keys(data).forEach(function (key) { var node = document.querySelector('[data-metric="' + key + '"]'); if (node) node.textContent = data[key]; }); var feed = document.getElementById('activity-feed'); if (feed && data.recent_activity) { feed.innerHTML = data.recent_activity.map(function (item) { return '<div class="activity-item"><span></span><div><strong>' + item.activity_type + '</strong><p>' + item.description + '</p><small>' + new Date(item.created_at).toLocaleTimeString() + '</small></div></div>'; }).join('') || '<p class="helper-text">No activity yet.</p>'; } }); }
        function showToast(title, message) { var toast = document.createElement('div'); toast.className = 'live-toast'; toast.innerHTML = '<strong></strong><p></p>'; toast.querySelector('strong').textContent = title; toast.querySelector('p').textContent = message; document.body.appendChild(toast); setTimeout(function () { toast.remove(); }, 4500); }
    }
})();
