<div align="center">

<!-- APP ICON & ANIMATED TYPING HEADER -->
<h1>💼</h1>
<a href="https://github.com/yourusername/applitrack">
  <img src="https://readme-typing-svg.demolab.com?font=Consolas&size=26&pause=1000&color=00F0FF&center=true&vCenter=true&width=680&lines=APPLITRACK+:+CAREER+OS;EXECUTIVE+JOB+APPLICATION+ENGINE;PIPELINE+TELEMETRY+AND+FUNNEL+ANALYTICS;ZERO-CLOUD+ENCRYPTED+SQLITE+STORAGE" alt="AppliTrack Dynamic Typing Header" />
</a>

<p align="center">
  <strong>A high-performance, obsidian-dark career operating system and job search pipeline engine built with Python, CustomTkinter, and Matplotlib.</strong>
</p>

<!-- DYNAMIC BADGES -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-08090e?style=for-the-badge&logo=python&logoColor=00f0ff" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-08090e?style=for-the-badge&logo=airplayvideo&logoColor=38bdf8" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Database-SQLite3%20Local-08090e?style=for-the-badge&logo=sqlite&logoColor=00f5a0" alt="SQLite3" />
  <img src="https://img.shields.io/badge/Analytics-Matplotlib-08090e?style=for-the-badge&logo=chartdotjs&logoColor=a855f7" alt="Matplotlib" />
  <img src="https://img.shields.io/badge/Packaging-PyInstaller%20Ready-08090e?style=for-the-badge&logo=windows&logoColor=f59e0b" alt="PyInstaller" />
  <img src="https://img.shields.io/badge/License-MIT-08090e?style=for-the-badge&logo=open-source-initiative&logoColor=ffffff" alt="MIT License" />
</p>

<!-- INTERACTIVE NAVIGATION BAR -->
<p align="center">
  <a href="#-system-overview">Overview</a> •
  <a href="#-key-capabilities">Capabilities</a> •
  <a href="#-interactive-tour--deep-dive">Feature Tour</a> •
  <a href="#-keyboard-control-deck">Hotkeys</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-quickstart--installation">Quickstart</a> •
  <a href="#-compilation-to-standalone-exe">Build Executable</a>
</p>

---

</div>

## ⚡ System Overview

