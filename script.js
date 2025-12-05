document.addEventListener('DOMContentLoaded', function() {
    // Мобильное меню
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Закрытие меню при клике на ссылку
    document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }));

    // Активная навигация
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section');
    
    function changeActiveNav() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= (sectionTop - 200)) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}` || 
                (current === '' && link.getAttribute('href') === '#hero')) {
                link.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', changeActiveNav);

    // Анимация цифр статистики
    const statNumbers = document.querySelectorAll('.stat-number');
    if (statNumbers.length > 0) {
        const animateStats = () => {
            statNumbers.forEach(stat => {
                const target = +stat.getAttribute('data-target');
                const count = +stat.innerText;
                const increment = target / 100;
                
                if (count < target) {
                    stat.innerText = Math.ceil(count + increment);
                    setTimeout(animateStats, 20);
                } else {
                    stat.innerText = target;
                }
            });
        };
        
        // Запуск при скролле до секции
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateStats();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        document.querySelectorAll('.stats, .hero-stats').forEach(el => observer.observe(el));
    }

    // Табы для факультетов
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-tab');
                
                // Убираем активные классы
                tabBtns.forEach(b => b.classList.remove('active'));
                tabPanes.forEach(p => p.classList.remove('active'));
                
                // Добавляем активные классы
                btn.classList.add('active');
                document.getElementById(tabId).classList.add('active');
            });
        });
    }

    // Фильтрация университетов на главной
    const filterBtns = document.querySelectorAll('.filter-btn');
    const uniCards = document.querySelectorAll('.university-card');
    
    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const filter = btn.getAttribute('data-filter');
                
                // Активная кнопка
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Фильтрация карточек
                uniCards.forEach(card => {
                    const categories = card.getAttribute('data-category');
                    if (filter === 'all' || categories.includes(filter)) {
                        card.style.display = 'block';
                        setTimeout(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        }, 100);
                    } else {
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(20px)';
                        setTimeout(() => {
                            card.style.display = 'none';
                        }, 300);
                    }
                });
            });
        });
    }

    // Поиск университетов
    const searchInput = document.getElementById('uni-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            
            uniCards.forEach(card => {
                const name = card.querySelector('.uni-name').textContent.toLowerCase();
                const desc = card.querySelector('.uni-desc').textContent.toLowerCase();
                
                if (name.includes(searchTerm) || desc.includes(searchTerm)) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    }

    // Форма контактов
    const contactForm = document.getElementById('sync-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ОТПРАВЛЯЕМ...';
            submitBtn.disabled = true;
            
            // Имитация отправки
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="fas fa-check"></i> ОТПРАВЛЕНО!';
                submitBtn.style.background = 'var(--eva-green)';
                
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.background = '';
                    contactForm.reset();
                }, 2000);
            }, 1500);
        });
    }

    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Анимация появления элементов при скролле
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.about-card, .secret-card, .university-card, .timeline-item');
        
        elements.forEach(el => {
            const elementTop = el.getBoundingClientRect().top;
            const elementVisible = 150;
            
            if (elementTop < window.innerHeight - elementVisible) {
                el.classList.add('animated');
            }
        });
    };
    
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Запуск при загрузке
});

// Анимация счетчиков
function animateCounter(element, start, end, duration, suffix = '') {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value + suffix;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Запуск анимации при прокрутке до статистики
function initCounters() {
    const counters = document.querySelectorAll('.stat-number[data-target]');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const suffix = counter.textContent.includes('%') ? '%' : 
                             counter.textContent.includes('+') ? '+' : '';
                
                // Сначала ставим 0
                counter.textContent = '0' + suffix;
                
                // Запускаем анимацию
                setTimeout(() => {
                    animateCounter(counter, 0, target, 2000, suffix);
                }, 300);
                
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

// Для статистики на главной без data-target
function initHeroStats() {
    const heroStats = document.querySelectorAll('.hero-stats .stat-number');
    const values = {
        '120+': 120,
        '5000+': 5000,
        '95%': 95,
        '1000+': 1000,
        '24/7': 24,
        '98%': 98
    };
    
    heroStats.forEach(stat => {
        const originalText = stat.textContent.trim();
        const target = values[originalText];
        
        if (target && !stat.classList.contains('animated')) {
            stat.classList.add('animated');
            const suffix = originalText.includes('%') ? '%' : 
                          originalText.includes('+') ? '+' : '';
            
            // Анимируем только если есть число
            if (!isNaN(parseInt(target))) {
                stat.textContent = '0' + suffix;
                setTimeout(() => {
                    animateCounter(stat, 0, target, 1500, suffix);
                }, 500);
            } else {
                // Для "24/7" просто показываем как есть
                stat.textContent = originalText;
            }
        }
    });
}

// Запускаем при загрузке и скролле
document.addEventListener('DOMContentLoaded', function() {
    initCounters();
    initHeroStats();
});

