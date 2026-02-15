# CI/CD Pipeline

## Overview

Continuous Integration/Continuous Deployment (CI/CD) automates testing, building, and deployment of code changes.

---

## CI/CD Philosophy

### Continuous Integration (CI)
- **Every push triggers automated checks**
- Tests run automatically
- Code quality checks
- Security scans
- Fast feedback on code quality

### Continuous Deployment (CD)
- **Automated deployment after approval**
- Staging environment testing
- Production deployment
- Rollback capabilities

---

## Current CI/CD Setup

### GitHub Actions Workflows

Located in `.github/workflows/`

#### 1. Code Review Workflow (`claude-code-review.yml`)

**Triggers:**
- On pull request open
- On pull request update

**Actions:**
- Automated code review using Claude AI
- Checks code quality
- Identifies issues
- Suggests improvements

**Configuration:**
```yaml
name: Claude Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-review@v1
```

#### 2. Main CI Workflow (`claude.yml`)

**Triggers:**
- On push to any branch
- On pull request

**Actions:**
- Run tests
- Check code formatting
- Run linters
- Security scanning

---

## Planned CI/CD Pipeline

### Stage 1: Code Quality Checks

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: ['**']
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 black pylint

      - name: Run Black
        run: black --check src/ tests/

      - name: Run Flake8
        run: flake8 src/ tests/

      - name: Run Pylint
        run: pylint src/
```

### Stage 2: Testing

```yaml
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Tests
        run: pytest tests/ -v --cov=src

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Stage 3: Security Scanning

```yaml
  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/

      - name: Check Dependencies
        run: |
          pip install safety
          safety check
```

### Stage 4: Build (if applicable)

```yaml
  build:
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker Image
        run: docker build -t beatthebooksmodel:${{ github.sha }} .

      - name: Push to Registry
        run: docker push beatthebooksmodel:${{ github.sha }}
```

---

## Required Checks for PR Merge

Before merging to `main`, these checks must pass:

- ✅ All tests pass
- ✅ Code style checks pass (Black, Flake8)
- ✅ No linting errors (Pylint)
- ✅ Security scans pass (Bandit, Safety)
- ✅ Code review approved
- ✅ No merge conflicts
- ✅ Branch up-to-date with main

**Set in GitHub:**
- Settings → Branches → Branch protection rules → Require status checks

---

## Local Pre-commit Checks

### Install Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'src/']
```

### Running Pre-commit

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files (automatic on git commit)
pre-commit run
```

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /----\     Integration Tests (Some)
     /------\    Unit Tests (Many)
    /________\
```

### Unit Tests (Many)
- Test individual functions
- Fast execution
- No external dependencies
- High coverage

```python
# tests/test_excel_scraper.py
def test_read_excel_urls():
    """Test reading URLs from Excel file."""
    # Test logic...
```

### Integration Tests (Some)
- Test component interactions
- Database connections
- External API calls
- Slower execution

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_scrape_real_excel():
    """Test full scraping workflow."""
    # Test with real database and Excel file
```

### E2E Tests (Few)
- Test complete user workflows
- Real environment
- Slowest execution
- Most realistic

```python
# tests/test_e2e.py
def test_complete_scraping_workflow():
    """Test entire scraping process end-to-end."""
    # Upload Excel → Scrape → Verify database
```

---

## CI/CD Best Practices

### ✅ DO

1. **Keep builds fast**
   - Target: <10 minutes for full pipeline
   - Parallelize jobs when possible
   - Cache dependencies

2. **Fail fast**
   - Run fastest checks first (linting)
   - Stop on critical failures
   - Don't waste resources on broken code

3. **Make builds reproducible**
   - Pin dependency versions
   - Use same Python version as production
   - Consistent environment variables

4. **Test on every push**
   - No exceptions
   - Every branch
   - Every commit

5. **Provide clear feedback**
   - Descriptive error messages
   - Link to logs
   - Explain how to fix

6. **Secure your pipeline**
   - No secrets in code
   - Use environment variables
   - Rotate credentials regularly

### ❌ DON'T

1. **Don't skip CI**
   - Never bypass checks
   - Don't merge failing PRs
   - No "it works on my machine"

