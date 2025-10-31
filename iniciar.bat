@echo off
title SEPLAN Backend - FastAPI
cd /d C:\seplan

REM Ativa ambiente virtual
call .venv\Scripts\activate

REM Abre Swagger automaticamente
start http://127.0.0.1:8000/docs

REM Inicia servidor com logs
uvicorn main:app --reload --reload-dir "C:\seplan" --log-config logging.yaml
