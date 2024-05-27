document.addEventListener('DOMContentLoaded', () => {
    const historyChartCtx = document.getElementById('history-chart').getContext('2d');

    luxon.Settings.defaultLocale = "de";

    let historyChart;

    function fetchHistory() {
        fetch(`/history/${counterName}`, { method: "POST" })
            .then(response => response.json())
            .then(data => {
                const labels = data.map(entry => new Date(entry.timestamp));
                const values = data.map(entry => entry.value);

                if (historyChart) {
                    historyChart.destroy();
                }

                historyChart = new Chart(historyChartCtx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Zählerstand',
                            data: values,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1,
                            fill: false
                        }]
                    },
                    options: {
                        scales: {
                            x: {
                                type: 'time',
                                time: {
                                    unit: 'minute'
                                },
                                adapters: {
                                    date: {
                                        locale: 'en'
                                    }
                                }
                            },
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            });
    }

    fetchHistory();
});