2. **Don't have flaky tests**
   - Fix unstable tests immediately
   - Don't ignore intermittent failures
   - Maintain test quality

3. **Don't hardcode secrets**
   - Use GitHub Secrets
   - Use environment variables
   - Never commit credentials

4. **Don't make builds too slow**
   - Keep under 10 minutes
   - Optimize test execution
   - Consider parallelization

---

## Environment Variables & Secrets

### GitHub Secrets

**Setup:**
1. Go to: Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add:
   - `DATABASE_URL`
   - `API_KEY`
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`

**Usage in Workflows:**
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

**Never do this:**
```python
# ❌ Bad
DATABASE_URL = "postgresql://user:pass@host:5432/db"

# ✅ Good
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## Deployment Stages

### 1. Development
- Every push to feature branches
- No deployment
- CI checks only

### 2. Staging
- Merges to `main`
- Auto-deploy to staging environment
- Test with production-like data
- Manual approval required for production

### 3. Production
- Manual trigger after staging approval
- Automated deployment
- Health checks
- Automatic rollback on failure

---

## Deployment Workflow Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Staging
        run: |
          # Deploy to staging server
          echo "Deploying to staging..."

      - name: Run Smoke Tests
        run: |
          # Test critical functionality
          pytest tests/smoke/

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Production
        run: |
          # Deploy to production
          echo "Deploying to production..."

      - name: Health Check
        run: |
          # Verify deployment
          curl https://api.beatthebooks.com/health
```

---

## Monitoring & Alerts

### After Deployment

**Monitor:**
- Application errors
- Response times
- Database connections
- CPU/Memory usage

**Alert on:**
- Deployment failures
- Test failures
- Security vulnerabilities
- Performance degradation

**Tools:**
- **Logs**: CloudWatch, Datadog, LogDNA
- **APM**: New Relic, Datadog APM
- **Alerts**: PagerDuty, Opsgenie
- **Uptime**: Pingdom, UptimeRobot

---

## Rollback Strategy

### Automatic Rollback

```yaml
- name: Deploy with Rollback
  run: |
    # Deploy new version
    ./deploy.sh

    # Wait for health check
    sleep 30

    # Check health
    if ! curl -f https://api.beatthebooks.com/health; then
      echo "Health check failed, rolling back..."
      ./rollback.sh
      exit 1
    fi
```

### Manual Rollback

```bash
# Rollback to previous version
git revert HEAD
git push origin main

# Or rollback to specific commit
git reset --hard abc123
git push origin main --force  # ⚠️ Requires admin
```

---

## CI/CD Metrics

Track these metrics to improve your pipeline:

- **Build Success Rate**: Target >95%
- **Build Time**: Target <10 minutes
- **Test Pass Rate**: Target >98%
- **Deployment Frequency**: Daily or more
- **Lead Time**: Target <1 day (commit to deploy)
- **Mean Time to Recovery (MTTR)**: Target <1 hour

---

## Troubleshooting CI/CD

### Build Failures

```bash
# Check logs
gh run view <run-id>

# Re-run failed jobs
gh run rerun <run-id>

# Download logs
gh run download <run-id>
```

### Common Issues

**Issue 1: Tests pass locally but fail in CI**
- Different Python versions
- Missing environment variables
- Database connection issues

**Fix:**
- Match local Python version to CI
- Check GitHub Secrets
- Use test database in CI

**Issue 2: Flaky tests**
- Timing issues
- Random data
- External dependencies

**Fix:**
- Use fixtures for consistent data
- Mock external services
- Add retries for flaky operations

**Issue 3: Slow builds**
- Too many tests
- No caching
- Sequential execution

**Fix:**
- Parallelize tests
- Cache dependencies
- Optimize slow tests

---

## CI/CD Checklist

Before merging to main:

- [ ] All CI checks pass
- [ ] Tests have good coverage
- [ ] No security vulnerabilities
- [ ] Code review approved
- [ ] Deployment plan ready
- [ ] Rollback strategy defined
- [ ] Monitoring configured
- [ ] Documentation updated

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CI/CD Best Practices](https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment)
- [pytest Documentation](https://docs.pytest.org/)

---

**Remember**: A good CI/CD pipeline catches bugs before users do! 🚀

**Last Updated**: February 2026
