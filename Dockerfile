FROM node:20-alpine AS frontend
WORKDIR /frontend

COPY frontend/ .
RUN npm install && npm run build

FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/main.py backend/functions.py ./
COPY --from=frontend /frontend/dist ./frontend/dist

RUN mkdir -p /data
EXPOSE 8001

WORKDIR /data
CMD ["uvicorn", "main:app", "--app-dir", "/app", "--host", "0.0.0.0", "--port", "8001"]
