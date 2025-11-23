@echo off
REM Load ANTHROPIC_API_KEY from environment variable or .env file
REM Set it in your system environment or create a .env file in the project root
cd C:\Users\18023\island-harvest-enterprise

REM Load environment variables from .env file
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" (
            set "%%a=%%b"
        )
    )
)

call venv\Scripts\activate
streamlit run island_harvest_hub/main.py --server.port 8501 --server.address localhost
