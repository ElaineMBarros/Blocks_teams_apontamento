// Initialize Microsoft Teams SDK
let teamsContext = null;
let timeEntries = [];

// Load entries from localStorage
function loadEntries() {
    const stored = localStorage.getItem('timeEntries');
    if (stored) {
        timeEntries = JSON.parse(stored);
    }
}

// Save entries to localStorage
function saveEntries() {
    localStorage.setItem('timeEntries', JSON.stringify(timeEntries));
}

// Initialize Teams
async function initializeTeams() {
    try {
        await microsoftTeams.app.initialize();
        
        // Get Teams context
        teamsContext = await microsoftTeams.app.getContext();
        
        console.log('Teams context:', teamsContext);
        
        // Display user information
        const userInfo = document.getElementById('userInfo');
        if (teamsContext.user) {
            userInfo.innerHTML = `
                <p>👤 <strong>${teamsContext.user.displayName || teamsContext.user.userPrincipalName}</strong></p>
                <p style="font-size: 12px; color: #8a8886;">Tema: ${teamsContext.app.theme || 'default'}</p>
            `;
        }
        
        // Listen for theme changes
        microsoftTeams.app.registerOnThemeChangeHandler((theme) => {
            updateTheme(theme);
        });
        
        // Notify Teams that the app loaded successfully
        microsoftTeams.app.notifySuccess();
        
    } catch (error) {
        console.error('Error initializing Teams:', error);
        // If not running in Teams, still allow the app to work
        const userInfo = document.getElementById('userInfo');
        userInfo.innerHTML = '<p>⚠️ Executando fora do Microsoft Teams (modo de desenvolvimento)</p>';
    }
}

// Update theme based on Teams theme
function updateTheme(theme) {
    const root = document.documentElement;
    if (theme === 'dark') {
        root.style.setProperty('--bg-color', '#1f1f1f');
        root.style.setProperty('--text-color', '#ffffff');
    } else if (theme === 'contrast') {
        root.style.setProperty('--bg-color', '#000000');
        root.style.setProperty('--text-color', '#ffffff');
    } else {
        root.style.setProperty('--bg-color', '#f5f5f5');
        root.style.setProperty('--text-color', '#252423');
    }
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Render time entries
function renderEntries() {
    const entriesList = document.getElementById('entriesList');
    
    if (timeEntries.length === 0) {
        entriesList.innerHTML = '<p class="empty-message">Nenhum apontamento registrado ainda.</p>';
        return;
    }
    
    // Sort entries by date (most recent first)
    const sortedEntries = [...timeEntries].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    entriesList.innerHTML = sortedEntries.map(entry => `
        <div class="entry-item">
            <div class="entry-header">
                <div class="entry-project">${entry.project}</div>
                <div class="entry-hours">${entry.hours}h</div>
            </div>
            <div class="entry-date">📅 ${formatDate(entry.date)}</div>
            <div class="entry-description">${entry.description}</div>
        </div>
    `).join('');
}

// Update summary
function updateSummary() {
    const totalHours = timeEntries.reduce((sum, entry) => sum + parseFloat(entry.hours), 0);
    document.getElementById('totalHours').textContent = `${totalHours.toFixed(1)}h`;
    document.getElementById('totalEntries').textContent = timeEntries.length;
}

// Handle form submission
function handleFormSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const entry = {
        id: Date.now(),
        date: formData.get('date'),
        hours: parseFloat(formData.get('hours')),
        project: formData.get('project'),
        description: formData.get('description'),
        user: teamsContext?.user?.displayName || 'Usuário'
    };
    
    timeEntries.push(entry);
    saveEntries();
    renderEntries();
    updateSummary();
    
    // Reset form
    event.target.reset();
    
    // Set today's date as default
    document.getElementById('date').valueAsDate = new Date();
    
    // Show success message (optional)
    console.log('Apontamento adicionado:', entry);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize Teams SDK
    await initializeTeams();
    
    // Load saved entries
    loadEntries();
    
    // Set today's date as default
    const dateInput = document.getElementById('date');
    dateInput.valueAsDate = new Date();
    
    // Render initial state
    renderEntries();
    updateSummary();
    
    // Setup form handler
    const form = document.getElementById('timeForm');
    form.addEventListener('submit', handleFormSubmit);
});
