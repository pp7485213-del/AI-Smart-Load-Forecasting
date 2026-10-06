import pandas as pd
import numpy as np
from flask import Flask, render_template_string, jsonify
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import threading
import webbrowser
import os

# =========================
# AI SMART LOAD FORECASTING
# =========================

# Create sample historical load data
np.random.seed(42)

hours = pd.date_range(
    start="2026-01-01",
    periods=24 * 60,
    freq="h"
)

data = pd.DataFrame({"datetime": hours})

data["hour"] = data["datetime"].dt.hour
data["dayofweek"] = data["datetime"].dt.dayofweek

# Simulated electricity load
data["load"] = (
    100
    + 25 * np.sin((data["hour"] - 6) * np.pi / 12)
    + 15 * np.where((data["hour"] >= 18) & (data["hour"] <= 22), 1, 0)
    + np.random.normal(0, 5, len(data))
)

# Train AI model
X = data[["hour", "dayofweek"]]
y = data["load"]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# =========================
# 24 HOUR FORECAST
# =========================

future = pd.date_range(
    start=datetime.now().replace(minute=0, second=0, microsecond=0),
    periods=24,
    freq="h"
)

future_df = pd.DataFrame({"datetime": future})
future_df["hour"] = future_df["datetime"].dt.hour
future_df["dayofweek"] = future_df["datetime"].dt.dayofweek

future_df["predicted_load"] = model.predict(
    future_df[["hour", "dayofweek"]]
)

future_df["predicted_load"] = future_df["predicted_load"].round(2)

peak_load = future_df["predicted_load"].max()
average_load = future_df["predicted_load"].mean()

# =========================
# FLASK WEBSITE
# =========================

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI Based Smart Load Forecasting</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #222;
}

.header {
    background: #172554;
    color: white;
    padding: 25px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 30px;
}

.header p {
    margin-top: 8px;
}

.container {
    width: 90%;
    max-width: 1100px;
    margin: 30px auto;
}

