// static/app.js

document.addEventListener("DOMContentLoaded", () => {
    fetchTransactions();
    loadFraudComparisonGraph();
    loadTimeSeriesGraph();
});

function fetchTransactions() {
    fetch("/api/transactions") // Ensure API exists in backend
        .then(response => response.json())
        .then(data => {
            let tableBody = document.querySelector("#transactionTable tbody");
            tableBody.innerHTML = ""; // Clear existing rows
            data.forEach(tx => {
                let row = `<tr>
                    <td>${tx.transaction_id}</td>
                    <td>${tx.payer_id}</td>
                    <td>${tx.payee_id}</td>
                    <td>${tx.transaction_amount}</td>
                    <td>${tx.transaction_channel}</td>
                    <td>${tx.transaction_payment_mode}</td>
                    <td>${tx.payment_gateway_bank}</td>
                    <td>${tx.is_fraud_predicted ? "Yes" : "No"}</td>
                    <td>${tx.is_fraud_reported ? "Yes" : "No"}</td>
                </tr>`;
                tableBody.innerHTML += row;
            });
        });
}

function filterData() {
    let date = document.getElementById("dateFilter").value;
    let payer = document.getElementById("payerFilter").value;
    let payee = document.getElementById("payeeFilter").value;
    
    fetch(`/api/transactions?date=${date}&payer=${payer}&payee=${payee}`)
        .then(response => response.json())
        .then(updateTable);
}

function searchTransaction() {
    let transactionID = document.getElementById("searchBox").value;
    
    fetch(`/api/transactions?transaction_id=${transactionID}`)
        .then(response => response.json())
        .then(updateTable);
}

function updateTable(data) {
    let tableBody = document.querySelector("#transactionTable tbody");
    tableBody.innerHTML = "";
    data.forEach(tx => {
        let row = `<tr>
            <td>${tx.transaction_id}</td>
            <td>${tx.payer_id}</td>
            <td>${tx.payee_id}</td>
            <td>${tx.transaction_amount}</td>
            <td>${tx.transaction_channel}</td>
            <td>${tx.transaction_payment_mode}</td>
            <td>${tx.payment_gateway_bank}</td>
            <td>${tx.is_fraud_predicted ? "Yes" : "No"}</td>
            <td>${tx.is_fraud_reported ? "Yes" : "No"}</td>
        </tr>`;
        tableBody.innerHTML += row;
    });
}

function loadFraudComparisonGraph() {
    fetch("/api/fraud-stats")
        .then(response => response.json())
        .then(data => {
            let ctx = document.getElementById("fraudComparisonChart").getContext("2d");
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: data.labels,
                    datasets: [
                        { label: "Predicted Fraud", data: data.predicted, backgroundColor: "red" },
                        { label: "Reported Fraud", data: data.reported, backgroundColor: "blue" }
                    ]
                }
            });
        });
}

function loadTimeSeriesGraph() {
    fetch("/api/time-series")
        .then(response => response.json())
        .then(data => {
            let ctx = document.getElementById("fraudTimeSeriesChart").getContext("2d");
            new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.dates,
                    datasets: [
                        { label: "Predicted Fraud", data: data.predicted, borderColor: "red", fill: false },
                        { label: "Reported Fraud", data: data.reported, borderColor: "blue", fill: false }
                    ]
                },
                options: {
                    responsive: true,
                    scales: { x: { type: 'time', time: { unit: data.granularity } } }
                }
            });
        });
}

function updateTimeSeries() {
    let timeframe = document.getElementById("timeFrame").value;
    fetch(`/api/time-series?timeframe=${timeframe}`)
        .then(response => response.json())
        .then(loadTimeSeriesGraph);
}

function updateEvaluation() {
    let period = document.getElementById("evalPeriod").value;
    fetch(`/api/evaluation?period=${period}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("confusionMatrix").textContent = data.confusion_matrix;
            document.getElementById("precision").textContent = data.precision;
            document.getElementById("recall").textContent = data.recall;
        });
}
