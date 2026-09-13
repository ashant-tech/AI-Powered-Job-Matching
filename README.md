# AI Job Matching System

An intelligent job matching platform that uses artificial intelligence to connect job seekers with relevant opportunities based on their skills, experience, and preferences.

## 🚀 Features

### For Job Seekers
- **Smart CV Analysis**: AI-powered extraction of skills, experience, and qualifications from your CV
- **Intelligent Job Matching**: Semantic matching algorithms to find the best job opportunities
- **Personalized Recommendations**: Tailored job suggestions based on your profile
- **Application Tracking**: Monitor your application status and get notified of updates
- **Skill Gap Analysis**: Identify skills you need to develop for your dream jobs

### For Employers
- **Automated Candidate Screening**: AI-powered ranking of candidates based on job requirements
- **Market Intelligence**: Salary benchmarking and skill availability analysis
- **Streamlined Hiring**: Integrated tools for managing the recruitment process
- **Quality Candidates**: Access to pre-qualified, matched candidates

## 🏗️ Architecture

The system consists of three main components:

### Frontend (Next.js + TypeScript + Tailwind CSS)
- Modern, responsive user interface
- Real-time updates and notifications
- Mobile-friendly design
- Type-safe development with TypeScript

### Backend (Python + FastAPI)
- RESTful API with comprehensive endpoints
- AI/ML-powered processing pipeline
- Secure authentication with JWT
- Scalable architecture

### Job Collector
- Automated job aggregation from multiple sources
- Data cleaning and deduplication
- Scheduled execution
- Extensible source integrations

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for containerized deployment)

## 🛠️ Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
cd ../database
python seed.py
```

6. Run the backend server:
```bash
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Job Collector Setup

1. Navigate to the job collector directory:
```bash
cd job-collector
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the job collector:
```bash
python main.py
```

## 🐳 Docker Deployment

For easy deployment, use Docker Compose:

```bash
docker-compose up --build
```

This will start:
- Backend API on port 8000
- Frontend on port 3000
- PostgreSQL database
- Job collector service

## 📖 API Documentation

Comprehensive API documentation is available in the `docs/api-documentation.md` file.

Key endpoints:
- Authentication: `/api/auth/*`
- User Management: `/api/users/*`
- CV Management: `/api/cv/*`
- Jobs: `/api/jobs/*`
- Matching: `/api/matching/*`
- Notifications: `/api/notifications/*`

## 🤖 AI Components

The system uses several AI/ML components:

- **CV Analysis**: Extracts structured information from unstructured CV text
- **Skill Extraction**: Identifies and categorizes skills from CV text
- **Job Analysis**: Analyzes job descriptions to extract requirements
- **Semantic Matching**: Calculates compatibility between CVs and jobs
- **Text Embeddings**: Generates vector representations for semantic analysis
- **Match Ranking**: Ranks and filters job matches for optimal results

Detailed documentation is available in `docs/ai-model.md`.

## 🗄️ Database

The system uses SQLite by default (for development) and can be configured to use PostgreSQL for production.

### Database Schema

- `users` - User accounts and profiles
- `cvs` - User uploaded CVs
- `jobs` - Job postings
- `skills` - Skills catalog
- `matches` - Job matching results
- `notifications` - User notifications

### Migrations

Database migrations are managed in the `database/migrations/` directory.

Run migrations:
```bash
python database/migrations/001_initial_schema.py
```

Seed the database with sample data:
```bash
python database/seed.py
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/app/config/settings.py` to configure:
- Database connection
- JWT settings
- File upload settings
- AI/ML API keys
- Email/SMS settings

### Frontend Configuration

Edit `frontend/package.json` and environment variables to configure:
- API endpoints
- Feature flags
- Analytics settings

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📚 Documentation

- [System Architecture](docs/system-architecture.md)
- [API Documentation](docs/api-documentation.md)
- [AI Model Documentation](docs/ai-model.md)
- [Ideation Process](docs/ideation-process.md)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with modern web technologies
- Inspired by the need for intelligent job matching
- Uses open-source AI/ML libraries

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

## 🗺️ Roadmap

### Phase 1: Foundation (Current)
- ✅ Basic authentication
- ✅ CV upload and analysis
- ✅ Job collection system
- ✅ Basic matching algorithm
- ✅ User dashboard

### Phase 2: Core Features
- ⏳ Advanced semantic matching
- ⏳ Machine learning models
- ⏳ Personalized recommendations
- ⏳ Employer portal

### Phase 3: Advanced Features
- ⏳ Real-time notifications
- ⏳ Video interviewing
- ⏳ Skill assessment tests
- ⏳ Mobile applications

### Phase 4: Ecosystem
- ⏳ API integrations
- ⏳ Third-party job boards
- ⏳ Career coaching
- ⏳ Salary optimization

---

Built with ❤️ using modern web technologies and artificial intelligence.
