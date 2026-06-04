/**
 * Dark Mode Toggle
 * Manages light/dark theme switching with localStorage persistence
 */

(function() {
    'use strict';

    const THEME_KEY = 'theme';
    const THEME_LIGHT = 'light';
    const THEME_DARK = 'dark';


    function getSavedTheme() {
        return localStorage.getItem(THEME_KEY) || THEME_LIGHT;
    }


    function saveTheme(theme) {
        localStorage.setItem(THEME_KEY, theme);
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }


    function updateToggleButton(theme) {
        const toggleButton = document.querySelector('.theme-toggle');
        if (!toggleButton) return;

        const lightText = toggleButton.querySelector('.theme-toggle__text--light');
        const darkText = toggleButton.querySelector('.theme-toggle__text--dark');

        if (theme === THEME_DARK) {
            // In dark mode, show "Light Mode" button (to switch back to light)
            lightText.classList.add('active');
            darkText.classList.remove('active');
            toggleButton.setAttribute('aria-label', 'Switch to light mode');
        } else {
            // In light mode, show "Dark Mode" button (to switch to dark)
            lightText.classList.remove('active');
            darkText.classList.add('active');
            toggleButton.setAttribute('aria-label', 'Switch to dark mode');
        }
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const currentTheme = getSavedTheme();
        const newTheme = currentTheme === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
        
        applyTheme(newTheme);
        saveTheme(newTheme);
        updateToggleButton(newTheme);
    }

    /**
     * Initialize theme on page load (before DOM ready to prevent flash)
     */
    function initTheme() {
        const savedTheme = getSavedTheme();
        applyTheme(savedTheme);
    }

    // Apply theme immediately (before DOM ready to prevent flash)
    initTheme();

    // Wait for DOM to be ready for button interactions
    document.addEventListener('DOMContentLoaded', function() {
        const toggleButton = document.querySelector('.theme-toggle');
        
        if (!toggleButton) {
            return;
        }

        const currentTheme = getSavedTheme();
        updateToggleButton(currentTheme);

        // Add click event listener
        toggleButton.addEventListener('click', function(event) {
            event.preventDefault();
            toggleTheme();
        });

        // Add keyboard support for accessibility (Enter and Space)
        toggleButton.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                toggleTheme();
            }
        });
    });
})();

