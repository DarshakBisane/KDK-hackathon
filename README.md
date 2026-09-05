Hosted Link :
https://kdk-hackathon-frontend-peach.vercel.app/
# Student Skill Gap Analyzer — Phase 1

> **Know Your Skill Gap. Build Your Career.**  
> A clean, minimal, student-friendly career-tech SaaS platform that analyzes student resumes using Gemini AI, computes deterministic skill gap readiness against target careers, and generates personalized learning roadmaps.

---

## 🚀 Overview

The **Student Skill Gap Analyzer (Phase 1)** provides an objective, reproducible bridge between a student's current skills and the requirements of industry career tracks. 

- **Gemini AI Resume Extraction**: Extracts structured skills, education, and projects directly from uploaded text-based PDF resumes without hallucinations.
- **Deterministic Skill-Gap Engine**: Computes exact readiness percentages based on matched vs. required skills.
- **Personalized Weekly Roadmap**: Translates missing skills into actionable learning milestones with interactive status tracking (*Not Started*, *Learning*, *Completed*).
- **Modern SaaS Aesthetics**: Minimalist, calm, soft-light UI with responsive navigation, consistent cards, progress bars, and feedback toasts.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS (Custom curated palette: `#F7F8FC`, `#6C63FF`, `#EEEAFE`, `#EAF8F1`, `#172033`)
- **Routing**: React Router v6 (Public and Protected Route guards)
- **Icons**: Lucide React
- **Animations**: Framer Motion & CSS transitions
- **HTTP Client**: Axios (with centralized JWT request/response interceptors)

### Backend
- **Framework**: Python 3.10+ / 3.14 + FastAPI
- **Database**: SQLite with SQLAlchemy ORM (Clean repository layer ready for PostgreSQL migration in Phase 2)
- **Validation**: Pydantic v2 schemas
- **Authentication**: JWT (JSON Web Tokens) with `bcrypt` password hashing
- **PDF Extraction**: PyPDF (with scanned/empty document validation)
- **AI Integration**: Google Generative Language / Gemini API (`gemini-2.5-flash` / `gemini-1.5-flash`)

---

## 📁 Project Structure

```
d:/Projects/KDK hackathon/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI Routers
│   │   │   ├── auth.py           # /api/auth/register, /api/auth/login
│   │   │   ├── users.py          # /api/users/me, /api/users/target-career
│   │   │   ├── careers.py        # /api/careers, /api/careers/{id}
│   │   │   ├── resumes.py        # /api/resumes/analyze
│   │   │   ├── skills.py         # /api/skills/gap, /api/skills/user
│   │   │   ├── dashboard.py      # /api/dashboard
│   │   │   ├── roadmap.py        # /api/roadmap, /api/roadmap/{id}
│   │   │   └── deps.py           # Auth Bearer & DB session dependencies
│   │   ├── database/
│   │   │   ├── session.py        # SQLite engine & session
│   │   │   └── seed.py           # 10 Careers & 35+ Skills seed dataset
│   │   ├── models/
│   │   │   └── models.py         # SQLAlchemy ORM models
│   │   ├── schemas/
│   │   │   └── schemas.py        # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── gemini_service.py # Gemini AI structured extraction
│   │   │   ├── resume_service.py # PDF to skill pipeline orchestrator
│   │   │   ├── normalization_service.py # Skill aliases normalizer
│   │   │   ├── skill_gap_service.py     # Deterministic readiness calculator
│   │   │   └── roadmap_service.py       # Milestone builder & status tracker
│   │   ├── utils/
│   │   │   ├── pdf_extractor.py  # PyPDF parser with empty/scanned validation
│   │   │   └── security.py       # Bcrypt hashing & JWT encoder/decoder
│   │   ├── config.py             # Settings & .env reader
│   │   └── main.py               # FastAPI entry, CORS, exception handlers
│   ├── tests/
│   │   ├── test_backend.py       # Pytest unit & integration tests
│   │   └── e2e_verify.py         # Complete end-to-end flow test script
│   ├── requirements.txt
│   ├── .env.example
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/           # Reusable UI component library
│   │   │   ├── Navbar.jsx        # Floating responsive SaaS navbar
│   │   │   ├── Button.jsx        # Standardized button variants
│   │   │   ├── Card.jsx          # Soft border & shadow container
│   │   │   ├── Input.jsx         # Accessible form inputs
│   │   │   ├── ProgressBar.jsx   # Linear & circular progress meters
│   │   │   ├── SkillBadge.jsx    # Matched vs Missing badges
│   │   │   ├── CareerCard.jsx    # Career track selection cards
│   │   │   ├── FileUpload.jsx    # PDF dropzone with multi-stage processing
│   │   │   ├── PageHeader.jsx    # Header with title & actions
│   │   │   ├── Modal.jsx         # Accessible dialog modal
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   ├── AuthContext.jsx   # Authentication state & actions
│   │   │   └── ToastContext.jsx  # Global notifications
│   │   ├── layouts/
│   │   │   └── MainLayout.jsx    # Layout container with Navbar & Footer
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx   # Hero, How It Works, Why Use It, CTA
│   │   │   ├── LoginPage.jsx     # User authentication
│   │   │   ├── RegisterPage.jsx  # Account creation
│   │   │   ├── ProfilePage.jsx   # Minimal student summary & edit modal
│   │   │   ├── CareerPage.jsx    # 10 Career track cards selector
│   │   │   ├── ResumePage.jsx    # PDF upload & AI extraction
│   │   │   ├── SkillGapPage.jsx  # Matched skills, missing skills, readiness %
│   │   │   ├── DashboardPage.jsx # Student summary, metric cards, next steps
│   │   │   └── RoadmapPage.jsx   # Weekly milestones & progress tracking
│   │   ├── services/
│   │   │   └── api.js            # Axios client with JWT interceptors
│   │   ├── App.jsx               # Route mapping
│   │   ├── main.jsx
│   │   └── index.css             # Tailwind design tokens
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── vite.config.js
├── .gitignore
└── README.md
```

