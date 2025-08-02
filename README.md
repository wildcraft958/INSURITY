# INSURITY: AI-Powered Telematics Insurance Platform

INSURITY is an advanced insurance technology platform leveraging AI and machine learning for dynamic risk assessment, personalized premiums, and gamified driver improvement.

## Features

- **Multi-Expert Risk Assessment:** Four specialized AI models (Behavior, Geographic, Contextual, Gating)
- **Dynamic Premiums:** Real-time pricing based on driving data
- **Gamification Engine:** Points, badges, and challenges to promote safe driving
- **Claims Analytics:** ML-powered frequency and severity predictions
- **Interactive Dashboard:** Real-time driver and risk visualization
- **Scalable Microservices:** Production-ready architecture

## Architecture

- **Backend (FastAPI):** RESTful API serving expert models and business logic
- **Dashboard (Streamlit):** Interactive data visualization
- **Gamification (Flask):** Points, badges, leaderboards
- **Database (PostgreSQL):** Secure, scalable storage
- **Expert Notebooks:** Jupyter notebooks for model R&D

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy, Pydantic, Uvicorn
- **ML/Data Science:** Scikit-learn, TensorFlow/Keras, XGBoost, SciPy, NumPy, Pandas, GeoPandas
- **Visualization:** Streamlit, Plotly, Folium, Matplotlib, Seaborn
- **Infrastructure:** Docker, Redis, Celery, Prometheus

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)
- Git

### Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd INSURITY
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   - Create `.env` in `backend/` (see example in README)
   - Set up PostgreSQL (see `deployment/aiven-setup.md`)
   - Initialize DB:  
     `python -c "from app.services.db import create_tables; create_tables()"`

4. **Run Services**
   - Backend: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - Dashboard:  
     ```bash
     cd dashboard
     pip install -r requirements.txt
     streamlit run app.py --server.port 8501
     ```
   - Gamification:  
     ```bash
     cd gamification
     pip install -r requirements.txt
     python app.py
     ```

## API Endpoints

- `GET /` – Health check
- `POST /assess-risk` – Risk assessment
- `POST /analyze-route` – Route risk analysis
- `POST /predict-claims` – Claims prediction
- `GET /driver/{driver_id}/trends` – Driver trends
- `POST /gamification/award-points` – Award points
- `GET /gamification/leaderboard` – Leaderboard

Full docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Contributing

- Fork, branch, commit, and open a PR
- Follow PEP 8, use type hints, and maintain >80% test coverage

## License

MIT License. See LICENSE file.

---

For technical details, see `ENHANCEMENT_SUMMARY.md`, deployment configs in `deployment/`, and model notebooks in `experts-notebooks/`.

---
