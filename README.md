# 👑 BAASHA — Master Your Money
### Intelligent Personal Finance Tracker & Advisory Platform

![BAASHA Official Logo](static/img/baasha_banner.png)

> **Institution:** SRM Institute of Science and Technology (SRMIST), Ramapuram  
> **Academic Program:** 2nd Year B.Tech — Department of Computer Science & Engineering (CSE Core)  
> **Academic Year:** 2026  
> **Project Team Members & Creators:**
> - **Kamallesh** — Lead Full-Stack Developer & System Architect (2nd Year CSE Core, SRMIST)
> - **Janardhanan** — Financial Analytics & Algorithmic Heuristics Specialist (2nd Year CSE Core, SRMIST)
> - **Suriya** — UI/UX Designer & Data Visualization Lead (2nd Year CSE Core, SRMIST)

---

## 📌 Project Overview
**BAASHA — Master Your Money** is a modern, responsive personal finance web application built with **Python 3**, **Flask**, **SQLite**, and **Chart.js**. It empowers users to monitor their cash flow, track income and expenses across detailed categories, identify behavioral spending patterns, view interactive **weekly, monthly, and yearly expense graphs**, and receive algorithmic savings suggestions based on the **50/30/20 wealth framework**.

---

## ✨ Key Features & Requirements

### 1. 💰 Income & Expense Management
- Record transactions with Type (`Income` or `Expense`), Amount, Date, Category, Payment Method (UPI, Credit/Debit Card, Net Banking, Cash), and Notes.
- Support for marking transactions as **Recurring** (Rent, Salary, Subscriptions).
- Full CRUD capability: Add, Edit, Delete, and Search/Filter records.
- **CSV Data Export** for offline spreadsheets (`.csv`).

### 2. 📊 Multi-Horizon Expense Graphs
- **Weekly Expense Graph**:
  - 7-day comparative daily bar chart (Current Week vs. Previous Week).
  - Weekly category breakdown (Doughnut chart).
  - Week-over-week (WoW) spending growth/reduction percentage.
  - Identification of peak spending day.
- **Monthly Expense Graph**:
  - Interactive Month and Year picker.
  - Day-by-day daily spend bars and cumulative expense trajectory curve.
  - 4-week expense comparison bars (Days 1–7, 8–14, 15–21, 22+).
  - Monthly category breakdown & income vs. expense comparison.
- **Yearly Expense Graph**:
  - 12-Month overview comparing monthly Income, Expense, and Net Savings.
  - Annual category ranking and distribution chart.
  - Highs and lows detection (Peak spending month vs. lowest spending month).

### 3. 🧠 Spending Habits & Smart Insights
- **50/30/20 Rule Analysis**:
  - **Needs (50%)**: Housing, Groceries, Utilities, Healthcare, Transportation.
  - **Wants (30%)**: Dining, Entertainment, Shopping, Subscriptions.
  - **Savings (20%)**: Retained surplus, investments, emergency fund.
- **Financial Health Score (0–100)**:
  - Dynamically calculates a vitality score and grade (`Excellent`, `Good`, `Fair`, `Critical`).
- **Behavioral Habit Auditing**:
  - Weekend vs. Weekday spending split (detects weekend splurges).
  - Payment channel preferences (UPI vs. Cards vs. Net Banking).
  - Burn-rate calculation (Average daily cost of living).

### 4. 🎯 Savings Suggestions & Goals
- Automated tips with estimated monthly rupee savings (e.g., dining reduction, subscription cancellation).
- 3-Month Emergency Fund runway calculator.
- Dedicated **Savings Goals Tracker** with milestone progress bars.

### 5. 👥 Team & About Section
- Dedicated page showcasing **Kamallesh**, **Janardhanan**, and **Suriya**, outlining individual technical roles, project architecture, algorithms, and college investigatory credits.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12 / 3.13, Flask 3.1 |
| **Database** | SQLite3 (Relational, embedded, zero-setup) |
| **Visualizations** | Chart.js 4.4 |
| **Front-End Styling** | Tailwind CSS 3.4 (CDN), Custom CSS |
| **Icons & Fonts** | FontAwesome 6, Plus Jakarta Sans, Outfit |

---

## 🚀 How to Run the Project

### Option 1: Double-Click (Easiest for Windows)
Simply double-click the **`run.bat`** file in this folder. It will:
1. Verify Python and dependencies.
2. Launch the Flask web server.
3. Automatically open your default web browser to `http://127.0.0.1:5000`.

---

### Option 2: Running via Terminal / PowerShell
Open your terminal inside this folder:

```powershell
# 1. Install dependencies
py -m pip install -r requirements.txt

# 2. Run the application
py app.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 📂 Project Architecture

```
Personal Tracker/
├── app.py                  # Main Flask application & routing
├── database.py             # SQLite schema, CRUD operations & sample data generator
├── analytics.py            # Financial formulas, 50/30/20 rule, weekly/monthly/yearly algorithms
├── requirements.txt        # Python dependencies (Flask)
├── run.bat                 # One-click Windows startup script
├── README.md               # Documentation & investigatory project report
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styling, fonts, and theme animations
│   └── js/
│       ├── charts.js       # Chart.js configs for Weekly, Monthly, Yearly charts
│       └── main.js         # Client-side modal toggles, dynamic forms & alerts
│
└── templates/
    ├── base.html           # Master layout with navbar, footer, modals
    ├── index.html          # Dashboard (KPIs, budget progress, recent ledger)
    ├── transactions.html   # Full ledger with filters, search, CSV export
    ├── analytics.html      # Flagship Weekly, Monthly, Yearly graph suite
    ├── insights.html       # 50/30/20 analysis, habits, smart suggestions & goals
    └── about.html          # Team page for Kamallesh, Janardhanan, Suriya
```

---

## 👥 Meet the Team

- **Kamallesh** — Lead Full-Stack Developer & System Architect  
  *Responsibilities: Core Flask application, SQLite schema design, REST API endpoints, CSV export logic.*
- **Janardhanan** — Financial Analytics & Algorithmic Heuristics Specialist  
  *Responsibilities: Predictive cash flow algorithms, Financial Health Score model, burn-rate metrics, savings heuristics.*
- **Suriya** — UI/UX Designer & Data Visualization Lead  
  *Responsibilities: Chart.js interactive canvases, responsive Tailwind CSS layouts, dashboard flows.*

---
*Created with pride for the College Investigatory Project 2026.*
