#!/bin/bash

# Setup script for AI Job Matching System

echo "Setting up AI Job Matching System..."

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

# Job collector setup
echo "Setting up job collector..."
cd job-collector
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Database setup
echo "Setting up database..."
cd database
python seed.py
cd ..

echo "Setup complete!"
echo "To start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "To start the frontend: cd frontend && npm run dev"
echo "To start the job collector: cd job-collector && source venv/bin/activate && python main.py"
