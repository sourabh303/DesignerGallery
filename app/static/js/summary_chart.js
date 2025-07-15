document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('barChart')?.getContext('2d');
    if (!ctx) return;

    const labels = window.chartData?.labels || [];
    const passedData = window.chartData?.passed || [];
    const pendingData = window.chartData?.pending || [];

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Passed',
                    data: passedData,
                    backgroundColor: '#28a745'
                },
                {
                    label: 'Pending',
                    data: pendingData,
                    backgroundColor: '#dc3545'
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'Design Status by Subfolder' }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Subfolders' }
                },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Count' }
                }
            }
        }
    });
});
