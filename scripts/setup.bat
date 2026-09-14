@echo off
REM Setup script for AI Job Matching System (Windows)

echo Setting up AI Job Matching System...

REM Backend setup
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend
npm install
cd ..

REM Job collector setup
echo Setting up job collector...
cd job-collector
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

REM Database setup
echo Setting up database...
cd database
python seed.py
cd ..

echo Setup complete!
echo To start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo To start the frontend: cd frontend ^&^& npm run dev
echo To start the job collector: cd job-collector ^&^& venv\Scripts\activate ^&^& python main.py
