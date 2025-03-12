// Theme switcher functionality
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        setTheme(systemPrefersDark ? 'dark' : 'light');
    }
    
    document.getElementById('theme-switch')?.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
    
    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        const lightIcon = document.querySelector('.theme-icon-light');
        const darkIcon = document.querySelector('.theme-icon-dark');
        
        if (theme === 'dark') {
            lightIcon.classList.add('d-none');
            darkIcon.classList.remove('d-none');
            document.body.classList.add('dark-theme');
        } else {
            lightIcon.classList.remove('d-none');
            darkIcon.classList.add('d-none');
            document.body.classList.remove('dark-theme');
        }
        
        updatePlotlyTheme(theme);
    }
    
    function updatePlotlyTheme(theme) {
        if (window.Plotly) {
            const plots = document.querySelectorAll('[id^="plotly"]');
            plots.forEach(plot => {
                if (plot._fullLayout) {
                    const newLayout = {
                        template: theme === 'dark' ? 'plotly_dark' : 'plotly',
                        paper_bgcolor: theme === 'dark' ? '#1e1e1e' : '#ffffff',
                        plot_bgcolor: theme === 'dark' ? '#1e1e1e' : '#ffffff',
                        font: {
                            color: theme === 'dark' ? '#e0e0e0' : '#2c3e50'
                        }
                    };
                    Plotly.relayout(plot, newLayout);
                }
            });
        }
    }
    
    document.getElementById('analyzeEngineBtn')?.addEventListener('click', function() {
        const resultContainer = document.getElementById('engineAnalysisResult');
        if (resultContainer) {
            resultContainer.innerHTML = '<div class="text-center"><i class="fas fa-cog fa-spin fa-3x my-3"></i><p>Wykonywanie analizy...</p></div>';
        }
        
        fetch('/analyze_engine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error); });
            }
            return response.json();
        })
        .then(data => {
            if (resultContainer) {
                resultContainer.innerHTML = '';
                const graphDiv = document.createElement('div');
                graphDiv.id = 'plotly-engine-analysis';
                graphDiv.style.height = '500px';
                resultContainer.appendChild(graphDiv);
                
                const currentTheme = document.documentElement.getAttribute('data-bs-theme');
                
                // Ustaw właściwości wykresu zgodnie z motywem
                if (data.layout) {
                    data.layout.template = currentTheme === 'dark' ? 'plotly_dark' : 'plotly';
                    data.layout.paper_bgcolor = currentTheme === 'dark' ? '#1e1e1e' : '#ffffff';
                    data.layout.plot_bgcolor = currentTheme === 'dark' ? '#1e1e1e' : '#ffffff';
                    data.layout.font = {
                        color: currentTheme === 'dark' ? '#e0e0e0' : '#2c3e50'
                    };
                }
                
                Plotly.newPlot('plotly-engine-analysis', data.data, data.layout);
            }
        })
        .catch(error => {
            if (resultContainer) {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i> ${error.message}
                    </div>`;
            }
        });
    });
    
    // Handle sidebar toggle on mobile
    $('.sidebar-dropdown > a').click(function() {
        $(this).next('.sidebar-submenu').slideToggle(200);
        $(this).parent().toggleClass('active');
        return false;
    });
    
    // Toggle sidebar on mobile
    $('.navbar-toggler').click(function() {
        $('body').toggleClass('sidebar-mobile-open');
    });
    
    // Auto-dismiss flash messages
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 4000);
});

// Function to download analysis data
function downloadAnalysisData(format = 'json') {
    // Placeholder for export functionality
    alert('Funkcja eksportu danych zostanie zaimplementowana w przyszłej aktualizacji.');
}
