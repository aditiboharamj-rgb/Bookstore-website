/**
 * Book Nest - Main JavaScript Client & PWA Controller
 * Handles Async Cart Actions, Favorite Toggling, Toast Notifications,
 * Search, and Service Worker Registration
 */

// Global CSRF helper for Django POST requests
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Toast Notification System
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-item toast-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button style="background:none;border:none;cursor:pointer;margin-left:auto;color:#888;" onclick="this.parentElement.remove()">&times;</button>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}

// Mobile Navigation Drawer Toggle
document.addEventListener('DOMContentLoaded', () => {
  const hamburgerBtn = document.getElementById('hamburger-btn');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const drawerOverlay = document.getElementById('drawer-overlay');
  const closeDrawerBtn = document.getElementById('close-drawer-btn');

  function toggleDrawer() {
    mobileDrawer?.classList.toggle('open');
    drawerOverlay?.classList.toggle('active');
  }

  hamburgerBtn?.addEventListener('click', toggleDrawer);
  drawerOverlay?.addEventListener('click', toggleDrawer);
  closeDrawerBtn?.addEventListener('click', toggleDrawer);

  // Async Cart Add / Remove
  document.querySelectorAll('.ajax-add-cart').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const bookId = btn.dataset.bookId;
      const url = `/cart/add/${bookId}/`;
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: new URLSearchParams({ quantity: 1 })
        });
        const data = await res.json();
        if (data.success) {
          // Update cart badge
          const badges = document.querySelectorAll('.cart-badge');
          badges.forEach(b => b.textContent = data.cart_count);
          showToast(data.message || 'Added to cart successfully!');
        }
      } catch (err) {
        console.error(err);
      }
    });
  });

  // Async Favorite Toggle
  document.querySelectorAll('.ajax-toggle-fav').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const bookId = btn.dataset.bookId;
      const url = `/favorites/toggle/${bookId}/`;
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
          }
        });
        const data = await res.json();
        const icon = btn.querySelector('i');
        if (data.favorited) {
          btn.classList.add('active');
          if (icon) {
            icon.classList.remove('bi-heart');
            icon.classList.add('bi-heart-fill');
            icon.style.color = '#e11d48';
          }
        } else {
          btn.classList.remove('active');
          if (icon) {
            icon.classList.remove('bi-heart-fill');
            icon.classList.add('bi-heart');
            icon.style.color = '';
          }
        }
        // Update favorite badges
        const favBadges = document.querySelectorAll('.fav-badge');
        favBadges.forEach(b => b.textContent = data.fav_count);
        showToast(data.message);
      } catch (err) {
        console.error(err);
      }
    });
  });

  // Register PWA Service Worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('Service Worker Registered for Book Nest', reg))
      .catch(err => console.warn('SW registration failed: ', err));
  }
});

// Hero Banner Slider Controller
let currentHeroSlide = 0;
function showHeroSlide(index) {
  const slides = document.querySelectorAll('.hero-slide');
  const dots = document.querySelectorAll('.hero-dot');
  if (!slides.length) return;
  
  if (index >= slides.length) currentHeroSlide = 0;
  else if (index < 0) currentHeroSlide = slides.length - 1;
  else currentHeroSlide = index;

  slides.forEach((s, idx) => {
    s.classList.toggle('active', idx === currentHeroSlide);
  });
  dots.forEach((d, idx) => {
    d.classList.toggle('active', idx === currentHeroSlide);
  });
}

function changeHeroSlide(dir) {
  showHeroSlide(currentHeroSlide + dir);
}

function goToHeroSlide(idx) {
  showHeroSlide(idx);
}

// Auto-advance hero banner every 6 seconds
setInterval(() => {
  const slides = document.querySelectorAll('.hero-slide');
  if (slides.length > 1) {
    changeHeroSlide(1);
  }
}, 6000);

