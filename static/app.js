/**
 * JoSAA Predictor - The Apple Interaction & Animation Engine
 * Engineered to strict Apple HIG & iOS/macOS physics guidelines:
 * 1. The Dynamic Dock & Hover Magnification
 * 2. Spatial Continuity & Apple Sheet Presentation (Z-axis scale)
 * 3. macOS Spotlight Command Search (⌘K / ⌘Space)
 * 4. Fluid Morphing Segmented Pill Controls
 * 5. Physics-Based Ease-Out Number Rollers
 * 6. Tactile Slider & Haptic Button Feedback
 * 7. Apple Dynamic Island Toast Notifications
 * 8. Real-time Spec Table Sorting & In-place Filtering
 */

(function () {
    'use strict';

    // ==========================================
    // 1. Apple Dynamic Island / HUD Toast System
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
        toast.className = `custom-toast animate-toast-in`;
        
        let iconColor = 'var(--brand)';
        if (type === 'warning') iconColor = 'var(--apple-orange)';
        if (type === 'danger') iconColor = 'var(--apple-red)';
        if (type === 'success') iconColor = 'var(--apple-green)';

        toast.innerHTML = `
            <div class="toast-icon" style="color: ${iconColor};"><i class="bi ${icon}"></i></div>
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
        }, 3600);
    };

    // ==========================================
    // 2. Spatial Continuity: Apple Sheet Presentation
    // ==========================================
    window.openAppleSheet = function () {
        document.body.classList.add('sheet-open');
    };

    window.closeAppleSheet = function () {
        document.body.classList.remove('sheet-open');
    };

    // ==========================================
    // 3. macOS Spotlight Command Search (⌘K / ⌘Space)
    // ==========================================
    const spotlightItems = [
        { title: 'Launch College Predictor', category: 'Tool', url: '/predictor', icon: 'bi-search' },
        { title: 'AIR & Percentile Calculator', category: 'Tool', url: '/rank-predictor', icon: 'bi-calculator' },
        { title: 'JEE Main 2025 Cutoff Benchmarks', category: 'Data', url: '/cutoffs', icon: 'bi-bar-chart-line' },
        { title: 'Top 23 IITs Admissions Directory', category: 'Institutes', url: '/predictor?type=IIT', icon: 'bi-buildings' },
        { title: 'Top 31 NITs Admissions Directory', category: 'Institutes', url: '/predictor?type=NIT', icon: 'bi-buildings' },
        { title: 'Top 26 IIITs Admissions Directory', category: 'Institutes', url: '/predictor?type=IIIT', icon: 'bi-cpu' },
        { title: '30+ GFTIs Admissions Directory', category: 'Institutes', url: '/predictor?type=GFTI', icon: 'bi-building' },
        { title: 'IIT Bombay Profile & Cutoffs', category: 'Guide', url: '/blog/iit-bombay', icon: 'bi-mortarboard' },
        { title: 'IIT Delhi Profile & Cutoffs', category: 'Guide', url: '/blog/iit-delhi', icon: 'bi-mortarboard' },
        { title: 'IIT Madras Profile & Cutoffs', category: 'Guide', url: '/blog/iit-madras', icon: 'bi-mortarboard' },
        { title: 'NIT Trichy Profile & Cutoffs', category: 'Guide', url: '/blog/nit-trichy', icon: 'bi-mortarboard' },
        { title: 'NIT Surathkal Profile & Cutoffs', category: 'Guide', url: '/blog/nit-surathkal', icon: 'bi-mortarboard' },
        { title: 'NIT Warangal Profile & Cutoffs', category: 'Guide', url: '/blog/nit-warangal', icon: 'bi-mortarboard' },
        { title: 'Counseling Methodology & Transparency', category: 'About', url: '/about', icon: 'bi-info-circle' },
        { title: 'Contact Counseling Desk', category: 'Support', url: '/contact', icon: 'bi-envelope' }
    ];

    function initSpotlight() {
        const modal = document.getElementById('cmd-palette-modal');
        const input = document.getElementById('cmd-palette-input');
        const list = document.getElementById('cmd-palette-list');
        if (!modal || !input || !list) return;

        let activeIndex = 0;
        let filteredItems = [...spotlightItems];

        function renderItems(items) {
            filteredItems = items;
            list.innerHTML = '';
            if (items.length === 0) {
                list.innerHTML = `<div class="cmd-empty">No matching colleges, predictors, or guides found.</div>`;
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

        function openSpotlight() {
            modal.classList.add('open');
            window.openAppleSheet();
            input.value = '';
            activeIndex = 0;
            renderItems(spotlightItems);
            setTimeout(() => input.focus(), 60);
        }

        function closeSpotlight() {
            modal.classList.remove('open');
            window.closeAppleSheet();
        }

        // Global hotkeys: Ctrl+K / Cmd+K
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                if (modal.classList.contains('open')) {
                    closeSpotlight();
                } else {
                    openSpotlight();
                }
            } else if (e.key === 'Escape' && modal.classList.contains('open')) {
                closeSpotlight();
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
            btn.addEventListener('click', openSpotlight);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeSpotlight();
        });

        input.addEventListener('input', () => {
            const q = input.value.toLowerCase().trim();
            const matches = spotlightItems.filter(item =>
                item.title.toLowerCase().includes(q) ||
                item.category.toLowerCase().includes(q)
            );
            activeIndex = 0;
            renderItems(matches);
        });
    }

    // ==========================================
    // 4. Fluid Morphing Segmented Pill Controls
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
    // 5. Physics-Based Ease-Out Number Rollers
    // ==========================================
    function initNumberRollers() {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    obs.unobserve(el);
                    const target = parseInt(el.getAttribute('data-count'), 10);
                    if (isNaN(target)) return;

                    const duration = 1500;
                    const startTime = performance.now();

                    function updateNumber(now) {
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // SwiftUI fluid cubic ease-out
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
        }, { threshold: 0.15 });

        document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
    }

    // ==========================================
    // 6. Scroll-Triggered Reveal (Apple Spatial Entrance)
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
    // 7. Dynamic Dock Mobile Navigation Toggle
    // ==========================================
    function initDynamicDock() {
        const trigger = document.getElementById('dockMobileTrigger');
        const nav = document.getElementById('dockNav');
        const backdrop = document.getElementById('dockBackdrop');

        if (trigger && nav) {
            function toggleMenu(forceClose = false) {
                const isOpen = forceClose ? false : !nav.classList.contains('mobile-open');
                nav.classList.toggle('mobile-open', isOpen);
                if (backdrop) backdrop.classList.toggle('active', isOpen);
                trigger.innerHTML = isOpen ? '<i class="bi bi-x-lg"></i>' : '<i class="bi bi-list"></i>';
                trigger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
                document.body.classList.toggle('mobile-menu-open', isOpen);
            }

            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleMenu();
            });

            if (backdrop) {
                backdrop.addEventListener('click', () => toggleMenu(true));
            }

            nav.querySelectorAll('.dock-item-link').forEach(link => {
                link.addEventListener('click', () => toggleMenu(true));
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && nav.classList.contains('mobile-open')) {
                    toggleMenu(true);
                }
            });

            window.addEventListener('resize', () => {
                if (window.innerWidth > 992 && nav.classList.contains('mobile-open')) {
                    toggleMenu(true);
                }
            });
        }
    }

    // ==========================================
    // 8. Real-Time Spec Table Sorting & In-place Filtering
    // ==========================================
    window.initTableUtilities = function (tableId, filterInputId = null) {
        const table = document.getElementById(tableId);
        if (!table) return;

        // Column Sorting with Apple HIG Chevrons
        const headers = table.querySelectorAll('th[data-sortable]');
        headers.forEach(header => {
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

        // In-place Live Filter
        if (filterInputId) {
            const input = document.getElementById(filterInputId);
            if (input) {
                input.addEventListener('input', () => {
                    const query = input.value.toLowerCase().trim();
                    const rows = table.querySelectorAll('tbody tr');
                    rows.forEach(row => {
                        const match = row.textContent.toLowerCase().includes(query);
                        row.style.display = match ? '' : 'none';
                    });
                });
            }
        }
    };

    // ==========================================
    // 9. Apple Theme Manager (Light / Dark HIG)
    // ==========================================
    function initThemeManager() {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');

        function applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            if (themeIcon) {
                if (theme === 'light') {
                    themeIcon.className = 'bi bi-moon-stars-fill';
                    if (themeToggle) themeToggle.setAttribute('title', 'Switch to Dark Mode');
                } else {
                    themeIcon.className = 'bi bi-sun-fill';
                    if (themeToggle) themeToggle.setAttribute('title', 'Switch to Light Mode');
                }
            }
            window.dispatchEvent(new CustomEvent('themechanged', { detail: { theme } }));
        }

        const initialTheme = document.documentElement.getAttribute('data-theme') || localStorage.getItem('theme') || 'dark';
        applyTheme(initialTheme);

        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.preventDefault();
                const active = document.documentElement.getAttribute('data-theme') || 'dark';
                const next = active === 'dark' ? 'light' : 'dark';
                localStorage.setItem('theme', next);
                applyTheme(next);
            });
        }
    }

    // DOM Ready initialization
    document.addEventListener('DOMContentLoaded', () => {
        initThemeManager();
        initSpotlight();
        initDynamicDock();
        initSegmentedControls();
        initNumberRollers();
        initScrollReveals();
    });

})();
