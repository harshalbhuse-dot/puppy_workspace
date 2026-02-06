# 🎯 Geofence Radius Predictor

A production-ready tool for predicting optimal geofence radii for driver **arrival** (parking) and **delivery** locations.

![Walmart](https://img.shields.io/badge/Walmart-0071CE?style=for-the-badge&logo=walmart&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

## 📊 What It Does

Predicts two geofence radii based on:
- **Property Type**: House, Apartment, Business, Mobile Home, Dorm, Other
- **Address Source**: AMS, Google, Mapbox, Customer Pin
- **Population Density**: Urban High, Urban Medium, Suburban, Rural
- **Percentile**: P90, P95, P99
- **Access Required**: Yes/No (gated communities, buzzers, etc.)

| Geofence | Purpose | Description |
|----------|---------|-------------|
| 🚗 **Arrival Radius** | Where driver parks | Based on `ARRVL_DIST_METER` analysis |
| 📦 **Delivery Radius** | Where driver delivers | Based on `DLVRD_DISTANCE` analysis |

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Open http://localhost:8501 in your browser.

### Option 2: Local Development

```bash
# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
uv pip install -r geofence_ui/requirements.txt

# Run the app
cd geofence_ui
uvicorn app:app --reload --port 8501
```

Open http://localhost:8501 in your browser.

## 📁 Project Structure

```
geofence-radius-predictor/
├── geofence_model.py      # Core prediction logic
├── geofence_config.json   # Configuration & lookup tables
├── geofence_ui/
│   ├── app.py             # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── templates/
│       └── index.html     # HTMX + Tailwind UI
├── Dockerfile             # Container definition
├── docker-compose.yml     # Easy deployment
└── README.md              # You are here!
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI |
| `/predict` | GET | Get both radii (HTMX partial) |
| `/health` | GET | Health check |

### Example API Call

```bash
curl "http://localhost:8501/predict?property_type=HOUSE&address_source=AMS&density_category=SUBURBAN&percentile=P95&access_required=NO"
```

## 📈 Data Source

Based on analysis of **26.8M delivery records** from `Chirag_dx.20250501_dlvrd_distance`:
- `ARRVL_DIST_METER` → Arrival radius predictions
- `DLVRD_DISTANCE` → Delivery radius predictions

## 🎨 Tech Stack

- **Backend**: FastAPI + Python 3.12+
- **Frontend**: HTMX + Tailwind CSS
- **Deployment**: Docker
- **Data**: BigQuery

## 🔒 Security Notes

- No PII is stored or processed by this application
- All predictions are based on aggregated statistical data
- Data stays within Walmart's network (Eagle)

## 📞 Support

For questions or issues:
- Slack: #element-genai-support
- Teams: [WMT AI Innovation Lab](https://teams.microsoft.com/l/channel/19%3AGbP8DGJjrXq1sL3IlXErZc5U7hk-IEqsokmnImcKyP41%40thread.tacv2/General?groupId=51caa2b5-ff58-4dc0-9ee0-c20eea1de9f8&tenantId=3cbcc3d3-094d-4006-9849-0d11d61f484d)

## 📄 License

Internal Walmart use only.

---

*Built with ❤️ by Code Puppy 🐶*
