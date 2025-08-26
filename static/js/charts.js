// static/js/charts.js - Real-time Chart Implementation
class QKDCharts {
    constructor() {
        this.eveChart = null;
        this.securityChart = null;
        this.initCharts();
    }
    
    initCharts() {
        // Eavesdropper Activity Chart
        const eveCtx = document.getElementById('eve-chart').getContext('2d');
        this.eveChart = new Chart(eveCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Attack Intensity',
                    data: [],
                    borderColor: '#FF5A5F',
                    backgroundColor: 'rgba(255, 90, 95, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 1 }
                }
            }
        });
        
        // Security Analysis Chart
        const secCtx = document.getElementById('security-chart').getContext('2d');
        this.securityChart = new Chart(secCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'QBER',
                    data: [],
                    borderColor: '#FF9D42',
                    backgroundColor: 'rgba(255, 157, 66, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 0, max: 0.2 }
                }
            }
        });
    }
    
    updateEveChart(activity) {
        const chart = this.eveChart;
        const data = chart.data;
        
        // Add new data point
        data.labels.push(data.labels.length);
        data.datasets[0].data.push(activity);
        
        // Keep only last 20 points
        if (data.labels.length > 20) {
            data.labels.shift();
            data.datasets[0].data.shift();
        }
        
        chart.update('none');
    }
    
    updateSecurityChart(qber) {
        const chart = this.securityChart;
        const data = chart.data;
        
        // Add new data point
        data.labels.push(data.labels.length);
        data.datasets[0].data.push(qber);
        
        // Keep only last 15 points
        if (data.labels.length > 15) {
            data.labels.shift();
            data.datasets[0].data.shift();
        }
        
        chart.update('none');
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.qkdCharts = new QKDCharts();
});