**AppliTrack** is an offline career pipeline tracker built for developers, engineers, and professionals navigating modern recruitment cycles. It replaces bloated spreadsheets and invasive third-party job trackers with an ultra-responsive, local desktop operating system that keeps application data strictly on your machine.

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │  [💼 APPLITRACK EXECUTIVE CAREER OS]                                   │
 │                                                                        │
 │  [// PIPELINE VOLUME]   [// IN PROGRESS]     [// OFFERS SECURED]       │
 │   42 Opportunities       08 Interviews        03 Formal Offers         │
 │   ▲ Yield Rate 7.1%      ● 19.0% In-Flight    ▲ Target Acquired        │
 │                                                                        │
 │  [CONVERSION FUNNEL]                          [ACTIVE REPOSITORY]      │
 │   • Stage Share (Donut Matrix)                • Stripe : Backend Lead  │
 │   • Dropoff Velocity (Funnel Bars)            • Figma  : Systems Eng   │
 │   • Channel Attribution (LinkedIn/Direct)     • Notion : Tech Lead     │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 💎 Key Capabilities

---

## 🔍 Interactive Tour & Deep Dive

The main command dashboard delivers real-time intelligence on your job hunt velocity:

* **Executive Telemetry Cards:** Instant feedback on Total Applications, Active Interviews, Offer Yields, and Rejection ratios.
* **Dual Visualization Engine:**
* **Status Share Donut Chart:** Visual breakdown of where your pipeline sits across `Applied`, `Interview`, `Offer`, and `Rejected`.
* **Hiring Funnel Bars:** Horizontal conversion graph tracking stage dropoff and progression efficiency.


* **Smart Filter Deck:** Filter tabs with live count indicators (e.g. `Interview [08]`, `Offer [03]`) alongside dynamic monospace company badges.

A distraction-free, dedicated full-screen workspace engineered for rapid data entry:

* **Target Organization & Role Specs:** Structured field validation preventing incomplete logs.
* **Conduit & Identity Profiling:** Easily select which job board channel was used and which email credential you applied with.
* **One-Click Chrono Input:** Quick `NOW` trigger instantly stamps the current calendar date.
* **Metadata & Referral Notes:** Dedicated multiline capture for recruiter links, requisition IDs, take-home repository URLs, or referral contacts.

* **Pre-Decided Export Destination:** Set your target directory once (defaults to `./exports`).
* **Instant 1-Click Export:** Clicking `⚡ Instant Export to Excel (.xlsx)` creates clean, auto-named, timestamped reports without repetitive save dialog prompts.
* **Application Conduit Manager:** Add or delete customized sourcing portals (e.g. *Y Combinator*, *Wellfound*, *Company Career Site*).
* **Credential Email Manager:** Manage multiple personal, agency, or professional alias emails used across job boards.
* **Explorer Trigger:** Direct `Open Folder` button to reveal exported spreadsheets in Windows Explorer immediately.

---

## ⌨️ Keyboard Control Deck

AppliTrack features global power-user hotkeys for keyboard-driven navigation:

| Key Binding | Function | Scope |
| --- | --- | --- |
| Ctrl + 1 | Jump to **Vault Dashboard** | Global Window |
| Ctrl + 2 | Open **Full-Screen Application Logger** | Global Window |
| Ctrl + 3 | Open **System Config & Conduit Settings** | Global Window |
| F5 / Ctrl + R | Force Re-render & Refresh Analytics Telemetry | Global Window |
| Esc | Dismiss Active Modal / Dropdown | Active Dialog |

---

## 🏗️ Architecture

```text
applitrack/
├── app.py              # Root controller, DPI awareness, hotkeys & view router
├── database.py         # SQLite manager, migrations & automated export path settings
├── metrics.py          # Top executive telemetry cards & yield calculations
├── analytics.py        # Embedded Matplotlib canvas (Donut matrix & Funnel charts)
├── applications.py     # Filterable application cards, search bar & status pills
├── entry_view.py       # Full-screen ingestion terminal & input validation
├── settings_view.py    # Predetermined export engine, conduits & email manager
├── sidebar.py          # Titanium navigation bar with status indicator
└── app_icon.ico        # Custom multi-size Windows icon

```

---

## 🚀 Quickstart & Installation

### Prerequisites

* Python `3.10` or higher
* Windows 10 / 11 (Per-Monitor DPI scaling supported)

### 1. Clone the Repository

```bash
git clone [https://github.com/yourusername/applitrack.git](https://github.com/yourusername/applitrack.git)
cd applitrack

```

### 2. Configure Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate environment (PowerShell)
.\.venv\Scripts\Activate.ps1

```

### 3. Install Dependencies

```powershell
pip install customtkinter matplotlib pandas openpyxl pillow

```

### 4. Launch AppliTrack

```powershell
python app.py

```

---

## 📦 Compilation to Standalone .exe

Package AppliTrack into a standalone, portable Windows `.exe` that runs with zero external dependencies:

```powershell
# Install compiler
pip install pyinstaller

# Build single-file production binary
pyinstaller --noconsole `
            --onefile `
            --icon="app_icon.ico" `
            --add-data "app_icon.ico;." `
            --collect-all customtkinter `
            --name "AppliTrack" `
            app.py

```

> **Build Output:** Your portable binary is generated at `dist/AppliTrack.exe`. Run it from anywhere—it automatically initializes `applitrack.db` and `./exports` in its directory.

---

### 💼 AppliTrack — Career OS & Executive Pipeline Engine

Engineered for speed, privacy, and full pipeline ownership.