---

## ⚡ Getting Started

### 1. Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **Gemini API Key**: Obtain a key from [Google AI Studio](https://aistudio.google.com/)

---

### 2. Backend Setup

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and provide your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   JWT_SECRET=your_custom_jwt_secret_key
   DATABASE_URL=sqlite:///./skillgap.db
   ENVIRONMENT=development
   ```

5. Run database migrations & start backend server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   The backend API will be live at `http://127.0.0.1:8000`.  
   Interactive Swagger docs available at `http://127.0.0.1:8000/docs`.

---

### 3. Frontend Setup

1. Open a second terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start Vite development server:
   ```bash
   npm run dev
   ```
   The web application will open at `http://localhost:5173`.

---

## 🧪 Running Automated Tests

Run backend unit and integration tests:
```bash
cd backend
pytest tests/test_backend.py -v
```

Run the complete end-to-end pipeline test (with real PDF extraction and Gemini AI):
```bash
python backend/tests/e2e_verify.py
```

---

## 🔐 Security & Architecture Highlights

1. **Zero Client-Side AI Secrets**: The Gemini API key is strictly stored on the backend in `.env` and is never bundled into frontend assets or returned in network responses.
2. **Deterministic Calculations**: Gemini is used exclusively for extracting structured resume information. Skill gap readiness ($matched / total \times 100$) and priority sorting are calculated via deterministic backend algorithms to ensure 100% reproducible results.
3. **Database Decoupling**: Database access uses clean SQLAlchemy models and session dependency injection, allowing seamless migration from SQLite to PostgreSQL in future phases.

---

## 📌 Phase 1 Features

- [x] Responsive Floating SaaS Navbar with active pill indicator & mobile drawer
- [x] Clean Landing Page with Hero, Pipeline visualization, How It Works, Why Use It, and CTA
- [x] JWT Authentication (Register, Login, Token verification, Protected routes)
- [x] Compact Student Profile (Basic info, career goal, detected skills list, Edit Profile modal)
- [x] Career Selection Grid (10 seeded tech roles with required skills dynamically loaded from DB)
- [x] PDF Resume Upload & Multi-Stage Processing Pipeline
- [x] Gemini AI Structured Extraction & Skill Normalization Layer
- [x] Deterministic Skill Gap Analysis (Readiness score gauge, matched skills in mint, missing skills in amber/lavender)
- [x] Student Analytics Dashboard (Readiness score, strong skills count, missing count, critical gaps, next steps)
- [x] Personalized Weekly Learning Roadmap with live milestone status toggles (*Not Started*, *Learning*, *Completed*)

---

## 🔮 Limitations of Phase 1

1. **Seeded Career Catalog**: Phase 1 uses a static seed dataset of 10 careers and 35+ core skills in SQLite rather than dynamic real-time job market scrapers.
2. **Local SQLite Storage**: Uploaded resume files and student records are stored in a local SQLite file (`skillgap.db`) rather than a multi-region distributed PostgreSQL database.
3. **Deterministic Learning Blueprints**: Roadmap milestones are generated from pre-configured curriculum blueprints mapped to missing skills rather than dynamic AI course search.

---

## 🗺️ Recommended Phase 2 Architecture

In Phase 2, the application can logically be expanded with:
1. **Dynamic Job Intelligence**: Integrate ESCO / O*NET taxonomy standards and live job postings (e.g. Adzuna / LinkedIn) to dynamically weight skill importance.
2. **PostgreSQL & Redis**: Migrate SQLite to PostgreSQL with `pgvector` for semantic skill similarity and Redis for caching frequent skill lookups.
3. **Skill Evidence & Confidence Scores**: Calculate skill proficiency levels based on project depth and years of experience mentioned in resumes.
4. **Learning Resource Recommendations**: Map missing skills directly to curated courses, GitHub repositories, and certification paths.
