function toggleDropdown() {
    document.getElementById('dropdownMenu').classList.toggle('hidden');
}


const ctx = document.getElementById('cryptoChart').getContext('2d');
const cryptoChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: Array.from({length: 10}, (_, i) => `Day ${i + 1}`),
        datasets: [{
            label: 'Crypto Market',
            data: Array.from({length: 10}, () => Math.floor(Math.random() * 10000)),
            borderColor: '#00d4ff',
            fill: false,
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: {
                beginAtZero: true,
                grid: {
                    color: '#333',
                }
            },
            y: {
                beginAtZero: true,
                grid: {
                    color: '#333',
                }
            }
        }
    }
});

let currentIndex = 0;
const newsItems = document.querySelectorAll('.news-item');

function showNews(index) {
    newsItems.forEach((item, i) => {
        item.classList.remove('active');
        if (i === index) item.classList.add('active');
    });
}

function nextNews() {
    currentIndex = (currentIndex + 1) % newsItems.length;
    showNews(currentIndex);
}

function prevNews() {
    currentIndex = (currentIndex - 1 + newsItems.length) % newsItems.length;
    showNews(currentIndex);
}