# Git Workflow - BeatTheBooksModel

## ⚠️ Golden Rule

**NEVER commit directly to the `main` branch.**

All changes must go through a Pull Request with code review.

---

## Branch Strategy (GitFlow)

### Branch Types

```
main (protected)
├── feature/excel-scraper     ✅ New features
├── bugfix/fix-403-errors     ✅ Bug fixes
├── hotfix/critical-fix       ✅ Urgent production fixes
└── docs/update-readme        ✅ Documentation updates
```

### Branch Naming Convention

```bash
feature/<short-description>    # New features
bugfix/<issue-number>-<description>  # Bug fixes
hotfix/<critical-issue>        # Urgent fixes
docs/<what-docs>               # Documentation
test/<test-description>        # Test additions
refactor/<what-refactor>       # Code refactoring
```

**Examples:**
- `feature/excel-url-scraper`
- `bugfix/14-fix-403-errors`
- `hotfix/database-connection`
- `docs/update-claude-md`
- `test/add-integration-tests`

---

## Standard Workflow

### 1. Start New Work

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Verify you're on the right branch
git branch
# * feature/my-feature
#   main
```

### 2. Make Changes

```bash
# Make your changes
# Edit files, add features, fix bugs

# Check what changed
git status
git diff

# Stage changes
git add <specific-files>
# OR
git add .  # Be careful with this - review what you're staging

# Commit with meaningful message
git commit -m "Add Excel URL scraper functionality

- Created excel_scraper_service.py
- Added repository layer for scraped data
- Created DTOs and entities
- Added tests

Closes #14"
```

### 3. Push to Remote

```bash
# Push feature branch to GitHub
git push origin feature/my-feature

# If this is the first push
git push -u origin feature/my-feature
```

### 4. Create Pull Request

```bash
# Using GitHub CLI (recommended)
gh pr create \
  --title "Add Excel URL scraper" \
  --body "Implements Excel-based URL scraping

## Changes
- New service for Excel scraping
- Repository pattern for data access
- Dynamic table creation
- Comprehensive tests

## Testing
- Unit tests pass
- Integration test successful
- Tested with real Excel file

Closes #14"

# OR open GitHub and create PR manually
```

### 5. Code Review

- Wait for automated checks to pass
- Request review from team member
- Address review feedback
- Push additional commits if needed

```bash
# Make requested changes
git add .
git commit -m "Address review feedback: refactor error handling"
git push origin feature/my-feature
# PR automatically updates
```

### 6. Merge

**After approval:**

```bash
# Option 1: Merge via GitHub UI (recommended)
# Click "Merge pull request" button

# Option 2: Merge via CLI with admin privileges
gh pr merge <pr-number> --squash --delete-branch

# Update your local main
git checkout main
git pull origin main

# Delete local feature branch
git branch -d feature/my-feature
```

---

## Commit Message Guidelines

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `style`: Formatting changes
- `chore`: Maintenance tasks

### Examples

**Good commits:**
```bash
git commit -m "feat: add Excel URL scraper

Implements Excel-based URL scraping with:
- Service layer for business logic
- Repository pattern for data access
- Dynamic table creation
- Comprehensive error handling

Closes #14"
```

```bash
git commit -m "fix: handle 403 errors from Pro-Football-Reference

Added 60-second delay between requests and enhanced
HTTP headers to reduce bot detection.

Fixes #15"
```

```bash
git commit -m "test: add unit tests for Excel scraper

Added comprehensive test suite covering:
- Excel file reading
- URL validation
- Metadata columns
- Error handling

8 tests, all passing."
```

**Bad commits:**
```bash
git commit -m "fixed stuff"           # Too vague
git commit -m "WIP"                   # Not descriptive
git commit -m "asdfasdf"              # Meaningless
git commit -m "commit"                # No information
```

---

## Common Scenarios

### Scenario 1: Staying Updated

```bash
# While working on feature branch, main gets updated
git checkout main
git pull origin main

git checkout feature/my-feature
git merge main
# OR
git rebase main

# Resolve conflicts if any
git push origin feature/my-feature
```

### Scenario 2: Switching Branches

```bash
# Save current work
git add .
git commit -m "WIP: saving progress"

# OR use stash
git stash

# Switch branches
git checkout other-branch

# Come back and restore
git checkout feature/my-feature
git stash pop  # if you used stash
```

### Scenario 3: Fixing Mistakes

```bash
# Undo last commit (keep changes)
git reset HEAD~1

# Undo last commit (discard changes) ⚠️ DANGEROUS
git reset --hard HEAD~1

# Amend last commit (if not pushed yet)
git add forgotten-file.py
git commit --amend --no-edit

# Undo changes to specific file
git checkout -- file.py

# Fix a mistake after pushing
# DON'T use git push --force on main
# Instead: create new commit that fixes it
git revert <commit-hash>
git push origin feature/my-feature
```

### Scenario 4: Accidental Commit to Main

**If you accidentally committed to main (but haven't pushed):**

```bash
# Create a feature branch with your changes
git branch feature/my-changes

# Reset main to origin
git reset --hard origin/main

# Switch to feature branch
git checkout feature/my-changes

# Push and create PR
git push -u origin feature/my-changes
gh pr create
```

**If you already pushed to main:**
1. Contact repository admin immediately
2. They may need to revert or fix
3. Learn from mistake - always check branch before committing

---

## Branch Protection Rules

The `main` branch should have these protections:

- ✅ Require pull request before merging
- ✅ Require approvals (at least 1)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require conversation resolution
- ❌ Allow force pushes (disabled)
- ❌ Allow deletions (disabled)

---

## Quick Reference

```bash
# Start new feature
git checkout -b feature/name

# Save work
git add .
git commit -m "message"

# Push changes
git push origin feature/name

# Create PR
gh pr create

# Update from main
git checkout main
git pull
git checkout feature/name
git merge main

# Clean up after merge
git checkout main
git pull
git branch -d feature/name
```

---

## Tools

### GitHub CLI (`gh`)
```bash
# Install: https://cli.github.com/

# Create PR
gh pr create

# View PR
gh pr view

# List PRs
gh pr list

# Merge PR
gh pr merge <number>

# View checks
gh pr checks
```

### Helpful Git Aliases

Add to `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    pl = pull
    ps = push
    lg = log --oneline --graph --decorate --all
    unstage = reset HEAD --
```

---

## Best Practices

### ✅ DO
- Create descriptive branch names
- Write meaningful commit messages
- Keep commits focused and atomic
- Test before pushing
- Review your own PR first
- Respond to review feedback promptly
- Delete branches after merging

### ❌ DON'T
- Commit directly to main
- Force push to main
- Commit secrets or credentials
- Make huge commits with unrelated changes
- Ignore review feedback
- Merge your own PRs without approval
- Leave feature branches open forever

---

## Need Help?

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Docs**: https://docs.github.com
- **Team Lead**: Open an issue for questions

---

**Remember**: When in doubt, create a branch! 🌿

**Last Updated**: February 2026
