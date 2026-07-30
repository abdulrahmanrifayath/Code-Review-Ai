# ReviewAI – AI-Powered Code Review Platform

**ReviewAI** is an enterprise-grade, production-quality SaaS application designed to integrate with GitHub repositories, automatically analyze Pull Requests, detect bugs, security vulnerabilities, performance bottlenecks, and code smells, while generating AI-driven code review comments, test cases, documentation, and professional reports.

---

## 🏗 System Architecture & Design Principles

The application is architected following **Clean Architecture** principles and the **Repository-Service Pattern** to ensure complete separation of concerns, high maintainability, testability, and enterprise scalability.

```
                  +-----------------------------------+
                  |         React Frontend            |
                  |  (React Router, Query, Axios)     |
                  +-----------------+-----------------+
                                    | REST API (JWT)
                                    v
                  +-----------------------------------+
                  |          FastAPI Backend          |
                  |                                   |
                  |  +-----------------------------+  |
                  |  |         API Controllers     |  |
                  |  +--------------+--------------+  |
                  |                 |                 |
                  |  +--------------v--------------+  |
                  |  |      Service Layer (Domain) |  |
                  |  +--------------+--------------+  |
                  |                 |                 |
                  |  +--------------v--------------+  |
                  |  |    Repository (Data Access) |  |
                  |  +--------------+--------------+  |
                  +-----------------|-----------------+
                                    | Async ORM
                                    v
                         +----------+----------+
                         | PostgreSQL / Redis  |
                         +---------------------+
```

### Key Architectural Layers:
1. **API Layer (`app/api`)**: Endpoints, OAuth2 authentication, request validation, and HTTP dependency injection.
2. **Service Layer (`app/services`)**: Business logic, orchestrating AI analysis pipelines (LangGraph, Tree-sitter), GitHub webhooks, and third-party APIs.
3. **Repository Layer (`app/repositories`)**: Data access layer wrapping SQLAlchemy async queries behind clean, abstract interfaces.
4. **Core Layer (`app/core`)**: Configuration management (Pydantic Settings), database session factories, structured logging, JWT security, and global exception handlers.
5. **Models Layer (`app/models`)**: SQLAlchemy ORM entity definitions.
6. **Schemas Layer (`app/schemas`)**: Pydantic DTOs for request/response serialization and validation.

---

## 📁 Comprehensive Folder Directory Explanation

Below is an exhaustive breakdown explaining the responsibility of every folder in the codebase:

### Root Level
- **`.github/workflows/`**: Continuous Integration (CI) automated pipelines for linting, type-checking, and running backend & frontend tests.
- **`backend/`**: Complete FastAPI backend service codebase.
- **`frontend/`**: Complete React TypeScript Vite web app frontend codebase.

---

### Backend Folder Breakdown (`backend/`)
- **`backend/app/`**: Root package of the Python FastAPI application.
- **`backend/app/api/`**: REST API endpoints and routing controllers.
  - **`backend/app/api/v1/`**: Version 1 API endpoints routing.
  - **`backend/app/api/v1/endpoints/`**: Specific resource route handlers (`auth.py`, `health.py`, `repositories.py`, `reviews.py`).
  - **`backend/app/api/deps.py`**: FastAPI dependency injection providers (DB sessions, current user authentication, service resolution).
- **`backend/app/core/`**: Application core components.
  - **`config.py`**: Pydantic `BaseSettings` loading environment variables.
  - **`database.py`**: Async SQLAlchemy engine and `AsyncSession` context managers.
  - **`errors.py`**: Custom application exception classes (`NotFoundError`, `ValidationError`, etc.) and global FastAPI error handlers.
  - **`logging.py`**: Structured Python standard logging configuration.
  - **`security.py`**: Password hashing (Bcrypt) and JWT token generation/validation utilities.
- **`backend/app/models/`**: Declarative SQLAlchemy ORM database models (`user.py`, `repository.py`, `review.py`).
- **`backend/app/schemas/`**: Pydantic schemas enforcing input validation and output API formatting.
- **`backend/app/repositories/`**: Repository layer abstractions encapsulating database query logic (`base.py`, `user.py`, `repository.py`).
- **`backend/app/services/`**: Service layer encapsulating domain business logic (`auth.py`, `github.py`, `ai_review.py`).
- **`backend/tests/`**: Automated test suite directory for unit and integration testing.

---

### Frontend Folder Breakdown (`frontend/`)
- **`frontend/public/`**: Static assets served directly without Vite build transformation.
- **`frontend/src/`**: Application TypeScript source code.
  - **`frontend/src/assets/`**: Images, logos, SVG icons, and visual media.
  - **`frontend/src/components/`**: Reusable React UI components.
    - **`components/common/`**: Application-wide structural components (`Header.tsx`, `Sidebar.tsx`, `LoadingSpinner.tsx`).
    - **`components/ui/`**: Low-level UI controls (buttons, modals, form inputs).
  - **`frontend/src/hooks/`**: Custom React hooks (`useAuth.ts`, `useRepositories.ts`).
  - **`frontend/src/layouts/`**: Top-level page layout templates (`DashboardLayout.tsx`).
  - **`frontend/src/pages/`**: Route-level view components (`DashboardPage.tsx`, `LoginPage.tsx`, `RepositoriesPage.tsx`, `ReviewsPage.tsx`).
  - **`frontend/src/services/`**: API client instances (`api.ts`) configured with Axios interceptors for JWT injection.
  - **`frontend/src/store/`**: Global state management stores (`authStore.ts`).
  - **`frontend/src/types/`**: TypeScript interfaces and type definitions (`index.ts`).
  - **`frontend/src/utils/`**: Helper utility functions (formatting, date utilities).

---

## 🛠 Tech Stack Overview

- **Frontend**: React 18, TypeScript, TailwindCSS v3, React Router v6, React Query (TanStack Query v5), Axios, Vite.
- **Backend**: FastAPI, Async SQLAlchemy 2.0, PostgreSQL 16, Redis 7, PyJWT, Passlib, Pydantic v2.
- **AI Integrations**: LangGraph, OpenAI-compatible API, Tree-sitter AST parsers, ESLint/Pylint integration.
- **DevOps**: Docker, Docker Compose, GitHub Actions CI.
- **Linting & Formatting**: Ruff, Pylint, Black for Python; ESLint, Prettier for TypeScript.

---

## 🚀 Quickstart Guide

### Option 1: Running with Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/Code-Review-Ai.git
   cd Code-Review-Ai
   ```

2. **Configure Environment Variables**:
   Copy the example environment files:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start Containers**:
   ```bash
   docker-compose up --build
   ```

4. **Access the Services**:
   - **Frontend UI**: [http://localhost:5173](http://localhost:5173)
   - **Backend API**: [http://localhost:8000](http://localhost:8000)
   - **Interactive API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option 2: Running Locally for Development

#### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Code Quality & Verification

Run backend linting and quality checks:
```bash
cd backend
ruff check .
pylint app
```

Run frontend type-checking and linting:
```bash
cd frontend
npx tsc --noEmit
npm run lint
```
