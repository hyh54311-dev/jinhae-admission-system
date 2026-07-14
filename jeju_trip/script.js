document.addEventListener('DOMContentLoaded', () => {
    const dayButtons = document.querySelectorAll('.day-btn');
    const daySections = document.querySelectorAll('.day-section');

    dayButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const day = btn.getAttribute('data-day');

            // Update buttons
            dayButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update sections with a simple fade effect
            daySections.forEach(section => {
                section.classList.add('hidden');
                if (section.id === `day-${day}`) {
                    section.classList.remove('hidden');
                    // Trigger a reflow for animation if needed
                    section.style.opacity = 0;
                    setTimeout(() => {
                        section.style.transition = 'opacity 0.4s ease';
                        section.style.opacity = 1;
                    }, 10);
                }
            });
        });
    });

    // Simple reveal animation on scroll for info cards
    const cards = document.querySelectorAll('.info-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s cubic-bezier(0.23, 1, 0.32, 1)';
        observer.observe(card);
    });
});
