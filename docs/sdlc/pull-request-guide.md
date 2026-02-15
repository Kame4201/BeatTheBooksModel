# Pull Request Guide

## Creating High-Quality Pull Requests

A good PR makes code review easier and speeds up the merge process.

---

## Before Creating a PR

### Checklist

- [ ] Code works locally
- [ ] Tests pass (`pytest`)
- [ ] Code follows project style (PEP 8)
- [ ] No console.log or debug statements
- [ ] No commented-out code
- [ ] Docstrings added/updated
- [ ] Type hints added
- [ ] Secrets removed
- [ ] Branch is up-to-date with main

```bash
# Run these before creating PR
pytest                                  # All tests pass
./venv/bin/python3 -m py_compile src/*  # No syntax errors
git diff main                           # Review your changes
```

---

## PR Template

### Title Format

```
<type>: <short description>
```

**Examples:**
- `feat: Add Excel URL scraper`
- `fix: Handle 403 errors from PFR`
- `test: Add integration tests for scraper`
- `docs: Update CLAUDE.md with SDLC`

### Description Template

```markdown
## Summary
Brief description of what this PR does (2-3 sentences).

## Changes
- Specific change 1
- Specific change 2
- Specific change 3

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Refactoring
- [ ] Test additions

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manually tested

**Test Results:**
```
pytest output here
```

## Screenshots (if applicable)
![image](url)

## Related Issues
Closes #14
Fixes #15
Related to #16

## Additional Notes
Any context reviewers should know.
```

---

## Example PR

### Good PR Example

```markdown
# Add Excel-based URL scraper

## Summary
Implements Excel-based URL scraping functionality that reads URLs from Excel files
and stores scraped data in the database with proper metadata tracking.

## Changes
- Created `excel_scraper_service.py` with scraping logic
- Added `ScrapedData` entity for metadata tracking
- Created `ScrapedDataRepository` with dynamic table creation
- Implemented `ScrapedDataMetadataCreate` DTO
- Added comprehensive unit tests (8 tests)
- Updated requirements.txt with openpyxl

## Type of Change
- [x] New feature
- [ ] Bug fix
- [x] Documentation
- [ ] Refactoring
- [x] Test additions

## Testing
- [x] Unit tests pass (8/8)
- [x] Integration test created
- [x] Manually tested with real Excel file

**Test Results:**
```
8 passed, 1 skipped in 6.84s
```

## Architecture
- Follows repository pattern
- Uses DTOs for data validation
- Proper separation of concerns (service/repository layers)
- Database operations abstracted in repository

## Performance
- 60-second delay between requests (configurable)
- Handles 403 errors gracefully
- Idempotent upserts (safe to re-run)

## Related Issues
Closes #14

## Additional Notes
Pro-Football-Reference may still block requests despite delays.
Consider using Selenium for production if 403 errors persist.
```

---

## PR Size Guidelines

### Optimal PR Size
- **Lines**: 200-400 lines changed
- **Files**: 5-10 files
- **Time to Review**: 15-30 minutes

### Too Large?
If your PR is >500 lines or >15 files:
- Consider breaking into smaller PRs
- Create a meta-issue tracking the feature
- Submit incremental changes

**Example breakdown:**
1. PR #1: Entity and DTO classes
2. PR #2: Repository layer
3. PR #3: Service layer
4. PR #4: API endpoints
5. PR #5: Tests

### Too Small?
- Single-line fixes are fine
- But don't create 10 PRs for 10 similar changes
- Group related changes together

---

## Code Review Process

### 1. Submit PR
```bash
gh pr create --title "feat: Add Excel scraper" --body "..."
```

### 2. Automated Checks
- CI/CD runs tests
- Code review agent analyzes changes
- Status checks must pass

### 3. Request Review
```bash
gh pr edit <number> --add-reviewer @teammate
```

### 4. Respond to Feedback

**Good responses:**
```
✅ "Fixed in commit abc123"
✅ "Refactored as suggested in commit def456"
✅ "Good catch! Updated the error handling"
✅ "I kept it as-is because [reason]. What do you think?"
```

**Bad responses:**
```
❌ "No" (no explanation)
❌ "Whatever" (dismissive)
❌ Ignoring comments
❌ Taking feedback personally
```

### 5. Make Updates
```bash
# Make changes based on feedback
git add .
git commit -m "Address review feedback: improve error handling"
git push origin feature/my-feature
# PR updates automatically
```

