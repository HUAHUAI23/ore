# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ORE is an AI workflow engine and web backend that integrates LangChain and FastAPI to provide enterprise-grade AI application solutions. It consists of:

- **Backend**: FastAPI-based REST API server with JWT authentication and modern security
- **Frontend**: React + TypeScript SPA with TanStack Router, React Query, and Tailwind CSS
- **Workflow Engine**: Pluggable AI workflow system supporting tree, DAG, and graph execution patterns
- **Multi-language support**: i18next for internationalization

## Development Commands

### Backend Development

```bash
# Start development server
workflow-server
# or
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Start server with custom options
workflow-server --host 0.0.0.0 --port 8000 --reload --env development

# Install project in development mode
pip install -e ".[dev,test]"

# Run tests
pytest
pytest backend/tests/test_auth.py  # specific test file
pytest --cov=backend --cov-report=html  # with coverage

# Code quality
black .                # format code
isort .               # sort imports  
mypy .                # type checking
ruff check .          # linting
pre-commit run --all-files  # run all hooks
```

### Frontend Development

```bash
# Navigate to frontend directory first
cd frontend

# Start development server
bun run dev
# or
bun run start

# Build for production
bun run build

# Run tests
bun run test

# Linting and formatting
bun run lint          # check linting
bun run lint:fix      # auto-fix linting issues
bun run format        # format code
bun run format:check  # check formatting
bun run check         # run both lint and format checks
bun run fix           # fix both lint and format issues
```

### Workflow Engine

```bash
# Run workflow engine CLI
workflow-engine

# Run example workflows
python -m workflow_engine.examples.tree_workflow
```

## Architecture Overview

### Backend Architecture (`backend/`)

- **FastAPI Application**: Modern async web framework with automatic OpenAPI docs
- **Authentication**: JWT-based auth with Argon2 password hashing (`backend/core/auth.py`)
- **Database**: SQLModel + SQLAlchemy with async support, PostgreSQL/SQLite compatibility
- **API Structure**: Versioned REST API under `/api/v1/` prefix
- **Configuration**: Pydantic Settings with environment variable support
- **Error Handling**: Centralized exception handlers with consistent response format

Key files:
- `backend/main.py`: FastAPI app initialization and middleware setup
- `backend/cli.py`: Command-line server launcher
- `backend/api/v1/`: API route definitions
- `backend/core/`: Core configuration and security
- `backend/services/`: Business logic layer

### Frontend Architecture (`frontend/`)

- **React 19** with TypeScript for type safety
- **TanStack Router**: File-based routing with type-safe navigation
- **TanStack Query**: Server state management and caching
- **Zustand**: Client-side state management
- **Tailwind CSS v4**: Utility-first styling with shadcn/ui components
- **Vite**: Build tool with HMR and code splitting
- **i18next**: Internationalization with language detection

Key files:
- `frontend/src/main.tsx`: App entry point with providers
- `frontend/src/routes/`: File-based route definitions
- `frontend/src/api/`: API client and service layer
- `frontend/src/store/`: Zustand state stores
- `frontend/src/components/`: Reusable UI components

### Workflow Engine (`workflow_engine/`)

Pluggable architecture supporting multiple execution patterns:
- **Base Engine** (`workflow_engine/base/engine.py`): Abstract base class for all engines
- **Tree Engine** (`workflow_engine/engines/tree/`): Hierarchical workflow execution
- **Configuration-driven**: JSON/YAML workflow definitions
- **Async Execution**: Built on asyncio for high performance

## Key Configuration Files

- `pyproject.toml`: Python project configuration with dependencies and tool settings
- `frontend/package.json`: Node.js dependencies and scripts
- `frontend/vite.config.ts`: Vite build configuration with path aliases
- `frontend/tsconfig.json`: TypeScript compiler options
- `.env`: Environment variables (copy from `.env.example`)

## API Documentation

When the development server is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See `docs/API_GUIDE.md` for comprehensive API usage examples and client code.

## Database Schema

The project uses SQLModel for ORM with these key models:
- `backend/models/user.py`: User account management
- Database migrations handled by Alembic (configured in `backend/db/`)

## Testing Strategy

- **Backend**: pytest with async support, coverage reporting
- **Frontend**: Vitest with jsdom environment, React Testing Library
- Test files located in `backend/tests/` and frontend uses `.test.ts` suffixes

## Environment Setup

1. **Backend setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -e ".[dev,test]"
   ```

2. **Frontend setup**:
   ```bash
   cd frontend
   bun install
   ```

3. **Environment variables**:
   - Copy `.env.example` to `.env` and configure API keys
   - Frontend env files: `.env.development`, `.env.template`

## Common Development Patterns

### Adding New API Endpoints

1. Create route in `backend/api/v1/`
2. Define Pydantic schemas in `backend/schemas/`
3. Implement business logic in `backend/services/`
4. Register router in `backend/main.py`

### Frontend Component Development

- Use shadcn/ui components from `@/components/ui/`
- Store API calls in `@/api/` with TanStack Query hooks
- Manage state with Zustand stores in `@/store/`
- Add routes as files in `@/routes/` (auto-generated routing)

### Workflow Engine Extensions

- Implement `BaseWorkflowEngine` interface
- Register new engines in `workflow_engine/engines/__init__.py`
- Add configuration schemas to `workflow_engine/workflow_types.py`

## Code Style and Quality

- **Python**: Black (88 char), isort, mypy, ruff
- **Frontend**: ESLint, Prettier, TypeScript strict mode
- **Commit hooks**: pre-commit configured for automated checks
- **Import sorting**: Absolute imports preferred, path aliases with `@/`

## Authentication Flow

1. User registers/logs in via `/api/v1/auth/register` or `/api/v1/auth/login`
2. Server returns JWT access token
3. Frontend stores token and includes in Authorization header
4. Protected routes require valid JWT token

## Internationalization

- Backend: Uses English for API responses and logging
- Frontend: i18next with JSON translation files in `public/locales/`
- Supported languages: English (en), Chinese (zh)
- Language detection via browser settings and localStorage