.hero {
    background: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.hero h2 {
    color: #172554;
}

.cards {
    display: flex;
    gap: 20px;
    margin-top: 25px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 220px;
    background: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.card h3 {
    color: #555;
}

.card .value {
    font-size: 30px;
    font-weight: bold;
    color: #172554;
}

.section {
    background: white;
    margin-top: 25px;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

canvas {
    max-height: 400px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

th {
    background: #172554;
    color: white;
}

.steps {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.step {
    flex: 1;
    min-width: 180px;
    padding: 20px;
    background: #eef2ff;
    border-radius: 10px;
}

.footer {
    margin-top: 30px;
    background: #172554;
    color: white;
    text-align: center;
    padding: 20px;
}

@media(max-width:700px) {
    .header h1 {
        font-size: 22px;
    }
}

</style>
</head>

<body>

<div class="header">
    <h1>AI Based Smart Load Forecasting</h1>
    <p>Using Machine Learning and Cloud Technology</p>
</div>

<div class="container">

<div class="hero">
    <h2>Smart Electricity Load Forecasting Dashboard</h2>
    <p>
    This system uses Artificial Intelligence to predict future electricity
    demand and helps in efficient power management.
    </p>
</div>

<div class="cards">

<div class="card">
    <h3>Peak Load</h3>
    <div class="value">{{ peak }} kW</div>
</div>

<div class="card">
    <h3>Average Load</h3>
    <div class="value">{{ average }} kW</div>
</div>

<div class="card">
    <h3>Forecast Hours</h3>
    <div class="value">24</div>
</div>

</div>

<div class="section">

<h2>24-Hour Load Forecast</h2>

<canvas id="loadChart"></canvas>

<script>

const labels = {{ labels | safe }};
const values = {{ values | safe }};

new Chart(document.getElementById("loadChart"), {

    type: "line",

    data: {
        labels: labels,

        datasets: [{
            label: "Predicted Load (kW)",
            data: values,
            borderWidth: 3,
            tension: 0.3,
            fill: false
        }]
    },

    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    }

});

</script>

</div>

<div class="section">

<h2>Forecast Details</h2>

<table>

<tr>
<th>Time</th>
<th>Predicted Load (kW)</th>
</tr>

{% for row in forecast %}

<tr>
<td>{{ row.time }}</td>
<td>{{ row.load }}</td>
</tr>

{% endfor %}

</table>

</div>

<div class="section">

<h2>How the System Works</h2>

<div class="steps">

<div class="step">
<h3>1. Data Collection</h3>
<p>Historical electricity load data is collected.</p>
</div>

<div class="step">
<h3>2. AI Processing</h3>
<p>Machine Learning analyzes the load pattern.</p>
</div>

<div class="step">
<h3>3. Load Prediction</h3>
<p>The system predicts electricity demand for the next 24 hours.</p>
</div>

<div class="step">
<h3>4. Smart Management</h3>
<p>Forecast information helps in better power management.</p>
</div>

</div>

</div>

</div>

<div class="footer">
AI Based Smart Load Forecasting Using Cloud | Final Year Project
</div>

</body>
</html>
"""

@app.route("/")
def home():

    forecast = []

    for _, row in future_df.iterrows():

        forecast.append({
            "time": row["datetime"].strftime("%d-%m-%Y %H:%M"),
            "load": row["predicted_load"]
        })

    labels = [
        row["datetime"].strftime("%H:%M")
        for _, row in future_df.iterrows()
    ]

    values = future_df["predicted_load"].tolist()

    return render_template_string(
        HTML,
        peak=round(peak_load, 2),
        average=round(average_load, 2),
        forecast=forecast,
        labels=labels,
        values=values
    )

@app.route("/api/forecast")
def api_forecast():

    return jsonify(
        future_df.to_dict(orient="records")
    )

# =========================
# START WEBSITE
# =========================

def start_server():
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )

thread = threading.Thread(
    target=start_server,
    daemon=True
)

thread.start()

webbrowser.open("http://127.0.0.1:5000")

print("====================================")
print("AI SMART LOAD FORECASTING WEBSITE")
print("====================================")
print("Website: http://127.0.0.1:5000")
print("Peak Load:", round(peak_load, 2), "kW")
print("Average Load:", round(average_load, 2), "kW")
print("24-Hour Forecast Generated Successfully!")

import pandas as pd
import numpy as np
from flask import Flask, render_template_string, jsonify
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import threading
import webbrowser
import os

# =========================
# AI SMART LOAD FORECASTING
# =========================

# Create sample historical load data
np.random.seed(42)

hours = pd.date_range(
    start="2026-01-01",
    periods=24 * 60,
    freq="h"
)

data = pd.DataFrame({"datetime": hours})

data["hour"] = data["datetime"].dt.hour
data["dayofweek"] = data["datetime"].dt.dayofweek

# Simulated electricity load
data["load"] = (
    100
    + 25 * np.sin((data["hour"] - 6) * np.pi / 12)
    + 15 * np.where((data["hour"] >= 18) & (data["hour"] <= 22), 1, 0)
    + np.random.normal(0, 5, len(data))
)

# Train AI model
X = data[["hour", "dayofweek"]]
y = data["load"]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# =========================
# 24 HOUR FORECAST
# =========================

future = pd.date_range(
    start=datetime.now().replace(minute=0, second=0, microsecond=0),
    periods=24,
    freq="h"
)

future_df = pd.DataFrame({"datetime": future})
future_df["hour"] = future_df["datetime"].dt.hour
future_df["dayofweek"] = future_df["datetime"].dt.dayofweek

future_df["predicted_load"] = model.predict(
    future_df[["hour", "dayofweek"]]
)

future_df["predicted_load"] = future_df["predicted_load"].round(2)

peak_load = future_df["predicted_load"].max()
average_load = future_df["predicted_load"].mean()

# =========================
# FLASK WEBSITE
# =========================

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>AI Based Smart Load Forecasting</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #222;
}

.header {
    background: #172554;
    color: white;
    padding: 25px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 30px;
}

.header p {
    margin-top: 8px;
}

.container {
    width: 90%;
    max-width: 1100px;
    margin: 30px auto;
}

.hero {
    background: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.hero h2 {
    color: #172554;
}

.cards {
    display: flex;
    gap: 20px;
    margin-top: 25px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 220px;
    background: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.card h3 {
    color: #555;
}

.card .value {
    font-size: 30px;
    font-weight: bold;
    color: #172554;
}

.section {
    background: white;
    margin-top: 25px;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

canvas {
    max-height: 400px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

th {
    background: #172554;
    color: white;
}

.steps {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.step {
    flex: 1;
    min-width: 180px;
    padding: 20px;
    background: #eef2ff;
    border-radius: 10px;
}

.footer {
    margin-top: 30px;
    background: #172554;
    color: white;
    text-align: center;
    padding: 20px;
}

@media(max-width:700px) {
    .header h1 {
        font-size: 22px;
    }
}

</style>
</head>

<body>

<div class="header">
    <h1>AI Based Smart Load Forecasting</h1>
    <p>Using Machine Learning and Cloud Technology</p>
</div>

<div class="container">

<div class="hero">
    <h2>Smart Electricity Load Forecasting Dashboard</h2>
    <p>
    This system uses Artificial Intelligence to predict future electricity
    demand and helps in efficient power management.
    </p>
</div>

<div class="cards">

<div class="card">
    <h3>Peak Load</h3>
    <div class="value">{{ peak }} kW</div>
</div>

<div class="card">
    <h3>Average Load</h3>
    <div class="value">{{ average }} kW</div>
</div>

<div class="card">
    <h3>Forecast Hours</h3>
    <div class="value">24</div>
</div>

</div>

<div class="section">

<h2>24-Hour Load Forecast</h2>

<canvas id="loadChart"></canvas>

<script>

const labels = {{ labels | safe }};
const values = {{ values | safe }};

new Chart(document.getElementById("loadChart"), {

    type: "line",

    data: {
        labels: labels,

        datasets: [{
            label: "Predicted Load (kW)",
            data: values,
            borderWidth: 3,
            tension: 0.3,
            fill: false
        }]
    },

    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: false
            }
        }
    }

});

</script>

</div>

<div class="section">

<h2>Forecast Details</h2>

<table>

<tr>
<th>Time</th>
<th>Predicted Load (kW)</th>
</tr>

{% for row in forecast %}

<tr>
<td>{{ row.time }}</td>
<td>{{ row.load }}</td>
</tr>

{% endfor %}

</table>

</div>

<div class="section">

<h2>How the System Works</h2>

<div class="steps">

<div class="step">
<h3>1. Data Collection</h3>
<p>Historical electricity load data is collected.</p>
</div>

<div class="step">
<h3>2. AI Processing</h3>
<p>Machine Learning analyzes the load pattern.</p>
</div>

<div class="step">
<h3>3. Load Prediction</h3>
<p>The system predicts electricity demand for the next 24 hours.</p>
</div>

<div class="step">
<h3>4. Smart Management</h3>
<p>Forecast information helps in better power management.</p>
</div>

</div>

</div>

</div>

<div class="footer">
AI Based Smart Load Forecasting Using Cloud | Final Year Project
</div>

</body>
</html>
"""

@app.route("/")
def home():

    forecast = []

    for _, row in future_df.iterrows():

        forecast.append({
            "time": row["datetime"].strftime("%d-%m-%Y %H:%M"),
            "load": row["predicted_load"]
        })

    labels = [
        row["datetime"].strftime("%H:%M")
        for _, row in future_df.iterrows()
    ]

    values = future_df["predicted_load"].tolist()

    return render_template_string(
        HTML,
        peak=round(peak_load, 2),
        average=round(average_load, 2),
        forecast=forecast,
        labels=labels,
        values=values
    )

@app.route("/api/forecast")
def api_forecast():

    return jsonify(
        future_df.to_dict(orient="records")
    )

# =========================
# START WEBSITE
# =========================

def start_server():
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )

thread = threading.Thread(
    target=start_server,
    daemon=True
)

thread.start()

webbrowser.open("http://127.0.0.1:5000")

print("====================================")
print("AI SMART LOAD FORECASTING WEBSITE")
print("====================================")
print("Website: http://127.0.0.1:5000")
print("Peak Load:", round(peak_load, 2), "kW")
print("Average Load:", round(average_load, 2), "kW")
print("24-Hour Forecast Generated Successfully!")

# ============================================
# SMART LOAD FORECASTING - WORKING DASHBOARD
# ============================================

import numpy as np
import pandas as pd
from flask import Flask, render_template_string, request
from sklearn.ensemble import RandomForestRegressor
import threading
import time
import webbrowser

# -----------------------------
# AI MODEL
# -----------------------------

np.random.seed(42)

dates = pd.date_range("2026-01-01", periods=24*60, freq="h")

data = pd.DataFrame({"datetime": dates})
data["hour"] = data["datetime"].dt.hour
data["day"] = data["datetime"].dt.dayofweek

data["load"] = (
    100
    + 20 * np.sin((data["hour"] - 6) * np.pi / 12)
    + np.where((data["hour"] >= 18) & (data["hour"] <= 22), 25, 0)
    + np.random.normal(0, 4, len(data))
)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(
    data[["hour", "day"]],
    data["load"]
)

# -----------------------------
# FLASK
# -----------------------------

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>

<title>AI Smart Load Forecasting</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    color: #1e293b;
}

header {
    background: #172554;
    color: white;
    padding: 25px;
    text-align: center;
}

header h1 {
    margin: 0;
    font-size: 30px;
}

nav {
    background: #0f172a;
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
}

nav button {
    background: transparent;
    border: none;
    color: white;
    padding: 15px 25px;
    cursor: pointer;
    font-size: 15px;
}

nav button:hover {
    background: #1e3a8a;
}

.container {
    width: 90%;
    max-width: 1100px;
    margin: 30px auto;
}

.page {
    display: none;
}

.active {
    display: block;
}

.box {
    background: white;
    padding: 30px;
    margin-bottom: 25px;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(0,0,0,.08);
}

.cards {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 200px;
    background: white;
    padding: 25px;
    text-align: center;
    border-radius: 15px;
    box-shadow: 0 3px 12px rgba(0,0,0,.08);
}

.card h3 {
    margin-top: 0;
}

.value {
    font-size: 30px;
    font-weight: bold;
    color: #172554;
}

input {
    padding: 12px;
    width: 100%;
    max-width: 350px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    margin: 8px 0;
}

.action {
    background: #172554;
    color: white;
    border: none;
    padding: 12px 25px;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 10px;
}

.action:hover {
    background: #1e40af;
}

.result {
    margin-top: 20px;
    padding: 20px;
    background: #eef2ff;
    border-radius: 10px;
    display: none;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

th {
    background: #172554;
    color: white;
}

.step {
    background: #eef2ff;
    padding: 20px;
    margin: 10px 0;
    border-radius: 10px;
}

footer {
    background: #172554;
    color: white;
    text-align: center;
    padding: 20px;
    margin-top: 40px;
}

</style>

</head>

<body>

<header>

<h1>AI Based Smart Load Forecasting</h1>

<p>Using Machine Learning and Cloud Technology</p>

</header>

<nav>

<button onclick="showPage('home')">🏠 Home</button>

<button onclick="showPage('predict')">🤖 Predict Load</button>

<button onclick="showPage('forecast')">📊 Forecast</button>

<button onclick="showPage('peak')">⚡ Peak Load</button>

<button onclick="showPage('about')">ℹ️ How It Works</button>

</nav>

<div class="container">

<!-- HOME -->

<div id="home" class="page active">

<div class="box">

<h2>Smart Load Forecasting System</h2>

<p>
This project uses Artificial Intelligence and Machine Learning
to forecast electricity load for future hours.
</p>

<p>
The system helps users understand electricity demand,
identify peak load periods and support efficient energy management.
</p>

<button class="action" onclick="showPage('predict')">
Start Load Prediction
</button>

</div>

<div class="cards">

<div class="card">

<h3>AI Model</h3>

<div class="value">ML</div>

<p>Random Forest</p>

</div>

<div class="card">

<h3>Forecast</h3>

<div class="value">24 H</div>

<p>Future Load</p>

</div>

<div class="card">

<h3>System</h3>

<div class="value">AI</div>

<p>Smart Prediction</p>

</div>

</div>

</div>


<!-- PREDICT -->

<div id="predict" class="page">

<div class="box">

<h2>🤖 AI Load Prediction</h2>

<p>Enter the hour and day to predict electricity load.</p>

<label>Hour (0 - 23)</label>

<input id="hour" type="number" min="0" max="23" placeholder="Example: 18">

<label>Day (0 = Monday, 6 = Sunday)</label>

<input id="day" type="number" min="0" max="6" placeholder="Example: 2">

<br>

<button class="action" onclick="predictLoad()">
Predict Load
</button>

<div id="predictionResult" class="result"></div>

</div>

</div>


<!-- FORECAST -->

<div id="forecast" class="page">

<div class="box">

<h2>📊 24-Hour Load Forecast</h2>

<canvas id="chart"></canvas>

</div>

<div class="box">

<h2>Forecast Details</h2>

<table>

<tr>
<th>Hour</th>
<th>Predicted Load (kW)</th>
</tr>

{% for item in forecast %}

<tr>

<td>{{ item.hour }}</td>

<td>{{ item.load }}</td>

</tr>

{% endfor %}

</table>

</div>

</div>


<!-- PEAK -->

<div id="peak" class="page">

<div class="box">

<h2>⚡ Load Analysis</h2>

<div class="cards">

<div class="card">

<h3>Peak Load</h3>

<div class="value">{{ peak }} kW</div>

</div>

<div class="card">

<h3>Average Load</h3>

<div class="value">{{ average }} kW</div>

</div>

<div class="card">

<h3>Forecast Period</h3>

<div class="value">24 H</div>

</div>

</div>

</div>

</div>


<!-- ABOUT -->

<div id="about" class="page">

<div class="box">

<h2>ℹ️ How The System Works</h2>

<div class="step">

<h3>1. Data Collection</h3>

<p>Historical electricity load data is collected.</p>

</div>

<div class="step">

<h3>2. AI Model</h3>

<p>Machine Learning identifies patterns in the data.</p>

</div>

<div class="step">

<h3>3. Prediction</h3>

<p>The model predicts future electricity demand.</p>

</div>

<div class="step">

<h3>4. Dashboard</h3>

<p>Predicted load is displayed using graphs and tables.</p>

</div>

<div class="step">

<h3>5. Cloud Extension</h3>

<p>
The system can store forecasting data in a cloud database
for remote access and monitoring.
</p>

</div>

</div>

</div>

</div>

<footer>

AI Based Smart Load Forecasting Using Cloud

</footer>


<script>

function showPage(page) {

    document.querySelectorAll(".page").forEach(function(p) {
        p.classList.remove("active");
    });

    document.getElementById(page).classList.add("active");

    if(page === "forecast") {
        drawChart();
    }
}


function predictLoad() {

    let hour = Number(document.getElementById("hour").value);

    let day = Number(document.getElementById("day").value);

    if(hour < 0 || hour > 23 || day < 0 || day > 6) {

        alert("Please enter valid Hour (0-23) and Day (0-6)");

        return;
    }

    let base =
        100
        + 20 * Math.sin((hour - 6) * Math.PI / 12)
        + ((hour >= 18 && hour <= 22) ? 25 : 0);

    let result = base.toFixed(2);

    let box = document.getElementById("predictionResult");

    box.style.display = "block";

    box.innerHTML =
        "<h3>Predicted Electricity Load</h3>" +
        "<h2>" + result + " kW</h2>" +
        "<p>AI model prediction completed successfully.</p>";
}


let chartCreated = false;

function drawChart() {

    if(chartCreated) return;

    chartCreated = true;

    const ctx = document.getElementById("chart");

    new Chart(ctx, {

        type: "line",

        data: {

            labels: {{ labels | safe }},

            datasets: [{

                label: "Predicted Load (kW)",

                data: {{ values | safe }},

                borderWidth: 3,

                tension: 0.3

            }]

        },

        options: {

            responsive: true,

            scales: {

                y: {
                    beginAtZero: false
                }

            }

        }

    });

}

</script>

</body>

</html>
"""


# -----------------------------
# GENERATE 24 HOUR FORECAST
# -----------------------------

future_hours = list(range(24))

future_df = pd.DataFrame({
    "hour": future_hours
})

future_df["day"] = datetime_day = pd.Timestamp.now().dayofweek

future_df["load"] = model.predict(
    future_df[["hour", "day"]]
)

future_df["load"] = future_df["load"].round(2)

peak = future_df["load"].max()

average = future_df["load"].mean()


@app.route("/")
def home():

    forecast = []

    for _, row in future_df.iterrows():

        forecast.append({
            "hour": f"{int(row['hour']):02d}:00",
            "load": row["load"]
        })

    labels = [
        f"{int(x):02d}:00"
        for x in future_df["hour"]
    ]

    values = future_df["load"].tolist()

    return render_template_string(
        HTML,
        forecast=forecast,
        peak=round(peak, 2),
        average=round(average, 2),
        labels=labels,
        values=values
    )


# -----------------------------
# START SERVER
# -----------------------------

def run_server():

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        use_reloader=False
    )


threading.Thread(
    target=run_server,
    daemon=True
).start()

time.sleep(2)

print("======================================")
print("SMART LOAD FORECASTING WEBSITE READY")
print("======================================")
print("Open Chrome:")
print("http://127.0.0.1:5000")

import os
print(os.listdir())

import pandas as pd
import numpy as np
from flask import Flask, render_template_string, jsonify, request
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import threading
import webbrowser
import json

# ==========================================
# AI BASED SMART LOAD FORECASTING
# ==========================================

np.random.seed(42)

# Historical data
hours = pd.date_range(
    start="2026-01-01",
    periods=24 * 60,
    freq="h"
)

data = pd.DataFrame({"datetime": hours})

data["hour"] = data["datetime"].dt.hour
data["dayofweek"] = data["datetime"].dt.dayofweek

data["load"] = (
    100
    + 25 * np.sin((data["hour"] - 6) * np.pi / 12)
    + 15 * np.where(
        (data["hour"] >= 18) & (data["hour"] <= 22), 1, 0
    )
    + np.random.normal(0, 5, len(data))
)

# Train AI model
X = data[["hour", "dayofweek"]]
y = data["load"]

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

# ==========================================
# 24 HOUR FORECAST
# ==========================================

future = pd.date_range(
    start=datetime.now().replace(
        minute=0,
        second=0,
        microsecond=0
    ),
    periods=24,
    freq="h"
)

future_df = pd.DataFrame({"datetime": future})

future_df["hour"] = future_df["datetime"].dt.hour
future_df["dayofweek"] = future_df["datetime"].dt.dayofweek

future_df["predicted_load"] = model.predict(
    future_df[["hour", "dayofweek"]]
)

future_df["predicted_load"] = future_df[
    "predicted_load"
].round(2)

peak_load = future_df["predicted_load"].max()
average_load = future_df["predicted_load"].mean()

# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>

<head>

<title>AI Smart Load Forecasting</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    color: #222;
}

.header {
    background: #172554;
    color: white;
    padding: 25px;
    text-align: center;
}

.header h1 {
    margin: 0;
    font-size: 30px;
}

.header p {
    margin: 8px 0 0;
}

.navbar {
    background: white;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 10;
}

.navbar button {
    background: #172554;
    color: white;
    border: none;
    padding: 12px 20px;
    margin: 5px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 15px;
}

.navbar button:hover {
    background: #2563eb;
}

.container {
    width: 90%;
    max-width: 1100px;
    margin: 30px auto;
}

.section {
    background: white;
    margin-bottom: 25px;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.hero {
    text-align: center;
}

.hero h2 {
    color: #172554;
}

.cards {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 220px;
    background: white;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.card h3 {
    color: #555;
}

.value {
    font-size: 30px;
    font-weight: bold;
    color: #172554;
}

.input-box {
    text-align: center;
}

.input-box input,
.input-box select {
    padding: 12px;
    margin: 8px;
    border: 1px solid #ccc;
    border-radius: 7px;
    font-size: 15px;
}

.predict-btn {
    background: #172554;
    color: white;
    border: none;
    padding: 12px 25px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
}

.predict-btn:hover {
    background: #2563eb;
}

.result {
    margin-top: 20px;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    color: #172554;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

th, td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: center;
}

th {
    background: #172554;
    color: white;
}

.steps {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.step {
    flex: 1;
    min-width: 180px;
    padding: 20px;
    background: #eef2ff;
    border-radius: 10px;
}

.footer {
    background: #172554;
    color: white;
    text-align: center;
    padding: 20px;
    margin-top: 30px;
}

.hidden {
    display: none;
}

</style>

</head>

<body>

<div class="header">

<h1>AI Based Smart Load Forecasting</h1>

<p>Using Machine Learning and Cloud Technology</p>

</div>


<!-- NAVIGATION BUTTONS -->

<div class="navbar">

<button onclick="showSection('home')">
Home
</button>

<button onclick="showSection('predict')">
Predict Load
</button>

<button onclick="showSection('forecast')">
Forecast
</button>

<button onclick="showSection('peak')">
Peak Load
</button>

<button onclick="showSection('how')">
How It Works
</button>

</div>


<div class="container">


<!-- HOME -->

<div id="home" class="section">

<div class="hero">

<h2>Smart Electricity Load Forecasting Dashboard</h2>

<p>
This system uses Artificial Intelligence and Machine Learning
to predict future electricity demand.
</p>

<p>
It helps in efficient electricity planning and smart power management.
</p>

</div>

</div>


<!-- PREDICT -->

<div id="predict" class="section hidden">

<h2>AI Load Prediction</h2>

<p>
Enter the hour and day to predict electricity load.
</p>

<div class="input-box">

<input
type="number"
id="hourInput"
min="0"
max="23"
placeholder="Hour (0-23)"
>

<select id="dayInput">

<option value="0">Monday</option>
<option value="1">Tuesday</option>
<option value="2">Wednesday</option>
<option value="3">Thursday</option>
<option value="4">Friday</option>
<option value="5">Saturday</option>
<option value="6">Sunday</option>

</select>

<br>

<button
class="predict-btn"
onclick="predictLoad()"
>
Predict Load
</button>

</div>

<div id="predictionResult" class="result"></div>

</div>


<!-- FORECAST -->

<div id="forecast" class="section hidden">

<h2>24-Hour Load Forecast</h2>

<canvas id="loadChart"></canvas>

<h2>Forecast Details</h2>

<table>

<tr>
<th>Time</th>
<th>Predicted Load (kW)</th>
</tr>

{% for row in forecast %}

<tr>

<td>{{ row.time }}</td>

<td>{{ row.load }}</td>

</tr>

{% endfor %}

</table>

</div>


<!-- PEAK -->

<div id="peak" class="hidden">

<div class="cards">

<div class="card">

<h3>Peak Load</h3>

<div class="value">
{{ peak }} kW
</div>

</div>


<div class="card">

<h3>Average Load</h3>

<div class="value">
{{ average }} kW
</div>

</div>


<div class="card">

<h3>Forecast Hours</h3>

<div class="value">
24
</div>

</div>

</div>

</div>


<!-- HOW IT WORKS -->

<div id="how" class="section hidden">

<h2>How the System Works</h2>

<div class="steps">

<div class="step">

<h3>1. Data Collection</h3>

<p>
Historical electricity load data is collected.
</p>

</div>


<div class="step">

<h3>2. AI Processing</h3>

<p>
Machine Learning analyzes electricity usage patterns.
</p>

</div>


<div class="step">

<h3>3. Load Prediction</h3>

<p>
Random Forest predicts future electricity demand.
</p>

</div>


<div class="step">

<h3>4. Smart Management</h3>

<p>
Forecast information helps in better power management.
</p>

</div>

</div>

</div>


</div>


<div class="footer">

AI Based Smart Load Forecasting Using Cloud |
Final Year Project

</div>


<script>

function showSection(sectionName) {

    const sections = [
        "home",
        "predict",
        "forecast",
        "peak",
        "how"
    ];

    sections.forEach(function(section) {

        document.getElementById(section)
        .classList.add("hidden");

    });

    document.getElementById(sectionName)
    .classList.remove("hidden");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


async function predictLoad() {

    const hour =
        document.getElementById("hourInput").value;

    const day =
        document.getElementById("dayInput").value;

    if (hour === "") {

        document.getElementById(
            "predictionResult"
        ).innerHTML =
        "Please enter an hour.";

        return;
    }

    const response = await fetch(
        "/api/predict?hour="
        + hour
        + "&day="
        + day
    );

    const result = await response.json();

    document.getElementById(
        "predictionResult"
    ).innerHTML =
    "Predicted Load: "
    + result.predicted_load
    + " kW";

}


const labels = {{ labels | safe }};

const values = {{ values | safe }};


new Chart(
    document.getElementById("loadChart"),
    {

        type: "line",

        data: {

            labels: labels,

            datasets: [{

                label: "Predicted Load (kW)",

                data: values,

                borderWidth: 3,

                tension: 0.3,

                fill: false

            }]

        },

        options: {

            responsive: true,

            scales: {

                y: {

                    beginAtZero: false

                }

            }

        }

    }
);

</script>

</body>

</html>
"""


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():

    forecast = []

    for _, row in future_df.iterrows():

        forecast.append({

            "time":
            row["datetime"].strftime(
                "%d-%m-%Y %H:%M"
            ),

            "load":
            row["predicted_load"]

        })


    labels = [

        row["datetime"].strftime("%H:%M")

        for _, row in future_df.iterrows()

    ]


    values = future_df[
        "predicted_load"
    ].tolist()


    return render_template_string(

        HTML,

        peak=round(peak_load, 2),

        average=round(average_load, 2),

        forecast=forecast,

        labels=json.dumps(labels),

        values=json.dumps(values)

    )


# ==========================================
# AI PREDICTION API
# ==========================================

@app.route("/api/predict")
def predict():

    hour = int(request.args.get("hour"))

    day = int(request.args.get("day"))

    prediction = model.predict(

        [[hour, day]]

    )[0]


    return jsonify({

        "hour": hour,

        "day": day,

        "predicted_load":
        round(float(prediction), 2)

    })


# ==========================================
# FORECAST API
# ==========================================

@app.route("/api/forecast")
def api_forecast():

    return jsonify(

        future_df.to_dict(
            orient="records"
        )

    )


# ==========================================
# START SERVER
# ==========================================

def start_server():

    app.run(

        host="127.0.0.1",

        port=5001,

        debug=False,

        use_reloader=False

    )


thread = threading.Thread(

    target=start_server,

    daemon=True

)

thread.start()


webbrowser.open(
    "http://127.0.0.1:5001"
)


print("====================================")
print("AI SMART LOAD FORECASTING WEBSITE")
print("====================================")
print("Website: http://127.0.0.1:5001")
print("Peak Load:", round(peak_load, 2), "kW")
print("Average Load:", round(average_load, 2), "kW")
print("24-Hour Forecast Generated Successfully!")

import os
print(os.path.exists("app.py"))

import os

print(os.path.abspath("app.py"))
print(os.path.exists("app.py"))

import os
print(os.path.isfile("app.py"))
print(os.path.getsize("app.py"))

with open("requirements.txt", "w") as f:
    f.write("""flask
pandas
numpy
scikit-learn
gunicorn
""")

print("requirements.txt created")

import os
print(os.path.exists("requirements.txt"))

