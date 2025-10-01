  // click row navigate
  $(function(){
    $('*[data-href]').on('click', function(){ window.location = $(this).data('href'); });
  });

  // Smooth scroll for TOC clicks
  document.querySelectorAll('#detail-toc a').forEach(function(link){
    link.addEventListener('click', function(e){
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) target.scrollIntoView({behavior:'smooth', block:'start'});
    });
  });

  // Enhanced TOC highlighting with better logic
  const tocLinks = document.querySelectorAll('#detail-toc a');
  const sections = document.querySelectorAll('section[id^="section-"]');

  // Modern scroll-based approach (more reliable than IntersectionObserver for TOC)
  function updateActiveSection() {
    const scrollPosition = window.scrollY + 20; // minimal offset

    let activeSection = null;
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionBottom = sectionTop + section.offsetHeight;

      if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
        activeSection = section;
      }
    });

    // Fallback: if no section is active, use the last visible one
    if (!activeSection) {
      for (let i = sections.length - 1; i >= 0; i--) {
        if (scrollPosition >= sections[i].offsetTop) {
          activeSection = sections[i];
          break;
        }
      }
    }

    // Update TOC highlighting
    tocLinks.forEach(link => link.classList.remove('active'));
    if (activeSection) {
      const activeLink = document.querySelector(`#detail-toc a[href="#${activeSection.id}"]`);
      if (activeLink) activeLink.classList.add('active');
    }
  }

  // Throttled scroll listener for better performance
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        updateActiveSection();
        ticking = false;
      });
      ticking = true;
    }
  });

  // Initial call
  updateActiveSection();

  // Format authorized capital with thousand separators
  document.addEventListener('DOMContentLoaded', function() {
    const cap = document.getElementById('capital-badge');
    if (cap) {
      const text = cap.textContent;
      const match = text.match(/(\d+)\s*₽/);
      if (match) {
        const number = match[1];
        const formatted = number.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        cap.innerHTML = text.replace(number, formatted);
      }
    }

    // format deal amounts
    document.querySelectorAll('.deal-amount').forEach(el => {
      const text = el.textContent;
      const m = text.match(/(\d+)\s*₽/);
      if (m){
        const n = m[1].replace(/\D/g,'');
        const fmt = n.replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        el.innerHTML = text.replace(m[1], fmt);
      }
    });

    // Функция для подсветки найденного текста в сделках
    function highlightDealText(element, query, className = 'highlight') {
      if (!query || query.length < 2) {
        removeDealHighlight(element);
        return;
      }

      const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
      );

      const textNodes = [];
      let node;
      while (node = walker.nextNode()) {
        textNodes.push(node);
      }

      textNodes.forEach(textNode => {
        const text = textNode.textContent;
        const regex = new RegExp(`(${query})`, 'gi');

        if (regex.test(text)) {
          const highlightedText = text.replace(regex, `<mark class="${className}">$1</mark>`);
          const wrapper = document.createElement('span');
          wrapper.innerHTML = highlightedText;
          textNode.parentNode.replaceChild(wrapper, textNode);
        }
      });
    }

    // Функция для удаления подсветки в сделках
    function removeDealHighlight(element) {
      const highlights = element.querySelectorAll('mark.highlight');
      highlights.forEach(mark => {
        const parent = mark.parentNode;
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
      });
    }

    // Фильтрация сделок
    function filterDeals() {
      const numberQuery = document.getElementById('deal-number-filter')?.value.toLowerCase().trim() || '';
      const borrowerQuery = document.getElementById('deal-borrower-filter')?.value.toLowerCase().trim() || '';
      const roleQuery = document.getElementById('deal-role-filter')?.value.toLowerCase().trim() || '';

      const dealsContainer = document.getElementById('deals-container');
      if (!dealsContainer) return;

      const dealCards = dealsContainer.querySelectorAll('.deal-card');
      let visibleCount = 0;

      dealCards.forEach(card => {
        const dealNumber = card.getAttribute('data-deal-number') || '';
        const dealBorrowers = card.getAttribute('data-deal-borrowers') || '';
        const dealRoles = card.getAttribute('data-deal-roles') || '';

        const matchesNumber = !numberQuery || dealNumber.includes(numberQuery);
        const matchesBorrower = !borrowerQuery || dealBorrowers.includes(borrowerQuery);
        const matchesRole = !roleQuery || dealRoles.includes(roleQuery);

        if (matchesNumber && matchesBorrower && matchesRole) {
          card.style.display = '';
          visibleCount++;

          // Убираем предыдущую подсветку
          removeDealHighlight(card);

          // Добавляем подсветку для номера сделки
          if (numberQuery && numberQuery.length >= 2) {
            // Подсвечиваем в заголовке карточки "№ XXX"
            const titleElement = card.querySelector('h5.card-title');
            if (titleElement && titleElement.textContent.toLowerCase().includes(numberQuery)) {
              highlightDealText(titleElement, numberQuery);
            }

            // Подсвечиваем в правой части где "Номер XXX"
            const rightText = card.querySelector('.text-end small');
            if (rightText && rightText.textContent.toLowerCase().includes(numberQuery)) {
              highlightDealText(rightText, numberQuery);
            }
          }

          // Добавляем подсветку для заемщиков/должников
          if (borrowerQuery && borrowerQuery.length >= 2) {
            const borrowerBadges = card.querySelectorAll('.badge.bg-light');
            borrowerBadges.forEach(badge => {
              // Проверяем, что это именно бейдж должника (находится в блоке с "Должник:")
              const parentDiv = badge.closest('div');
              if (parentDiv && parentDiv.innerHTML.includes('Должник:')) {
                if (badge.textContent.toLowerCase().includes(borrowerQuery)) {
                  highlightDealText(badge, borrowerQuery);
                }
              }
            });
          }

        } else {
          card.style.display = 'none';
          // Убираем подсветку для скрытых карточек
          removeDealHighlight(card);
        }
      });
    }

    // Добавляем обработчики событий для фильтров сделок
    const dealNumberFilter = document.getElementById('deal-number-filter');
    const dealBorrowerFilter = document.getElementById('deal-borrower-filter');
    const dealRoleFilter = document.getElementById('deal-role-filter');

    if (dealNumberFilter) dealNumberFilter.addEventListener('input', filterDeals);
    if (dealBorrowerFilter) dealBorrowerFilter.addEventListener('input', filterDeals);
    if (dealRoleFilter) dealRoleFilter.addEventListener('change', filterDeals);
  });