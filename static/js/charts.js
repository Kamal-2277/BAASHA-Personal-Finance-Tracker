/**
 * BAASHA Personal Finance Tracker - Chart.js Rendering Engine
 * Handles Weekly, Monthly, and Yearly dynamic data visualizations.
 */

const PALETTE = [
    '#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', 
    '#14b8a6', '#f97316', '#6366f1', '#84cc16', '#06b6d4', '#e11d48'
];

// Helper to format currency in Indian style or standard
function formatMoney(num) {
    return '₹' + Number(num).toLocaleString('en-IN');
}

// ----------------- WEEKLY CHARTS ----------------- //

function renderWeeklyExpensesChart(canvasId, labels, currentData, prevData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'This Week',
                    data: currentData,
                    backgroundColor: 'rgba(16, 185, 129, 0.85)',
                    borderColor: '#10b981',
                    borderWidth: 2,
                    borderRadius: 6,
                    borderSkipped: false
                },
                {
                    label: 'Previous Week',
                    data: prevData,
                    backgroundColor: 'rgba(203, 213, 225, 0.5)',
                    borderColor: '#94a3b8',
                    borderWidth: 1.5,
                    borderRadius: 6,
                    borderSkipped: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 14, font: { family: 'Plus Jakarta Sans', weight: '600' } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatMoney(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(226, 232, 240, 0.6)' },
                    ticks: {
                        callback: function(value) { return '₹' + value.toLocaleString(); },
                        font: { family: 'Plus Jakarta Sans' }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Plus Jakarta Sans', weight: '500' } }
                }
            }
        }
    });
}

function renderWeeklyCategoryChart(canvasId, categories, amounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: PALETTE.slice(0, categories.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                            return ` ${ctx.label}: ${formatMoney(ctx.raw)} (${pct}%)`;
                        }
                    }
                }
            },
            cutout: '68%'
        }
    });
}

// ----------------- MONTHLY CHARTS ----------------- //

function renderMonthlyTimelineChart(canvasId, days, dailyExpenses, cumulativeExpenses) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [
                {
                    type: 'line',
                    label: 'Cumulative Total',
                    data: cumulativeExpenses,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.08)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    yAxisID: 'yCumulative',
                    pointRadius: 2,
                    pointHoverRadius: 6
                },
                {
                    type: 'bar',
                    label: 'Daily Expense',
                    data: dailyExpenses,
                    backgroundColor: 'rgba(59, 130, 246, 0.75)',
                    borderColor: '#3b82f6',
                    borderWidth: 1.5,
                    borderRadius: 4,
                    yAxisID: 'y'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 14 } },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            return `${ctx.dataset.label}: ${formatMoney(ctx.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    title: { display: true, text: 'Daily Spend (₹)' },
                    ticks: { callback: function(val) { return '₹' + val.toLocaleString(); } }
                },
                yCumulative: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    title: { display: true, text: 'Cumulative (₹)' },
                    ticks: { callback: function(val) { return '₹' + val.toLocaleString(); } }
                },
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 16 }
                }
            }
        }
    });
}

function renderMonthlyWeeksChart(canvasId, labels, amounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Expenses',
                data: amounts,
                backgroundColor: ['#60a5fa', '#34d399', '#fbbf24', '#f87171'],
                borderRadius: 8,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(ctx) { return `Spend: ${formatMoney(ctx.raw)}`; }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: function(v) { return '₹' + v.toLocaleString(); } }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

// ----------------- YEARLY CHARTS ----------------- //

function renderYearlyComparisonChart(canvasId, months, expenses, incomes, netSavings) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        data: {
            labels: months,
            datasets: [
                {
                    type: 'bar',
                    label: 'Income',
                    data: incomes,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10b981',
                    borderRadius: 6,
                    borderWidth: 1.5,
                    order: 2
                },
                {
                    type: 'bar',
                    label: 'Expense',
                    data: expenses,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: '#ef4444',
                    borderRadius: 6,
                    borderWidth: 1.5,
                    order: 3
                },
                {
                    type: 'line',
                    label: 'Net Savings',
                    data: netSavings,
                    borderColor: '#3b82f6',
                    backgroundColor: '#3b82f6',
                    borderWidth: 3,
                    tension: 0.3,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    order: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 14 } },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            return `${ctx.dataset.label}: ${formatMoney(ctx.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    ticks: { callback: function(v) { return '₹' + v.toLocaleString(); } },
                    grid: { color: 'rgba(226, 232, 240, 0.6)' }
                },
                x: { grid: { display: false } }
            }
        }
    });
}

// ----------------- HABITS CHARTS ----------------- //

function renderPaymentMethodsChart(canvasId, methods, amounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'pie',
        data: {
            labels: methods,
            datasets: [{
                data: amounts,
                backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total > 0 ? ((ctx.raw / total) * 100).toFixed(1) : 0;
                            return ` ${ctx.label}: ${formatMoney(ctx.raw)} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}
