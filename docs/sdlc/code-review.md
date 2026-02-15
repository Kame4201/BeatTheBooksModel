# Code Review Guidelines

## Purpose of Code Review

Code reviews ensure:
- **Quality**: Code meets project standards
- **Knowledge Sharing**: Team learns from each other
- **Bug Prevention**: Catch issues before they reach production
- **Consistency**: Maintain consistent patterns across codebase

---

## For Reviewers

### Review Checklist

#### 1. Functionality
- [ ] Does the code solve the stated problem?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?
- [ ] Does it follow the project architecture?

#### 2. Code Quality
- [ ] Is the code readable and maintainable?
- [ ] Are variable/function names clear and descriptive?
- [ ] Is the code DRY (Don't Repeat Yourself)?
- [ ] Are functions small and focused?
- [ ] Is complexity reasonable?

#### 3. Architecture & Design
- [ ] Follows repository pattern?
- [ ] Proper separation of concerns (service/repo/entity/dto)?
- [ ] DTOs used for data validation?
- [ ] No direct SQL in service layer?
- [ ] Consistent with existing patterns?

#### 4. Testing
- [ ] Are there tests?
- [ ] Do tests cover edge cases?
- [ ] Are tests readable and maintainable?
- [ ] Do all tests pass?

#### 5. Documentation
- [ ] Are docstrings present?
- [ ] Are type hints provided?
- [ ] Is README updated if needed?
- [ ] Are comments clear and necessary?

#### 6. Security
- [ ] No hardcoded credentials or secrets?
- [ ] Input validation present?
- [ ] SQL injection prevented?
- [ ] No security vulnerabilities?

#### 7. Performance
- [ ] No obvious performance issues?
- [ ] Database queries optimized?
- [ ] Rate limiting where appropriate?
- [ ] No unnecessary computations?

#### 8. Style
- [ ] Follows PEP 8?
- [ ] Consistent formatting?
- [ ] No debug code (print, console.log)?
- [ ] No commented-out code?

---

## Review Process

### 1. Initial Review (5-10 minutes)

```bash
# Checkout the PR branch
gh pr checkout <pr-number>

# Review the changes
gh pr diff <pr-number>

# Check what tests exist
pytest --collect-only

# Run tests
pytest -v
```

**Quick Assessment:**
- PR size appropriate? (200-400 lines ideal)
- Description clear?
- Tests included?
- CI checks passing?

### 2. Deep Review (15-30 minutes)

Read through code carefully:
1. Understand the problem being solved
2. Review the approach
3. Check implementation details
4. Verify tests
5. Consider edge cases

### 3. Provide Feedback

Use GitHub's review features:
- **Approve**: Code is good to merge
- **Request Changes**: Issues must be fixed
- **Comment**: Non-blocking suggestions

---

## Providing Feedback

### Comment Types

#### 🛑 Blocking Issues (Must Fix)
```markdown
**[BLOCKING]** This SQL query is vulnerable to injection.

Use parameterized queries instead:
```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
query = "SELECT * FROM users WHERE id = :user_id"
db.execute(query, {"user_id": user_id})
```

#### 💡 Suggestions (Nice to Have)
```markdown
**[Suggestion]** Consider extracting this into a helper function for reusability.

```python
def validate_url(url: str) -> bool:
    """Validate URL format."""
    return url.startswith('http') and '://' in url
```
This would make the code more maintainable.
```

#### ❓ Questions (Seeking Clarification)
```markdown
**[Question]** Why are we using a 60-second delay here?

Is this based on the API rate limit, or can we use a shorter delay?
```

#### ✅ Praise (Acknowledge Good Work)
```markdown
**[Nice]** Great use of the repository pattern here! This makes the code much more testable.
```

---

## Feedback Best Practices

### ✅ DO

**Be Specific**
```
❌ "This is confusing"
✅ "The variable name `x` is unclear. Consider renaming to `user_count` to clarify its purpose."
```

**Be Constructive**
```
❌ "This code is terrible"
✅ "This function is doing too much. Consider breaking it into smaller functions, each with a single responsibility."
```

**Provide Examples**
```
✅ "Consider using a dict comprehension here:
```python
# Instead of
result = {}
for item in items:
    result[item.id] = item.name

# Use
result = {item.id: item.name for item in items}
```
```

**Ask Questions**
```
✅ "What happens if the URL is invalid? Should we raise an exception or return None?"
```

**Acknowledge Good Work**
```
✅ "Great error handling here! I like how you're logging the details."
```

### ❌ DON'T

**Be Vague**
```
❌ "Fix this"
❌ "This doesn't work"
❌ "Bad code"
```

**Be Rude or Personal**
```
❌ "You clearly don't understand Python"
❌ "Did you even test this?"
❌ "This is the worst code I've seen"
```

**Nitpick Excessively**
```
❌ "This line has an extra space"
❌ "Use single quotes instead of double quotes" (unless it's a project standard)
```

**Make Assumptions**
```
❌ "You forgot to add tests" (maybe they're in a different PR)
✅ "Are tests coming in a follow-up PR, or should they be included here?"
```

---

## Common Review Patterns

### 1. Architectural Review

```markdown
## Architecture Feedback

**Current Structure:**
```python
# service layer calling database directly
def scrape_url(url):
    db.execute("INSERT INTO data VALUES ...")
```

**Suggested Structure:**
```python
# service layer
def scrape_url(url):
    data = fetch_data(url)
    repo.save(data)

# repository layer
class DataRepository:
    def save(self, data):
        self.db.execute("INSERT INTO data VALUES ...")
```

This follows our repository pattern and makes the code more testable.
```

### 2. Security Review

```markdown
## Security Concern

**[BLOCKING]** Potential SQL injection vulnerability at line 42.

**Current code:**
```python
query = f"SELECT * FROM users WHERE name = '{user_name}'"
```

**Fix:**
```python
query = "SELECT * FROM users WHERE name = :name"
result = db.execute(query, {"name": user_name})
```

Always use parameterized queries to prevent SQL injection.
```

### 3. Performance Review

```markdown
## Performance Concern

**[Suggestion]** This loop makes N database queries (N+1 problem).

**Current:**
```python
for user in users:
    orders = db.query(Order).filter_by(user_id=user.id).all()
```

**Better:**
```python
# Single query with join
users_with_orders = db.query(User).options(
    joinedload(User.orders)
).all()
```

This reduces database round trips from N+1 to 1.
```

### 4. Testing Review

```markdown
## Testing Feedback

Great test coverage! A few suggestions:

1. **Add edge case test:**
```python
def test_scrape_with_invalid_url():
    """Test that invalid URLs raise appropriate error."""
    with pytest.raises(ValueError):
        scrape_url("not-a-valid-url")
```

2. **Test the error path:**
```python
def test_scrape_with_403_error():
    """Test handling of 403 Forbidden response."""
    # Mock the response
    # Assert appropriate error handling
```
```

---

## Review Response Time

- **Small PRs (<100 lines)**: Same day
- **Medium PRs (100-400 lines)**: Within 24 hours
- **Large PRs (400+ lines)**: Within 48 hours
- **Urgent/Hotfix PRs**: Within 2 hours

If you can't review in time:
- Comment on the PR: "I'll review this by [date]"
- Suggest an alternative reviewer

---

## For Authors: Responding to Reviews

### Addressing Feedback

**Acknowledge all comments:**
```markdown
✅ "Fixed in commit abc123"
✅ "Good point! I've refactored this to use a helper function"
✅ "Added the suggested test case"
✅ "I kept it as-is because [reason]. Happy to discuss further."
```

**Don't:**
```markdown
❌ "No" (no explanation)
❌ Ignoring comments
❌ Getting defensive
```

### Pushing Updates

```bash
# Make requested changes
git add .
git commit -m "Address review feedback

- Refactor scraping logic into helper function
- Add edge case tests
- Fix SQL injection vulnerability
- Update docstrings"

git push origin feature/branch-name
# PR updates automatically
```

### Resolving Conversations

- Fix the issue first
- Comment with the fix
- Let the reviewer resolve the conversation
- Only resolve your own clarification questions

---

## Handling Disagreements

### When You Disagree with Feedback

1. **Understand the concern**
   - Ask clarifying questions
   - Understand the reviewer's perspective

2. **Explain your reasoning**
   ```markdown
   I see your concern about performance. However, I chose this approach because:
   - The dataset is small (<100 items)
   - Readability is more important here
   - Profiling shows no bottleneck

   Would you like me to add a comment explaining this tradeoff?
   ```

3. **Propose alternatives**
   ```markdown
   Option 1: Use the approach you suggested
   Option 2: Keep current approach but add documentation
   Option 3: Create a follow-up issue to revisit if it becomes a problem

   What do you think?
   ```

4. **Escalate if needed**
   - If you can't reach agreement, bring in a third party
   - Tag the team lead or another senior developer
   - Focus on the code, not personalities

---

## Code Review Anti-Patterns

### ❌ The Rubber Stamp
- Approving without reading the code
- "LGTM" without any comments
- Not running tests

**Instead:** Take time to review properly

### ❌ The Nitpicker
- Focusing only on style issues
- Ignoring automated linting
- Hundreds of minor comments

**Instead:** Use linters, focus on logic and architecture

### ❌ The Redesigner
- Suggesting complete rewrites
- Imposing personal preferences
- Rejecting valid approaches

**Instead:** Accept different valid solutions

### ❌ The Ghost
- Requesting review then disappearing
- Not responding to questions
- Delaying reviews indefinitely

**Instead:** Review promptly or decline the request

### ❌ The Blocker
- Blocking on non-issues
- Refusing to approve good code
- Moving goalposts

**Instead:** Distinguish blocking vs. nice-to-have feedback

---

## Self-Review Checklist

Before requesting review, authors should:

- [ ] Read through your own PR on GitHub
- [ ] Remove debug code and commented-out code
- [ ] Verify tests pass locally
- [ ] Check that docstrings and type hints are present
- [ ] Ensure commit messages are clear
- [ ] Confirm no secrets are committed
- [ ] Test the functionality manually
- [ ] Add screenshots for UI changes
- [ ] Write a clear PR description

**Self-review saves time for everyone!**

---

## Automated Review Tools

### Linting (Automated)
```bash
# Python linting
flake8 src/
pylint src/

# Auto-formatting
black src/
autopep8 --in-place src/
```

### Type Checking (Automated)
```bash
mypy src/
```

### Security Scanning (Automated)
```bash
bandit -r src/
safety check
```

### Test Coverage (Automated)
```bash
pytest --cov=src tests/
```

**Use automated tools to catch style and basic issues, so reviewers can focus on logic and architecture.**

---

## Example Reviews

### Good Review Example

```markdown
## Summary
This PR adds Excel URL scraping functionality. Overall looks great!
I have a few suggestions and one blocking security issue.

## Blocking Issues

### 1. SQL Injection Vulnerability (line 89)
**[BLOCKING]** The dynamic table creation is vulnerable to SQL injection.

**Current:**
```python
query = f"CREATE TABLE {table_name} ..."
```

**Fix:**
```python
# Validate table_name against whitelist
if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
    raise ValueError(f"Invalid table name: {table_name}")
```

## Suggestions

### 2. Error Handling (line 142)
Consider adding more specific exception handling:
```python
try:
    df = pd.read_excel(path)
except FileNotFoundError:
    logger.error(f"Excel file not found: {path}")
    raise
except Exception as e:
    logger.error(f"Failed to read Excel: {e}")
    raise
```

### 3. Rate Limiting (line 200)
The 60-second delay is hardcoded. Consider making it configurable:
```python
SCRAPE_DELAY_SECONDS = int(os.getenv('SCRAPE_DELAY', '60'))
```

## Nice!

Line 156: Great use of the repository pattern! This makes testing much easier.

Line 234: Good defensive programming with the URL validation.

## Questions

1. Have you tested this with very large Excel files (>1000 rows)?
2. What happens if the website returns a 403 after the delay?

## Tests

Test coverage looks good! Consider adding:
- Test for large Excel files
- Test for 403 error handling

## Verdict

Please fix the SQL injection issue (blocking), then I'll approve.
The suggestions are non-blocking but would improve the code.
```

---

## Review Metrics

Track these to improve the review process:
- **Average time to first review**: Target <24 hours
- **Average time to approval**: Target <3 days
- **Review comments per PR**: Target 3-8 comments
- **Changes requested rounds**: Target <2 rounds

---

## Resources

- [Google's Code Review Guide](https://google.github.io/eng-practices/review/)
- [Conventional Comments](https://conventionalcomments.org/)
- [Pull Request Guide](pull-request-guide.md)
- [Git Workflow](git-workflow.md)

---

**Remember**: The goal is to improve the code and help each other grow, not to be perfect. Good reviews make good code! 🎯

**Last Updated**: February 2026
