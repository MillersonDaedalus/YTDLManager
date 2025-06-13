// Get the theme toggle button
const themeToggle = document.getElementById('theme-toggle');

// Function to toggle the theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        themeToggle.textContent = 'Toggle Dark Mode';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        themeToggle.textContent = 'Toggle Light Mode';
    }
}

// Add event listener to the toggle button
themeToggle.addEventListener('click', toggleTheme);

// Load the user's preferred theme on page load
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.textContent = savedTheme === 'dark' ? 'Toggle Light Mode' : 'Toggle Dark Mode';
}

// Call the loadTheme function when the page loads
window.addEventListener('load', loadTheme);