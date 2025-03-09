function toggleMode() {
    let basic = document.getElementById("basicMode");
    let advanced = document.getElementById("advancedMode");
    if (basic.style.display === "none") {
        basic.style.display = "block";
        advanced.style.display = "none";
    } else {
        basic.style.display = "none";
        advanced.style.display = "block";
        loadGraphs();
    }
}

function loadGraphs() {
    fetch("/graph_data")
        .then(response => response.json())
        .then(data => {
            let ctx1 = document.getElementById("pieChart").getContext("2d");
            new Chart(ctx1, {
                type: "pie",
                data: {
                    labels: Object.keys(data.categories),
                    datasets: [{
                        data: Object.values(data.categories),
                        backgroundColor: ["red", "blue", "green", "yellow"],
                    }]
                }
            });

            let ctx2 = document.getElementById("barChart").getContext("2d");
            new Chart(ctx2, {
                type: "bar",
                data: {
                    labels: Object.keys(data.monthly_expenses),
                    datasets: [{
                        label: "Monthly Spending",
                        data: Object.values(data.monthly_expenses),
                        backgroundColor: "blue",
                    }]
                }
            });
        });
}
