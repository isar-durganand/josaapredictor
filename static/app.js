/**
 * JoSAA Predictor - World-Class Interaction & Animation Engine
 * Inspired by Linear, Vercel, and Stripe.
 * Provides:
 * 1. Global Command Palette (Ctrl+K / Cmd+K)
 * 2. Mouse Spotlight Card Shimmer
 * 3. Animated Number Rollers
 * 4. Interactive Segmented Sliding Pills
 * 5. Instant Table Column Sorting & Live Search
 * 6. Interactive Toast Notification System
 * 7. Keyboard Navigation & Accessibility
 */

(function () {
    'use strict';

    // ==========================================
    // 1. Toast Notification System
    // ==========================================
    window.showToast = function (title, message = '', icon = 'bi-check-circle-fill', type = 'success') {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container-global';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `custom-toast toast-${type} animate-toast-in`;
        toast.innerHTML = `
            <div class="toast-icon"><i class="bi ${icon}"></i></div>
            <div class="toast-body">
                <div class="toast-title">${title}</div>
                ${message ? `<div class="toast-desc">${message}</div>` : ''}
            </div>
            <button class="toast-close" aria-label="Close">&times;</button>
        `;

        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.add('animate-toast-out');
            setTimeout(() => toast.remove(), 250);
        });

        container.appendChild(toast);

        setTimeout(() => {
            if (toast.parentNode) {
                toast.classList.add('animate-toast-out');
                setTimeout(() => toast.remove(), 250);
            }
        }, 4000);
    };

    // ==========================================
    // 2. Command Palette (Ctrl+K / Cmd+K)
    // ==========================================
    const commandItems = [
        { title: 'Launch College Predictor', category: 'Tool', url: '/predictor', icon: 'bi-search' },
        { title: 'Calculate AIR from Score / Percentile', category: 'Tool', url: '/rank-predictor', icon: 'bi-calculator' },
        { title: 'JEE Main 2025 Cutoff Percentiles', category: 'Data', url: '/cutoffs', icon: 'bi-bar-chart-line' },
        { title: 'Explore Top 23 IITs', category: 'Institutes', url: '/predictor?type=IIT', icon: 'bi-buildings' },
        { title: 'Explore Top 31 NITs', category: 'Institutes', url: '/predictor?type=NIT', icon: 'bi-buildings' },
        { title: 'Explore 26 IIITs', category: 'Institutes', url: '/predictor?type=IIIT', icon: 'bi-cpu' },
        { title: 'Explore 30+ GFTIs', category: 'Institutes', url: '/predictor?type=GFTI', icon: 'bi-building' },
        { title: 'IIT Bombay Profile & Cutoffs', category: 'Guide', url: '/blog/iit-bombay', icon: 'bi-mortarboard' },
        { title: 'IIT Delhi Profile & Cutoffs', category: 'Guide', url: '/blog/iit-delhi', icon: 'bi-mortarboard' },
        { title: 'IIT Madras Profile & Cutoffs', category: 'Guide', url: '/blog/iit-madras', icon: 'bi-mortarboard' },
        { title: 'NIT Trichy Profile & Cutoffs', category: 'Guide', url: '/blog/nit-trichy', icon: 'bi-mortarboard' },
        { title: 'NIT Surathkal Profile & Cutoffs', category: 'Guide', url: '/blog/nit-surathkal', icon: 'bi-mortarboard' },
        { title: 'NIT Warangal Profile & Cutoffs', category: 'Guide', url: '/blog/nit-warangal', icon: 'bi-mortarboard' },
        { title: 'Counseling Methodology & Transparency', category: 'About', url: '/about', icon: 'bi-info-circle' },
        { title: 'Contact Counseling Desk', category: 'Support', url: '/contact', icon: 'bi-envelope' }
    ];

    function initCommandPalette() {
        const modal = document.getElementById('cmd-palette-modal');
        const input = document.getElementById('cmd-palette-input');
        const list = document.getElementById('cmd-palette-list');
        if (!modal || !input || !list) return;

        let activeIndex = 0;
        let filteredItems = [...commandItems];

        function renderItems(items) {
            filteredItems = items;
            list.innerHTML = '';
            if (items.length === 0) {
                list.innerHTML = `<div class="cmd-empty">No matching pages, colleges, or tools found.</div>`;
                return;
            }

            items.forEach((item, index) => {
                const el = document.createElement('a');
                el.href = item.url;
                el.className = `cmd-item ${index === activeIndex ? 'active' : ''}`;
                el.innerHTML = `
                    <div class="cmd-item-left">
                        <span class="cmd-item-icon"><i class="bi ${item.icon}"></i></span>
                        <span class="cmd-item-title">${item.title}</span>
                    </div>
                    <span class="cmd-item-category">${item.category}</span>
                `;
                el.addEventListener('mouseenter', () => {
                    activeIndex = index;
                    updateActive();
                });
                list.appendChild(el);
            });
        }

        function updateActive() {
            const els = list.querySelectorAll('.cmd-item');
            els.forEach((el, i) => {
                el.classList.toggle('active', i === activeIndex);
            });
            if (els[activeIndex]) {
                els[activeIndex].scrollIntoView({ block: 'nearest' });
            }
        }

        function openPalette() {
            modal.classList.add('open');
            input.value = '';
            activeIndex = 0;
            renderItems(commandItems);
            setTimeout(() => input.focus(), 50);
            document.body.style.overflow = 'hidden';
        }

        function closePalette() {
            modal.classList.remove('open');
            document.body.style.overflow = '';
        }

        // Global key shortcut Ctrl+K / Cmd+K
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                if (modal.classList.contains('open')) {
                    closePalette();
                } else {
                    openPalette();
                }
            } else if (e.key === 'Escape' && modal.classList.contains('open')) {
                closePalette();
            } else if (modal.classList.contains('open')) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    if (filteredItems.length > 0) {
                        activeIndex = (activeIndex + 1) % filteredItems.length;
                        updateActive();
                    }
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    if (filteredItems.length > 0) {
                        activeIndex = (activeIndex - 1 + filteredItems.length) % filteredItems.length;
                        updateActive();
                    }
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    if (filteredItems[activeIndex]) {
                        window.location.href = filteredItems[activeIndex].url;
                    }
                }
            }
        });

        // Trigger buttons
        document.querySelectorAll('.btn-open-cmd').forEach(btn => {
            btn.addEventListener('click', openPalette);
        });

        // Modal backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closePalette();
        });

        // Filter search input
        input.addEventListener('input', () => {
            const q = input.value.toLowerCase().trim();
            const matches = commandItems.filter(item =>
                item.title.toLowerCase().includes(q) ||
                item.category.toLowerCase().includes(q)
            );
            activeIndex = 0;
            renderItems(matches);
        });
    }

    // ==========================================
    // 3. Mouse Spotlight Card Hover Effect (Linear Style)
    // ==========================================
    function initSpotlightCards() {
        const cards = document.querySelectorAll('.spotlight-card, .metric-card, .control-card, .guide-card, .feature-grid-card');
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--mouse-x', `${x}px`);
                card.style.setProperty('--mouse-y', `${y}px`);
            });
        });
    }

    // ==========================================
    // 4. Smooth Number Rollers (Physics Ease-Out)
    // ==========================================
    function initNumberRollers() {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    obs.unobserve(el);
                    const target = parseInt(el.getAttribute('data-count'), 10);
                    if (isNaN(target)) return;

                    const duration = 1600;
                    const startTime = performance.now();

                    function updateNumber(now) {
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // Ease-out cubic curve
                        const eased = 1 - Math.pow(1 - progress, 3);
                        const current = Math.floor(eased * target);

                        el.textContent = current.toLocaleString() + (target > 100 ? '+' : '');

                        if (progress < 1) {
                            requestAnimationFrame(updateNumber);
                        } else {
                            el.textContent = target.toLocaleString() + (target > 100 ? '+' : '');
                        }
                    }

                    requestAnimationFrame(updateNumber);
                }
            });
        }, { threshold: 0.2 });

        document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
    }

    // ==========================================
    // 5. Interactive Scroll-Triggered Reveal
    // ==========================================
    function initScrollReveals() {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
    }

    // ==========================================
    // 6. Interactive Segmented Sliding Control
    // ==========================================
    function initSegmentedControls() {
        document.querySelectorAll('.segmented-control').forEach(container => {
            let indicator = container.querySelector('.segmented-indicator');
            if (!indicator) {
                indicator = document.createElement('div');
                indicator.className = 'segmented-indicator';
                container.prepend(indicator);
            }

            const tabs = container.querySelectorAll('.segmented-tab');

            function moveIndicator(tab) {
                if (!tab) return;
                const containerRect = container.getBoundingClientRect();
                const tabRect = tab.getBoundingClientRect();
                const left = tabRect.left - containerRect.left - 2;
                const width = tabRect.width;

                indicator.style.transform = `translateX(${left}px)`;
                indicator.style.width = `${width}px`;
            }

            // Initial positioning
            const activeTab = container.querySelector('.segmented-tab.active') || tabs[0];
            if (activeTab) {
                setTimeout(() => moveIndicator(activeTab), 50);
            }

            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    tabs.forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    moveIndicator(tab);
                });
            });

            window.addEventListener('resize', () => {
                const cur = container.querySelector('.segmented-tab.active');
                if (cur) moveIndicator(cur);
            }, { passive: true });
        });
    }

    // ==========================================
    // 7. Interactive Table Utilities (Sort & Live Filter)
    // ==========================================
    window.initTableUtilities = function (tableId, filterInputId = null) {
        const table = document.getElementById(tableId);
        if (!table) return;

        // Column Sorting
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.title = 'Click to sort';
            header.addEventListener('click', () => {
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const colIndex = Array.from(header.parentNode.children).indexOf(header);
                const isAsc = header.classList.contains('sort-asc');

                headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                header.classList.toggle('sort-asc', !isAsc);
                header.classList.toggle('sort-desc', isAsc);

                rows.sort((a, b) => {
                    const aCell = a.children[colIndex].textContent.trim().replace(/,/g, '');
                    const bCell = b.children[colIndex].textContent.trim().replace(/,/g, '');
                    const aNum = parseFloat(aCell);
                    const bNum = parseFloat(bCell);

                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return isAsc ? bNum - aNum : aNum - bNum;
                    }
                    return isAsc ? bCell.localeCompare(aCell) : aCell.localeCompare(bCell);
                });

                rows.forEach(r => tbody.appendChild(r));
            });
        });

        // Instant Live Filter
        if (filterInputId) {
            const input = document.getElementById(filterInputId);
            if (input) {
                input.addEventListener('input', () => {
                    const query = input.value.toLowerCase().trim();
                    const rows = table.querySelectorAll('tbody tr');
                    let count = 0;
                    rows.forEach(row => {
                        const match = row.textContent.toLowerCase().includes(query);
                        row.style.display = match ? '' : 'none';
                        if (match) count++;
                    });
                });
            }
        }
    };

    // Initialize all modules on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        initCommandPalette();
        initSpotlightCards();
        initNumberRollers();
        initScrollReveals();
        initSegmentedControls();
    });

})();
