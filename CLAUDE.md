# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ORE is a modern AI workflow engine that integrates LangChain 0.3 with FastAPI, providing enterprise-grade solutions for AI-powered workflow orchestration. The project consists of two main components:

1. **Workflow Engine** (`workflow_engine/`) - Tree-based workflow execution engine with LangChain integration
2. **Web Backend** (`backend/`) - FastAPI-based REST API service with JWT authentication

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev,test]"

# Install all optional dependencies
pip install -e ".[dev,test,prod,docs]"
```

### Running the Application

#### Web Server
```bash
# Start development server (auto-reload enabled)
workflow-server --reload

# Start production server
workflow-server --workers 4

# Direct uvicorn command
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Workflow Engine
```bash
# Run workflow engine CLI
workflow-engine

# Run example workflow
python -m workflow_engine.examples.tree_workflow
```

### Development Tools
```bash
# Code formatting
black .
isort .

# Static analysis
mypy .
ruff check .

# Testing
pytest
pytest backend/tests/test_auth.py  # Run specific test file
pytest --cov=backend --cov-report=html  # With coverage
```

## Architecture Overview

### Workflow Engine Architecture

The workflow engine is built on a modular, extensible architecture:

- **Base Engine** (`workflow_engine/base/engine.py`): Abstract base class defining common workflow execution patterns
- **Tree Engine** (`workflow_engine/engines/tree/`): Concrete implementation for tree-structured workflows
- **Type System** (`workflow_engine/workflow_types.py`): Core type definitions shared across all engines

#### Key Workflow Engine Concepts

1. **Node Types**: START, INTERMEDIATE, LEAF
2. **Execution Flow**: Event-driven execution with dependency checking
3. **LLM Integration**: Uses LangChain 0.3 with ChatPromptTemplate for variable substitution
4. **Parallel Execution**: Supports multiple start nodes and concurrent execution
5. **Cycle Detection**: Automatic cycle detection during graph construction

### Backend API Architecture

FastAPI-based REST API with modern Python practices:

- **Layered Architecture**: API → Services → Models
- **Authentication**: JWT-based with Argon2 password hashing
- **Configuration**: Pydantic settings management
- **Exception Handling**: Centralized error handling with custom exceptions
- **CORS Support**: Configurable cross-origin resource sharing

## Configuration

### Environment Variables

Essential environment variables (see `.env.example`):

```bash
# AI Service Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key  # Alternative provider

# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key  # Auto-generated if not provided

# Application
APP_ENV=development
LOG_LEVEL=INFO
```

### Workflow Configuration

Workflow settings are managed in `config/workflow_config.py`:

- LLM provider selection (OpenAI, Anthropic, custom)
- Model parameters (temperature, max_tokens)
- Execution settings

## Code Patterns and Conventions

### Workflow Engine Development

When extending the workflow engine:

1. **Inherit from BaseWorkflowEngine**: All workflow engines must extend the base class
2. **Implement Required Methods**: `_initialize_from_config()` and `execute_workflow()`
3. **Use Event-Driven Patterns**: Leverage the async execution loop for node orchestration
4. **LangChain Integration**: Use ChatPromptTemplate with input_variables for dynamic content

### API Development

When adding new API endpoints:

1. **Follow REST Conventions**: Use appropriate HTTP methods and status codes
2. **Pydantic Schemas**: Define request/response models in `backend/schemas/`
3. **Dependency Injection**: Use FastAPI's dependency system for auth and services
4. **Error Handling**: Raise appropriate custom exceptions for business logic errors

### Testing Patterns

- **Async Testing**: Use `pytest-asyncio` for testing async workflow functions
- **API Testing**: Use `httpx` for FastAPI endpoint testing
- **Mocking**: Mock LLM calls during testing to avoid API costs

## Important File Locations

- **Main Application**: `backend/main.py` - FastAPI app initialization
- **CLI Entry**: `backend/cli.py` - Command-line server startup
- **Workflow Base**: `workflow_engine/base/engine.py` - Core workflow abstractions
- **Tree Engine**: `workflow_engine/engines/tree/engine.py` - Main workflow implementation
- **Configuration**: `config/` - Centralized settings management
- **Project Config**: `pyproject.toml` - Dependencies and tool configurations

## Security Considerations

- **Password Hashing**: Uses Argon2 for secure password storage
- **JWT Tokens**: Cryptographically signed authentication tokens
- **Environment Secrets**: Never commit API keys or secrets to version control
- **Input Validation**: All API inputs validated through Pydantic schemas

## Performance Notes

- **Async Execution**: Workflow engine uses asyncio for concurrent node execution
- **LLM Caching**: Consider implementing response caching for repeated prompts
- **Database Optimization**: Use connection pooling in production environments
- **Resource Monitoring**: Monitor LLM API usage and costs

## Troubleshooting

### Common Issues

1. **LLM API Failures**: Check API keys and network connectivity; engine provides graceful fallback
2. **Workflow Cycles**: Tree engine automatically detects and prevents cycles during construction
3. **Dependency Issues**: Ensure all prerequisite nodes complete before dependent nodes execute
4. **Port Conflicts**: Default server port is 8000; use `--port` flag to change

### Debug Mode

Enable debug mode for development:
```bash
export APP_ENV=development
```

This enables:
- FastAPI docs at `/docs` and `/redoc`
- Detailed error messages
- Auto-reload functionality