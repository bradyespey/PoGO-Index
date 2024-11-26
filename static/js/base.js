// static/js/base.js

document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('darkModeToggle');
    const darkModeText = document.getElementById('darkModeText');
    const prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
    let currentTheme = localStorage.getItem('theme');

    // Apply the initial theme based on user preference or system setting
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-mode');
        darkModeText.textContent = 'Light Mode';
    } else if (currentTheme === 'light') {
        document.body.classList.remove('dark-mode');
        darkModeText.textContent = 'Dark Mode';
    } else if (prefersDarkScheme.matches) {
        document.body.classList.add('dark-mode');
        darkModeText.textContent = 'Light Mode';
    }

    // Toggle dark mode on click
    toggle.addEventListener('click', function (e) {
        e.preventDefault();
        if (document.body.classList.contains('dark-mode')) {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
            darkModeText.textContent = 'Dark Mode';
        } else {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
            darkModeText.textContent = 'Light Mode';
        }
    });
});