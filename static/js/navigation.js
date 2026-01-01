/**
 * Mobile Navigation Toggle
 * Handles hamburger menu functionality for responsive navigation
 */

(function() {
    'use strict';

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        const menuToggle = document.querySelector('.menu-toggle');
        const navMenu = document.querySelector('.header-menu');
        const header = document.querySelector('header');

        if (!menuToggle || !navMenu) {
            return;
        }

        /**
         * Toggle mobile menu open/closed
         */
        function toggleMenu() {
            const isOpen = navMenu.classList.contains('is-open');
            
            if (isOpen) {
                closeMenu();
            } else {
                openMenu();
            }
        }

        /**
         * Open the mobile menu
         */
        function openMenu() {
            navMenu.classList.add('is-open');
            menuToggle.classList.add('is-active');
            menuToggle.setAttribute('aria-expanded', 'true');
            
            // Add event listener to close menu when clicking outside
            setTimeout(() => {
                document.addEventListener('click', handleOutsideClick);
            }, 0);
        }

        /**
         * Close the mobile menu
         */
        function closeMenu() {
            navMenu.classList.remove('is-open');
            menuToggle.classList.remove('is-active');
            menuToggle.setAttribute('aria-expanded', 'false');
            
            // Remove outside click listener
            document.removeEventListener('click', handleOutsideClick);
        }

        /**
         * Handle clicks outside the menu
         */
        function handleOutsideClick(event) {
            if (!header.contains(event.target)) {
                closeMenu();
            }
        }

        /**
         * Close menu when clicking on a navigation link (for single-page navigation)
         */
        const navLinks = navMenu.querySelectorAll('.header-menu__item');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                // Small delay to allow navigation to occur
                setTimeout(closeMenu, 150);
            });
        });

        // Add click event to hamburger button
        menuToggle.addEventListener('click', function(event) {
            event.stopPropagation();
            toggleMenu();
        });

        // Close menu on window resize if open (prevents issues when resizing)
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth > 600 && navMenu.classList.contains('is-open')) {
                    closeMenu();
                }
            }, 250);
        });
    });
})();

