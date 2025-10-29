# Test Plan — CodeCollab

## 1. Overview

This document defines the testing strategy, environment, and objectives for the **CodeCollab** web application — a collaborative project and task management platform built with **FastAPI (Python)**, **PostgreSQL**, and **React (Vite)**.

The purpose of testing is to validate all backend REST API endpoints, database integrity, authentication mechanisms, and the integration between backend and frontend components.

## 2. Objectives

1. Verify functional correctness of all backend endpoints (`/auth`, `/users`, `/projects`, `/tasks`, `/admin`).
2. Validate data persistence and relational integrity in PostgreSQL.
3. Ensure frontend integration with backend APIs.
4. Confirm security of authentication and authorization layers.
5. Evaluate system stability and error handling.

## 3. Scope

### In Scope
- Unit and integration tests for all FastAPI routes.
- Database operations (CRUD) on PostgreSQL.
- Authentication and authorization flow.
- API–frontend interaction via REST.
- Admin route verification (`reset-users`, `reset-all`).

### Out of Scope
- UI testing (handled in React Vite project).
- Load and stress testing beyond development scale.
- Third-party integrations (future roadmap).

## 4. Test Strategy

Testing will be performed using **automated pytest-based testing** integrated with a **PostgreSQL Docker test instance**.

### Frameworks and Tools
| Type | Tool |
|------|------|
| Test runner | pytest |
| Async client | httpx.AsyncClient |
| Database | PostgreSQL (Docker container) |
| ORM | SQLAlchemy |
| Web framework | FastAPI |
| Coverage | pytest-cov |
| CI/CD | GitHub Actions |

## 5. Test Environment

| Component | Technology |
|------------|-------------|
| OS | Windows 11 |
| Backend | FastAPI (Python 3.11) |
| Frontend | React (Vite) |
| Database | PostgreSQL 15 (Docker instance) |
| Test DB | `codecollab_test` |
| Port | 8000 (backend), 5173 (frontend) |

### Docker test database configuration:
```yaml
version: "3.9"
services:
  db_test:
    image: postgres:15
    container_name: codecollab_test_db
    environment:
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
      POSTGRES_DB: codecollab_test
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "test_user"]
      interval: 5s
      retries: 5
```

## 6. Test Types and Coverage

| Type | Purpose |
|------|----------|
| **Unit Tests** | Verify isolated CRUD logic and models |
| **API Integration Tests** | Validate HTTP routes and business flow |
| **Auth Tests** | Confirm JWT creation, expiry, and user roles |
| **DB Tests** | Check data integrity, constraints, relationships |
| **Security Tests** | Verify token protection and permissions |

## 7. Risks and Mitigation

| Risk | Mitigation |
|------|-------------|
| Database schema changes break tests | Use migrations per test setup |
| Token expiration during tests | Extend JWT lifetime for test environment |
| Docker DB startup delay | Add healthcheck with retries before running tests |

✅ **Risk level:** Low–Moderate

## 8. Entry and Exit Criteria

**Entry**
- All dependencies installed.
- Docker test database running and healthy.
- Backend application imports without errors.

**Exit**
- All tests executed successfully.
- Critical and major defects resolved.
- API endpoints verified in `/docs`.

## 9. Reporting and Deliverables

| Deliverable | Description |
|--------------|-------------|
| TEST_PLAN.md | This document |
| TEST_RESULTS.md | Execution results |
| TESTING_SUMMARY.md | Summary and conclusions |