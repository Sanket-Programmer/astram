# ASTraM Command Center
## AI-Driven Event Impact Forecasting & Resource Deployment for Bengaluru Traffic Police

ASTraM (AI-Based Smart Traffic Management) is an interactive Streamlit dashboard designed to support **traffic event forecasting, hotspot intelligence, resource deployment planning, and post-event learning** for urban traffic police operations.

The system predicts the **Traffic Impact Index (TII)** of a traffic event using a trained machine learning model and recommends **traffic officers, barricades, and diversion actions**. It also supports a **Post-Event Learning Loop**, where field feedback can be saved and used to improve future recommendations.

---

# Table of Contents
1. [Project Overview](#project-overview)
2. [Core Features](#core-features)
3. [Project Folder Structure](#project-folder-structure)
4. [Required Files](#required-files)
5. [Installation and Setup](#installation-and-setup)
6. [Running the App](#running-the-app)
7. [How to Use the App](#how-to-use-the-app)
8. [Forecasting Command Center Workflow](#forecasting-command-center-workflow)
9. [Post-Event Learning Loop](#post-event-learning-loop)
10. [Hotspot Intelligence Module](#hotspot-intelligence-module)
11. [Event Analytics Module](#event-analytics-module)
12. [Adaptive Learning Logic](#adaptive-learning-logic)
13. [Troubleshooting](#troubleshooting)
14. [Recommended Demo Flow](#recommended-demo-flow)
15. [Example Demo Scenario](#example-demo-scenario)
16. [Technology Stack](#technology-stack)
17. [Future Scope](#future-scope)

---

# Project Overview

ASTraM is a **decision-support dashboard** for traffic management. It is built for scenarios where traffic control teams need to quickly understand:

- **How severe a traffic event may become**
- **Which junctions are historically vulnerable**
- **How many officers and barricades may be required**
- **Whether a diversion should be activated**
- **How to record actual field outcomes for future improvement**

The app is designed to be run **locally using Streamlit** for project demonstrations, academic evaluation, and prototype simulation.

---

# Core Features

## 1) Dashboard Overview
Provides a citywide snapshot of historical traffic event patterns:
- Total traffic events
- Planned vs unplanned events
- High-priority events
- Average Traffic Impact Index
- Top event causes
- Priority distribution
- Top hotspot junctions

## 2) Forecasting Command Center
This is the operational core of ASTraM.

It allows the user to:
- Input an incident scenario
- Predict the **Traffic Impact Index (TII)**
- View the **risk level**
- Receive recommendations for:
  - **Traffic officers**
  - **Barricades**
  - **Diversion requirement**
  - **Operational actions**

It also includes:
- Tactical incident map
- AI reasoning panel
- Dispatch summary
- Post-event learning form

## 3) Hotspot Intelligence
This module shows historical hotspot trends using junction-level event frequency and impact patterns.

It includes:
- hotspot summary table
- risk level by hotspot
- optional hotspot HTML map

## 4) Event Analytics
This module provides visual analytics for:
- event causes
- priority levels
- planned vs unplanned incidents
- top police stations by event volume
- junction hotspot summary

## 5) Post-Event Learning Loop
After an incident is resolved, the actual field outcome can be logged into the system.

This helps store:
- actual clearance time
- actual officers used
- actual barricades used
- diversion actually required
- qualitative prediction feedback

This data is saved into a feedback CSV file for future adaptive learning.

---

# Project Folder Structure

Make sure your project folder contains the following files:

```bash
ASTraM/
│
├── app.py
├── impact_dataset.csv
├── traffic_impact_predictor.pkl
├── astram_retraining_log.csv        # optional, generated automatically if not present
├── traffic_hotspots_final.html      # optional hotspot map file
├── requirements.txt                 # optional but recommended
└── README.md
```

---

# Required Files

## 1. `app.py`
Main Streamlit application file.

## 2. `impact_dataset.csv`
Historical traffic event dataset used for:
- dashboard metrics
- hotspot intelligence
- analytics
- context-aware filtering

## 3. `traffic_impact_predictor.pkl`
Trained machine learning model used to predict **Traffic Impact Index**.

## 4. `astram_retraining_log.csv`
Feedback log generated from the Post-Event Learning Loop.

- If the file does not exist, the app can create it automatically after the first feedback submission.
- This file stores actual field outcomes and learning feedback.

## 5. `traffic_hotspots_final.html`
Optional hotspot map file for the Hotspot Intelligence page.

## 6. `requirements.txt`
Recommended dependency file for easier project setup.

---

# Installation and Setup

## Step 1: Install Python
Make sure **Python 3.10 or above** is installed.

Check using:

```bash
python --version
```

or

```bash
python3 --version
```

## Step 2: Create a Virtual Environment (Recommended)

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Required Libraries

Install the required packages:

```bash
pip install streamlit pandas numpy joblib folium streamlit-folium plotly scikit-learn
```

If you have a `requirements.txt` file, use:

```bash
pip install -r requirements.txt
```

---

# Running the App

From the project folder, run:

```bash
streamlit run app.py
```

After running, Streamlit will open the app in your browser automatically.

If it does not open automatically:
1. copy the local URL shown in the terminal (usually `http://localhost:8501`)
2. paste it into your browser

---

# How to Use the App

## Step 1: Clone the project in a local file

## Step 2: Launch the App
Run:

```bash
streamlit run app.py
```

Once the app opens, use the **left sidebar** to switch between modules:
- Dashboard Overview
- Forecasting Command Center
- Hotspot Intelligence
- Event Analytics

---

# Forecasting Command Center Workflow

This is the main prediction module of ASTraM.

## Step 1: Open Forecasting Command Center
From the sidebar, select:

**Forecasting Command Center**

## Step 2: Fill Incident Details
Enter the incident details from the sidebar.

### Required Inputs
- **Event Cause**
  - Examples: `accident`, `congestion`, `public_event`, `procession`, `water_logging`, `vehicle_breakdown`

- **Event Type**
  - `planned` / `unplanned`

- **Priority**
  - `High` / `Low`

- **Requires Road Closure**
  - `True` / `False`

- **Zone**
  - Select the relevant traffic zone if available

- **Police Station**
  - Select the relevant station if available

- **Junction**
  - Select the relevant junction  
  - This is important because the trained model uses **junction** as an input feature

- **Incident Notes (Optional)**
  - Example:  
    `Heavy vehicle breakdown near signal causing lane blockage`

## Step 3: Click **Analyze Incident**
After entering the incident details, click:

**🚨 Analyze Incident**

The app will then:
1. send the input to the trained ML model
2. predict the **Traffic Impact Index**
3. assign a **risk level**
4. recommend:
   - officers
   - barricades
   - diversion requirement
5. display the tactical map and dispatch summary

---

# Understanding the Forecast Output

After clicking **Analyze Incident**, ASTraM shows:

## A. Alert Banner
A visual alert based on predicted severity:
- **HIGH IMPACT ALERT**
- **MEDIUM IMPACT ALERT**
- **LOW IMPACT ALERT**

## B. KPI Cards
You will see:
- **Traffic Impact Index**
- **Risk Level**
- **Recommended Officers**
- **Barricades**
- **Diversion Required**

---

# Forecasting Tabs Explained

After analysis, ASTraM shows 3 tabs:

## Tab 1: Tactical Map
This tab displays:
- forecasted incident marker
- operational impact radius
- optional historical hotspot heatmap
- closest historical hotspot pattern

## Tab 2: AI Reasoning & Dispatch
This tab displays:
- the major drivers behind the prediction
- recommended operational actions
- dispatch summary in a readable command format

## Tab 3: Post-Event Learning Loop
This tab is used **after the incident has been resolved in the field**.

It allows the user to log the actual field outcome.

---

# Post-Event Learning Loop

The Post-Event Learning Loop is one of the key parts of ASTraM because it allows the system to store actual field outcomes after an incident is resolved.

## When to use it
Use this tab **after**:
1. you have analyzed an incident
2. you have obtained recommendations
3. the simulated or real field outcome is available

## Fields to Fill in the Feedback Form

### 1) Actual Clearance Time (Minutes)
Enter how long the incident actually took to clear.

### 2) Actual Officers Used
Enter the actual number of officers used in the field.

### 3) Actual Barricades Used
Enter the actual number of barricades used.

### 4) Diversion Actually Required
Select whether diversion was actually required in the field.

### 5) Was the Forecast Accurate?
Choose one of:
- **Yes**
- **No - Predicted Too High**
- **No - Predicted Too Low**

## Step 4: Save Feedback
Click:

**💾 Save to Retraining Log**

The app will save the feedback into:

```bash
astram_retraining_log.csv
```

---

# What Gets Stored in the Feedback Log

Each feedback row can contain:
- timestamp
- event cause
- event type
- priority
- road closure flag
- zone
- police station
- junction
- predicted impact
- predicted risk
- recommended officers
- recommended barricades
- recommended diversion
- actual clearance time
- actual officers used
- actual barricades used
- actual diversion requirement
- prediction feedback
- observed field impact score
- impact error
- notes

---

# Viewing Saved Feedback History

Below the feedback form, the app displays the contents of the feedback log file.

This helps you:
- verify that feedback was stored
- review past feedback entries
- demonstrate post-event learning during project evaluation

---

# Hotspot Intelligence Module

Open **Hotspot Intelligence** from the sidebar.

This module shows:
- top hotspot junctions
- average Traffic Impact Index at each hotspot
- risk level of hotspot junctions
- optional embedded hotspot HTML map

If `traffic_hotspots_final.html` is present in the project folder, it will be displayed inside the app.

If the file is missing, the app will show a warning.

---

# Event Analytics Module

Open **Event Analytics** from the sidebar.

This module displays visual analytics such as:
- Event cause distribution
- Priority distribution
- Planned vs unplanned events
- Top police stations by event volume
- Junction hotspot summary

Use this module to:
- understand the dataset
- explain historical operational patterns
- present the analytical side of the project

---

# Adaptive Learning Logic

ASTraM uses a **hybrid learning approach**.

## Layer 1: Base ML Model
The file `traffic_impact_predictor.pkl` predicts the initial **Traffic Impact Index** using:
- `event_cause`
- `priority`
- `requires_road_closure`
- `event_type`
- `junction`

## Layer 2: Feedback-Based Learning
The file `astram_retraining_log.csv` stores actual field outcomes.

This log can be used to:
- compare predicted impact with observed field impact
- review actual officers and barricades used
- evaluate whether diversion was actually required
- build adaptive learning logic for future improvements

---

# Troubleshooting

## 1) Model File Not Found
If you see an error like:

```bash
Model file traffic_impact_predictor.pkl not found
```

make sure the trained model file is present in the same folder as `app.py`.

## 2) Dataset File Missing
If `impact_dataset.csv` is missing, the app will not be able to load historical data.

## 3) Feedback Not Saving to CSV
If clicking **Save to Retraining Log** does not save anything:
- make sure the app has permission to write files
- do not keep the CSV open in Excel
- save feedback only after running **Analyze Incident**
- if the CSV is corrupted/empty, delete it and let the app recreate it

## 4) Hotspot Map Not Appearing
If the Hotspot Intelligence page shows a warning, it usually means `traffic_hotspots_final.html` is missing from the project folder.

---

# Recommended Demo Flow

1. Open **Dashboard Overview** and explain the historical event pattern.
2. Open **Hotspot Intelligence** and show the hotspot table/map.
3. Open **Forecasting Command Center**.
4. Enter a sample incident scenario.
5. Click **Analyze Incident**.
6. Explain the predicted impact, risk level, officers, barricades, and diversion.
7. Open **AI Reasoning & Dispatch** and show the dispatch summary.
8. Open **Post-Event Learning Loop** and enter a realistic field outcome.
9. Save the feedback and show that the system stores it in the log.

---

# Example Demo Scenario

Use a sample scenario like:

- **Event Cause:** accident
- **Event Type:** unplanned
- **Priority:** High
- **Requires Road Closure:** True
- **Zone:** East
- **Police Station:** Indiranagar
- **Junction:** Domlur Junction
- **Incident Notes:** Multi-vehicle collision causing lane blockage during peak hour

---

# Technology Stack

- **Python**
- **Streamlit**
- **Pandas / NumPy**
- **Scikit-learn**
- **Joblib**
- **Folium**
- **Streamlit-Folium**
- **Plotly Express**

---

# Future Scope

Possible future enhancements:
- live traffic API integration
- automatic retraining pipeline
- centralized shared feedback storage
- route diversion optimization
- GIS integration for control room use
- multilingual dashboard
- real-time event ingestion

---

# Project Note

ASTraM Command Center is an **AI-powered traffic event forecasting and resource deployment prototype** for smart urban traffic policing scenarios.
