document.addEventListener('DOMContentLoaded', function () {
   // Initialize all components
   initFloatingTriangles();
});
document.querySelectorAll('.nav-link').forEach(link => {
   link.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');

      // Só aplicar o scroll se o link for uma âncora interna (#alguma-coisa)
      if (targetId && targetId.startsWith('#')) {
         e.preventDefault();
         const targetSection = document.querySelector(targetId);

         if (targetSection) {
            const nav = document.querySelector('.hub-nav') || document.querySelector('#navbar');
            const navHeight = nav ? nav.offsetHeight : 0;
            const targetPosition = targetSection.offsetTop - navHeight - 20;

            window.scrollTo({
               top: targetPosition,
               behavior: 'smooth'
            });
         }
      }
      // se o link for uma URL normal, deixa o comportamento padrão
   });
});
// ===== FLOATING TRIANGLES BACKGROUND =====
function initFloatingTriangles() {
   const container = document.getElementById('floating-triangles');

   // Create floating triangles
   for (let i = 0; i < 8; i++) {
      const triangle = document.createElement('div');
      triangle.className = 'triangle';

      // Random positioning and sizing
      const size = Math.random() * 30 + 20;
      const x = Math.random() * 100;
      const y = Math.random() * 100;
      const delay = Math.random() * 6;

      triangle.style.cssText = `
            left: ${x}%;
            top: ${y}%;
            border-left: ${size / 2}px solid transparent;
            border-right: ${size / 2}px solid transparent;
            border-bottom: ${size * 0.866}px solid hsl(0, 84%, 60%);
            animation-delay: ${delay}s;
        `;

      container.appendChild(triangle);
   }
}

// News Carousel
const newsTrack = document.querySelector('.news-track');
const prevBtn = document.querySelector('.carousel-control.prev');
const nextBtn = document.querySelector('.carousel-control.next');
const newsCards = document.querySelectorAll('.news-card');

let currentIndex = 0;
const cardWidth = 400; // flex-basis width
const gap = 32; // 2rem gap
const totalCards = newsCards.length;

function updateCarousel() {
   const offset = currentIndex * (cardWidth + gap);
   newsTrack.style.transform = `translateX(-${offset}px)`;
}

prevBtn.addEventListener('click', () => {
   if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
   }
});

nextBtn.addEventListener('click', () => {
   const maxIndex = totalCards - Math.floor(window.innerWidth / (cardWidth + gap));
   if (currentIndex < maxIndex && currentIndex < totalCards - 1) {
      currentIndex++;
      updateCarousel();
   }
});

// Auto-scroll carousel
let autoScrollInterval = setInterval(() => {
   const maxIndex = totalCards - Math.floor(window.innerWidth / (cardWidth + gap));
   if (currentIndex < maxIndex && currentIndex < totalCards - 1) {
      currentIndex++;
      updateCarousel();
   } else {
      currentIndex = 0;
      updateCarousel();
   }
}, 5000);

// Pause auto-scroll on hover
document.querySelector('.carousel-wrapper').addEventListener('mouseenter', () => {
   clearInterval(autoScrollInterval);
});

document.querySelector('.carousel-wrapper').addEventListener('mouseleave', () => {
   autoScrollInterval = setInterval(() => {
      const maxIndex = totalCards - Math.floor(window.innerWidth / (cardWidth + gap));
      if (currentIndex < maxIndex && currentIndex < totalCards - 1) {
         currentIndex++;
         updateCarousel();
      } else {
         currentIndex = 0;
         updateCarousel();
      }
   }, 5000);
});

// // Active Navigation Link on Scroll
// const sections = document.querySelectorAll('.hub-section');
// const navLinks = document.querySelectorAll('.nav-link');

// function setActiveLink() {
//    let currentSection = '';
//    const navHeight = document.querySelector('.hub-nav').offsetHeight;

//    sections.forEach(section => {
//       const sectionTop = section.offsetTop - navHeight - 50;
//       const sectionHeight = section.offsetHeight;

//       if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
//          currentSection = section.getAttribute('id');
//       }
//    });

//    navLinks.forEach(link => {
//       link.style.color = '';
//       if (link.getAttribute('href') === `#${currentSection}`) {
//          link.style.color = 'var(--primary-color)';
//       }
//    });
// }

// window.addEventListener('scroll', setActiveLink);

// Responsive carousel adjustment
window.addEventListener('resize', () => {
   currentIndex = 0;
   updateCarousel();
});
