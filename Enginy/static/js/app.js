document.getElementById('analyzeEngineBtn')?.addEventListener('click', function() {
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
        document.getElementById('engineAnalysisResult').innerText = data.result;
    })
    .catch(error => {
        alert(error.message);
    });
});
