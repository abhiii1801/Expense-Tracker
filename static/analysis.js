google.charts.load('current', {'packages': ['corechart']});
google.charts.setOnLoadCallback(drawCharts);

function drawCharts() {
    drawPieChart();
    drawBarChart();
    drawLineChart();
    drawExpenseByAccountChart();
}

function drawPieChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Category');
    data.addColumn('number', 'Amount');

    expensesData.forEach(function(record) {
        data.addRow([record.record_category, record.amount]);
    });

    var options = {
        pieHole: 0.5, // Donut chart
        colors: ['#4caf50', '#f44336', '#2196f3', '#ffc107', '#673ab7'],
        chartArea: { width: '90%', height: '90%' },
        legend: { position: 'bottom' }
    };

    var chart = new google.visualization.PieChart(document.getElementById('piechart'));
    chart.draw(data, options);
}

// Bar Chart
function drawBarChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Month');
    data.addColumn('number', 'Expenses');

    expensesData.forEach(function(record) {
        var date = new Date(record.formatted_date); // Convert string to date
        var month = date.toLocaleString('default', { month: 'short' });
        data.addRow([month, record.amount]);
    });

    var options = {
        hAxis: { title: 'Month' },
        vAxis: { title: 'Expenses' },
        chartArea: { width: '70%', height: '70%' }
    };

    var chart = new google.visualization.BarChart(document.getElementById('barchart'));
    chart.draw(data, options);
}

// Line Chart
function drawLineChart() {
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Date');
    data.addColumn('number', 'Cash Flow');

    expensesData.forEach(function(record) {
        // Format the date to display only day and month (e.g., "15 Jan")
        var date = new Date(record.formatted_date);
        var formattedDate = date.toLocaleString('default', { day: '2-digit', month: 'short' }); // Formats as 'DD MMM'
        
        data.addRow([formattedDate, record.amount]);
    });

    var options = {
        hAxis: { title: 'Date', titleTextStyle: { color: '#333' } },
        vAxis: { minValue: 0 },
        chartArea: { width: '70%', height: '70%' }
    };

    var chart = new google.visualization.LineChart(document.getElementById('linechart'));
    chart.draw(data, options);
}

function drawExpenseByAccountChart() {
    var accountData = {};
    expensesData.forEach(function(record) {
        accountData[record.account_name] = (accountData[record.account_name] || 0) + record.amount;
    });

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Account');
    data.addColumn('number', 'Amount');

    Object.entries(accountData).forEach(([account, total]) => {
        data.addRow([account, total]);
    });

    var options = {
        pieHole: 0.5, // Donut chart
        colors: ['#4caf50', '#f44336', '#2196f3', '#ffc107', '#673ab7'],
        chartArea: { width: '90%', height: '90%' },
        legend: { position: 'bottom' }
    };

    var chart = new google.visualization.PieChart(document.getElementById('accountchart'));
    chart.draw(data, options);
}