### 6. Resolve Conversations
- Mark conversations as resolved after addressing
- Don't resolve reviewer's conversations
- Leave a comment explaining your fix

### 7. Get Approval
- Wait for approving review
- Don't merge until approved
- Don't merge your own PRs (unless you're the only developer)

### 8. Merge
```bash
# After approval
gh pr merge <number> --squash --delete-branch
```

---

## Review Response Time

### For Reviewers
- **Urgent**: Same day
- **Normal**: Within 24 hours
- **Low Priority**: Within 48 hours

### For PR Authors
- **Review Feedback**: Respond within 24 hours
- **Requested Changes**: Fix within 2-3 days
- **Questions**: Answer promptly

---

## Common PR Issues

### Issue 1: Merge Conflicts

```bash
# Update your branch from main
git checkout main
git pull origin main
git checkout feature/my-feature
git merge main

# Resolve conflicts
# Edit conflicted files
git add <resolved-files>
git commit -m "Resolve merge conflicts"
git push origin feature/my-feature
```

### Issue 2: Failed Tests

```bash
# Run tests locally
pytest -v

# Fix failing tests
# Commit fixes
git add tests/
git commit -m "Fix failing tests"
git push origin feature/my-feature
```

### Issue 3: Outdated Branch

```bash
# GitHub will show "This branch is out-of-date"
git checkout main
git pull origin main
git checkout feature/my-feature
git merge main
git push origin feature/my-feature
```

---

## PR Best Practices

### ✅ DO
- Keep PRs focused (one feature/fix per PR)
- Write clear descriptions
- Include tests
- Update documentation
- Respond to reviews quickly
- Use draft PRs for work-in-progress
- Link related issues
- Add screenshots for UI changes
- Self-review before requesting review

### ❌ DON'T
- Mix multiple features in one PR
- Submit untested code
- Ignore CI failures
- Merge your own PRs without approval
- Force push after review starts
- Create PR without description
- Leave PRs open for weeks
- Get defensive about feedback

---

## Draft PRs

Use drafts for:
- Work in progress
- Seeking early feedback
- Complex features
- Collaborative development

```bash
# Create draft PR
gh pr create --draft

# Mark as ready for review
gh pr ready
```

---

## Emergency Hotfixes

For critical production bugs:

```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue

# Fix the issue
git add .
git commit -m "hotfix: fix critical database connection issue"

# Fast-track review
git push origin hotfix/critical-issue
gh pr create --title "HOTFIX: Critical database issue" \
             --body "Urgent fix for production" \
             --label hotfix

# Request immediate review
gh pr edit <number> --add-reviewer @lead
```

---

## Tools & Tips

### GitHub CLI

```bash
# View PR in browser
gh pr view --web

# View PR status
gh pr status

# Check PR checks
gh pr checks

# Approve PR
gh pr review --approve

# Request changes
gh pr review --request-changes

# Checkout PR locally
gh pr checkout <number>
```

### Useful Git Commands

```bash
# View changes before committing
git diff

# View staged changes
git diff --staged

# Interactive staging
git add -p

# Amend last commit
git commit --amend

# View PR diff
git diff main...feature/branch
```

---

## Review Checklist for Authors

Before requesting review:

- [ ] Self-reviewed all changes
- [ ] No debug code or console.log
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] Type hints added
- [ ] Docstrings written
- [ ] Error handling in place
- [ ] Code follows project patterns
- [ ] PR description complete

---

## When Your PR is Stuck

1. **No response from reviewer?**
   - Ping them in PR comments
   - Tag them: "@reviewer could you review?"
   - After 48 hours, request another reviewer

2. **Disagreement with feedback?**
   - Explain your reasoning
   - Suggest alternatives
   - Have a discussion
   - Escalate to team lead if needed

3. **Too many changes requested?**
   - Ask which are blocking vs nice-to-have
   - Create follow-up issues for non-critical items
   - Focus on getting core functionality merged

---

## PR Metrics to Track

- **Time to First Review**: Target < 24 hours
- **Time to Merge**: Target < 3 days
- **Changes Requested**: Target < 2 rounds
- **PR Size**: Target 200-400 lines

---

## Resources

- [GitHub PR Docs](https://docs.github.com/en/pull-requests)
- [Google's Code Review Guide](https://google.github.io/eng-practices/review/)
- [Project Code Review Guidelines](code-review.md)

---

**Remember**: Good PRs lead to better code and faster reviews! 🚀

**Last Updated**: February 2026
