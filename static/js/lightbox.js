// Image lightbox functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create lightbox elements
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox__overlay"></div>
        <div class="lightbox__content">
            <img class="lightbox__image" src="" alt="">
            <button class="lightbox__close" aria-label="Close lightbox">&times;</button>
        </div>
    `;
    document.body.appendChild(lightbox);

    const lightboxImage = lightbox.querySelector('.lightbox__image');
    const lightboxClose = lightbox.querySelector('.lightbox__close');
    const lightboxOverlay = lightbox.querySelector('.lightbox__overlay');

    // Find all images in article content
    const contentImages = document.querySelectorAll('.content img');
    
    contentImages.forEach(img => {
        // Make images clickable
        img.style.cursor = 'pointer';
        img.setAttribute('role', 'button');
        img.setAttribute('tabindex', '0');
        
        // Click to open
        img.addEventListener('click', function() {
            lightboxImage.src = this.src;
            lightboxImage.alt = this.alt;
            lightbox.classList.add('lightbox--active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        });

        // Keyboard support (Enter key)
        img.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                lightboxImage.src = this.src;
                lightboxImage.alt = this.alt;
                lightbox.classList.add('lightbox--active');
                document.body.style.overflow = 'hidden';
            }
        });
    });

    // Close lightbox function
    function closeLightbox() {
        lightbox.classList.remove('lightbox--active');
        document.body.style.overflow = ''; // Restore scrolling
    }

    // Close on button click
    lightboxClose.addEventListener('click', closeLightbox);

    // Close on overlay click
    lightboxOverlay.addEventListener('click', closeLightbox);

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && lightbox.classList.contains('lightbox--active')) {
            closeLightbox();
        }
    });
});
