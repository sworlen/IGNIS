const themeToggleButton = document.getElementById('theme-toggle');

if (themeToggleButton) {
    themeToggleButton.addEventListener('click', () => {
        const htmlElement = document.documentElement;
        htmlElement.classList.toggle('dark');
        const isDark = htmlElement.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}
