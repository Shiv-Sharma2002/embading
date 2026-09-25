# POI Semantic Search — Deploy Guide

## Local run
```
pip install -r requirements.txt
uvicorn app:app --reload
```
Open: http://127.0.0.1:8000  (frontend) | /docs (API) | /api/health

## Deploy option 1: Render (free, easiest)
1. GitHub repo banao, ye folder push karo.
2. render.com -> New Web Service -> repo select.
3. Build: `pip install -r requirements.txt`, Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. `render.yaml` already included hai — auto-detect ho jayega.

## Option 2: Railway / Fly / VPS (Docker)
```
docker build -t poi-app .
docker run -p 8000:8000 poi-app
```

## Option 3: Vercel (frontend+API same repo)
Frontend `static/` hai, API FastAPI hai — Vercel python runtime se deploy ho jayega, ya Render recommended hai.

## API
- GET  /api/health
- GET  /api/pois
- POST /api/search {"query":"not vegetarian","method":"semantic","threshold":0.05,"top_k":5}
- GET  /api/search?q=veg&method=semantic
- POST /api/pois  | DELETE /api/pois/{pid}
