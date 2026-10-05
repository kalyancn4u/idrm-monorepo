# IDRM v3 · Contributing

<!-- IDRM-CLEANUP doc=v3-g30-contribute status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — contributing → current
> → [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> + [`git-github-101`](../../../../guides/mvp/learn/git-github-101.md) + Definition of Done. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: Contributors · Status: Archived — v3 historical generation*
*Consolidated from: 50-CONTRIBUTION-GUIDE.md, contributor-guide-v3.md*

## Contents
- [IDRM: Contribution Guide](#idrm-contribution-guide)
- [IDRM MVP: Contributor Guide v3.0](#idrm-mvp-contributor-guide-v30)

---

## IDRM: Contribution Guide

### How to Contribute to IDRM - The Complete Guide for Beginners

**Version**: 3.0  
**Audience**: Anyone who wants to contribute  
**Reading Time**: 2-3 hours  
**Last Updated**: May 16, 2026

---

### 🎯 **What This Guide Covers**

Welcome to the IDRM project! This guide will teach you **everything** you need to know to contribute, even if you've never contributed to open source before.

**You'll learn**:
- ✅ How open-source contribution works
- ✅ How to set up your development environment
- ✅ Git and GitHub workflows
- ✅ Coding standards and best practices
- ✅ How to submit your first contribution
- ✅ Code review process
- ✅ Community guidelines

**Prerequisites**: Basic knowledge of Git and programming

---

### 📚 **Table of Contents**

1. [Welcome to IDRM](#1-welcome-to-idrm)
2. [Ways to Contribute](#2-ways-to-contribute)
3. [Getting Started](#3-getting-started)
4. [Development Workflow](#4-development-workflow)
5. [Coding Standards](#5-coding-standards)
6. [Submitting Changes](#6-submitting-changes)
7. [Code Review Process](#7-code-review-process)
8. [Community Guidelines](#8-community-guidelines)
9. [Getting Help](#9-getting-help)

---

## 1. **Welcome to IDRM**

### 1.1 What is IDRM?

**IDRM** = Integrated Disaster Response Management

A platform that connects people who need help during disasters with organizations that can provide it - all on an interactive map.

**Our Mission**: Save lives by making disaster response faster, more efficient, and transparent.

---

### 1.2 Why Contribute?

**Make a Real Impact**:
```
Your code will:
✅ Help people during disasters
✅ Save lives in emergencies
✅ Make government services more accessible
✅ Build your portfolio
✅ Learn real-world development
```

**Learn & Grow**:
```
✅ Work with modern technologies
✅ Learn from experienced developers
✅ Get code review feedback
✅ Build production skills
✅ Network with the community
```

---

### 1.3 Code of Conduct

**Be Respectful**:
- ✅ Welcome and inclusive to everyone
- ✅ Patient with beginners
- ✅ Constructive in feedback
- ❌ No harassment or discrimination
- ❌ No trolling or spam

**We Value**:
- Collaboration over competition
- Questions over silence
- Learning over perfection
- Kindness over cleverness

---

## 2. **Ways to Contribute**

### 2.1 Code Contributions

**Backend** (Python):
- API endpoints
- Database models
- Geospatial queries
- Authentication logic
- Testing

**Frontend** (HTML/JavaScript):
- User interfaces
- Map interactions
- Forms and validation
- Responsive design
- Accessibility

**DevOps**:
- Docker configurations
- CI/CD pipelines
- Deployment scripts
- Monitoring setup

---

### 2.2 Non-Code Contributions

**Documentation**:
- Tutorial writing
- API documentation
- User guides
- Video tutorials
- Translations

**Design**:
- UI/UX improvements
- Icons and graphics
- Mockups
- Accessibility audit

**Testing**:
- Bug reports
- Feature testing
- Usability testing
- Performance testing

**Community**:
- Answer questions
- Help newcomers
- Organize events
- Spread the word

---

## 3. **Getting Started**

### 3.1 Prerequisites

**Required Knowledge**:
```
Basic:
- Git basics (clone, commit, push, pull)
- Terminal/Command line
- Text editor (VS Code recommended)

For Backend:
- Python basics
- Understanding of APIs
- SQL basics

For Frontend:
- HTML/CSS basics
- JavaScript basics
- DOM manipulation
```

**Don't know these yet?** No problem!
- Read our [Development Guide](49-IDRM-COMPLETE-DEVELOPMENT-GUIDE.md)
- Take online courses (freeCodeCamp, Codecademy)
- Ask for help in our Discord

---

### 3.2 Setup Your Development Environment

#### Step 1: Fork the Repository

```
1. Go to https://github.com/idrm-platform/idrm
2. Click "Fork" button (top right)
3. This creates your own copy of the repository
```

#### Step 2: Clone Your Fork

```bash
## Clone your fork (not the original!)
git clone https://github.com/YOUR-USERNAME/idrm.git

## Navigate to directory
cd idrm

## Add upstream remote (original repository)
git remote add upstream https://github.com/idrm-platform/idrm.git

## Verify remotes
git remote -v
## Should show:
## origin    https://github.com/YOUR-USERNAME/idrm.git (fetch)
## origin    https://github.com/YOUR-USERNAME/idrm.git (push)
## upstream  https://github.com/idrm-platform/idrm.git (fetch)
## upstream  https://github.com/idrm-platform/idrm.git (push)
```

#### Step 3: Install Dependencies

**Backend Setup**:
```bash
cd backend

## Create virtual environment
python3.11 -m venv venv

## Activate it
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

## Install dependencies
pip install -r requirements.txt
```

**Database Setup**:
```bash
## Create database (PostgreSQL)
sudo -u postgres psql

postgres=# CREATE DATABASE idrm_dev;
postgres=# CREATE USER idrm_user WITH PASSWORD 'dev_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE idrm_dev TO idrm_user;
postgres=# \c idrm_dev
idrm_dev=# CREATE EXTENSION postgis;
idrm_dev=# \q
```

**Run Migrations**:
```bash
## Apply database migrations
alembic upgrade head
```

**Start Development Server**:
```bash
## Backend
uvicorn main:app --reload --port 8000

## Frontend (in another terminal)
cd ../frontend
python3 -m http.server 3000
```

**Verify Setup**:
```bash
## Backend health check
curl http://localhost:8000/api/v1/health

## Frontend
## Open http://localhost:3000 in browser
```

---

## 4. **Development Workflow**

### 4.1 Finding an Issue to Work On

**Check Issue Tracker**:
```
1. Go to https://github.com/idrm-platform/idrm/issues
2. Filter by labels:
   - "good first issue" (for beginners)
   - "help wanted" (need contributors)
   - "bug" (bug fixes)
   - "enhancement" (new features)
   - "documentation" (docs)
```

**Choose Wisely**:
```
Good First Issues:
✅ Clearly defined
✅ Limited scope
✅ Good documentation
✅ Mentor available

Avoid for First Contribution:
❌ Large refactoring
❌ Breaking changes
❌ Complex algorithms
❌ No clear requirements
```

**Claim the Issue**:
```
1. Comment on the issue: "I'd like to work on this"
2. Wait for maintainer confirmation
3. Ask questions if anything unclear
```

---

### 4.2 Git Workflow

#### Create Feature Branch

```bash
## Make sure you're on main
git checkout main

## Get latest changes from upstream
git fetch upstream
git merge upstream/main

## Create feature branch (descriptive name!)
git checkout -b feature/add-email-notifications
## OR
git checkout -b fix/login-redirect-bug
## OR
git checkout -b docs/update-api-reference
```

**Branch Naming Convention**:
```
feature/  → New feature
fix/      → Bug fix
docs/     → Documentation
refactor/ → Code refactoring
test/     → Adding tests
chore/    → Maintenance (deps, config)

Examples:
✅ feature/add-service-filtering
✅ fix/map-marker-positioning
✅ docs/update-deployment-guide
❌ my-changes
❌ updates
❌ fix
```

---

#### Make Your Changes

**Write Code**:
```python
## Example: Adding a new API endpoint

## File: backend/app/api/services.py

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.service import ServiceCreate, ServiceResponse

router = APIRouter()

@router.post("/services", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    current_user = Depends(get_current_user)
):
    """
    Create a new service request.
    
    - **service_type**: Type of service (MEDICAL, FOOD, etc.)
    - **priority**: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
    - **location**: GeoJSON point with coordinates
    - **description**: Detailed description
    """
    # Validate location
    if not is_valid_coordinates(service.location):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    # Create service in database
    db_service = create_service_in_db(service, current_user.id)
    
    return db_service
```

**Follow Coding Standards** (see [Section 5](#5-coding-standards))

---

#### Commit Your Changes

**Commit Often**:
```bash
## Stage changes
git add file1.py file2.py

## Or stage all
git add .

## Commit with descriptive message
git commit -m "feat: add email notification on service creation"
```

**Commit Message Format**:
```
<type>: <short description>

[optional body]

[optional footer]

Types:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation
- style:    Formatting, no code change
- refactor: Code restructuring
- test:     Adding tests
- chore:    Maintenance

Examples:
✅ feat: add filtering to service list
✅ fix: resolve login redirect issue on mobile
✅ docs: update API reference for auth endpoints
✅ test: add unit tests for geospatial queries

❌ updated files
❌ changes
❌ stuff
```

**Good Commit Messages**:
```bash
## Good
git commit -m "feat: add email notification on service creation

- Add EmailService class
- Create notification templates
- Send email when service created
- Add tests for email sending

Closes #123"

## Also Good (simple fix)
git commit -m "fix: correct typo in login error message"

## Bad
git commit -m "changes"
git commit -m "update"
git commit -m "stuff I did"
```

---

#### Test Your Changes

**Run Tests**:
```bash
## Backend tests
cd backend
pytest

## With coverage
pytest --cov=app --cov-report=html

## Specific test file
pytest tests/test_services.py

## Specific test
pytest tests/test_services.py::test_create_service
```

**Manual Testing**:
```
1. Test the feature/fix yourself
2. Test edge cases
3. Test on different browsers (if frontend)
4. Verify no existing features broken
```

---

#### Push Your Changes

```bash
## Push to your fork
git push origin feature/add-email-notifications

## If first time pushing this branch
git push -u origin feature/add-email-notifications
```

---

### 4.3 Keep Your Fork Updated

**Regularly sync with upstream**:

```bash
## Fetch latest from upstream
git fetch upstream

## Merge into your main branch
git checkout main
git merge upstream/main

## Push to your fork
git push origin main

## Update your feature branch
git checkout feature/add-email-notifications
git rebase main
```

**If there are conflicts**:
```bash
## During rebase, fix conflicts
## Edit conflicting files
## Then:
git add .
git rebase --continue

## Or abort if needed
git rebase --abort
```

---

## 5. **Coding Standards**

### 5.1 Python (Backend)

**For complete standards**, see **41-CODE-STANDARDS.md**

**Quick Reference**:

```python
## File structure
from fastapi import APIRouter, Depends
from typing import List, Optional
import logging

## Constants at top
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

## Logging
logger = logging.getLogger(__name__)

## Type hints always
def get_service(service_id: str) -> Optional[Service]:
    """Get service by ID.
    
    Args:
        service_id: Unique service identifier
        
    Returns:
        Service object or None if not found
    """
    pass

## Use Pydantic for validation
class ServiceCreate(BaseModel):
    service_type: ServiceType
    priority: Priority
    location: GeoJSONPoint
    description: str = Field(..., min_length=10, max_length=2000)

## Error handling
try:
    service = get_service(service_id)
except ValueError as e:
    logger.error(f"Invalid service ID: {service_id}")
    raise HTTPException(status_code=400, detail=str(e))
```

**Formatting**:
```bash
## Use Black for formatting
black app/

## Use isort for imports
isort app/

## Use flake8 for linting
flake8 app/ --max-line-length=120
```

---

### 5.2 JavaScript (Frontend)

**Quick Reference**:

```javascript
// Use const/let, not var
const API_URL = '/api/v1';
let currentUser = null;

// Async/await for promises
async function login(email, password) {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, {
      email,
      password
    });
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
}

// Use template literals
const message = `Welcome, ${user.name}!`;

// Destructuring
const { email, full_name } = user;

// Arrow functions
const users = response.data.map(user => user.name);

// Error handling
try {
  await fetchData();
} catch (error) {
  showError(error.message);
}
```

**Comments**:
```javascript
/**
 * Create a new service request
 * @param {Object} data - Service request data
 * @param {string} data.service_type - Type of service
 * @param {string} data.priority - Priority level
 * @returns {Promise<Object>} Created service
 */
async function createService(data) {
  // Implementation
}
```

---

### 5.3 HTML/CSS

**HTML**:
```html
<!-- Semantic HTML -->
<header>
  <nav>
    <a href="/">Home</a>
  </nav>
</header>

<main>
  <section>
    <h1>Page Title</h1>
    <p>Content</p>
  </section>
</main>

<footer>
  <p>&copy; 2026 IDRM</p>
</footer>

<!-- Accessibility -->
<button aria-label="Close dialog">×</button>
<img src="map.png" alt="Service request map">
<label for="email">Email:</label>
<input id="email" type="email" required>
```

**Tailwind CSS**:
```html
<!-- Use utility classes -->
<div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h2 class="text-2xl font-bold mb-4">Title</h2>
  <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
    Click me
  </button>
</div>

<!-- Responsive design -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Content -->
</div>
```

---

### 5.4 SQL

**For complete query reference**, see **45-DATABASE-QUERY-REFERENCE.md**

**Quick Reference**:
```sql
-- Use meaningful names
SELECT 
    sr.service_id,
    sr.service_type,
    u.full_name AS requestor_name,
    ST_AsGeoJSON(sr.location) AS location_geojson
FROM service_requests sr
INNER JOIN users u ON sr.requestor_id = u.user_id
WHERE sr.status = 'SUBMITTED'
  AND sr.priority = 'CRITICAL'
ORDER BY sr.created_at DESC
LIMIT 20;

-- Use prepared statements (prevents SQL injection)
-- In Python:
cursor.execute(
    "SELECT * FROM service_requests WHERE service_id = %s",
    (service_id,)
)

-- Indexes for performance
CREATE INDEX CONCURRENTLY idx_services_status 
ON service_requests(status);

CREATE INDEX CONCURRENTLY idx_services_location 
ON service_requests USING GIST(location);
```

---

## 6. **Submitting Changes**

### 6.1 Create Pull Request

**Step 1: Push Your Branch**
```bash
git push origin feature/add-email-notifications
```

**Step 2: Open Pull Request**
```
1. Go to https://github.com/YOUR-USERNAME/idrm
2. Click "Compare & pull request"
3. Select base: main
4. Select compare: feature/add-email-notifications
5. Click "Create pull request"
```

---

### 6.2 Pull Request Template

**Title**: Clear and descriptive

```
Good Titles:
✅ Add email notifications for service creation
✅ Fix login redirect bug on mobile devices
✅ Update API reference documentation

Bad Titles:
❌ Updates
❌ Fix bug
❌ New feature
```

**Description**: Use this template

```markdown
### What does this PR do?

Brief description of the changes.

### Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

### Related Issue

Closes #123

### How Has This Been Tested?

Describe the tests you ran:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Tested on different browsers (if frontend)

### Screenshots (if applicable)

[Add screenshots here]

### Checklist

- [ ] My code follows the project's code standards
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code where necessary
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

---

### 6.3 Pull Request Best Practices

**Small PRs**:
```
✅ One feature/fix per PR
✅ Under 500 lines changed
✅ Easy to review
✅ Faster to merge

❌ Multiple unrelated changes
❌ 2000+ lines changed
❌ Hard to review
❌ Likely to have issues
```

**Good PR Description**:
```markdown
### What does this PR do?

Adds email notifications when a service request is created. 
Users will receive an email confirmation with service details 
and tracking link.

### Type of Change

- [x] New feature

### Related Issue

Closes #123

### How Has This Been Tested?

- [x] Unit tests for EmailService class
- [x] Integration test for notification flow
- [x] Manual testing with Gmail and Outlook
- [x] Verified HTML email renders correctly

Test Coverage: 95% (added 12 new tests)

### Screenshots

[Email screenshot here]

### Checklist

- [x] Code follows standards (Black, flake8 passing)
- [x] Self-reviewed code
- [x] Added docstrings
- [x] Updated API documentation
- [x] All tests passing (42/42)
```

---

## 7. **Code Review Process**

### 7.1 What to Expect

**Timeline**:
```
1. You submit PR
   ↓
2. Automated checks run (1-5 min)
   - Linting
   - Tests
   - Code coverage
   ↓
3. Maintainer reviews (1-3 days)
   - Code quality
   - Tests
   - Documentation
   ↓
4. Changes requested OR approved
   ↓
5. You address feedback
   ↓
6. Final approval
   ↓
7. PR merged! 🎉
```

---

### 7.2 Review Comments

**Types of Comments**:

**Blocking** (must fix):
```
❗ This has a security vulnerability
❗ This breaks existing functionality
❗ Missing required tests
```

**Suggestion** (nice to have):
```
💡 Consider using a list comprehension here
💡 This could be refactored for clarity
💡 Add a docstring here
```

**Question**:
```
❓ Why did you choose this approach?
❓ Can you explain this logic?
❓ Is this tested?
```

**Praise**:
```
👍 Great solution!
✨ Nice refactoring
🎉 Excellent test coverage
```

---

### 7.3 Responding to Feedback

**Good Response**:
```markdown
> Consider using a list comprehension here

Good idea! Changed in commit abc123.

> Why did you choose this approach?

I chose this because it handles edge case X better. 
Alternative approach Y would fail when Z happens.
Happy to change if you prefer Y though!

> This has a security vulnerability

Oh no! Fixed in commit def456. Also added test to prevent 
regression. Thanks for catching this!
```

**Making Changes**:
```bash
## Make the requested changes
## Edit files...

## Commit changes
git add .
git commit -m "Address review comments

- Use list comprehension in filter_services
- Add docstring to create_service
- Fix security issue in auth validation"

## Push to same branch
git push origin feature/add-email-notifications

## PR automatically updates!
```

---

## 8. **Community Guidelines**

### 8.1 Communication Channels

**GitHub Issues**:
- Bug reports
- Feature requests
- Technical discussions

**GitHub Discussions**:
- General questions
- Ideas and brainstorming
- Show and tell

**Discord** (coming soon):
- Real-time chat
- Quick questions
- Community hangout

**Email**:
- Private/sensitive issues
- Security vulnerabilities
- Contact: security@idrm.gov.in

---

### 8.2 Asking Good Questions

**Before Asking**:
```
✅ Search existing issues
✅ Read documentation
✅ Try to solve it yourself
✅ Prepare minimal example
```

**Good Question**:
```markdown
### Context

I'm trying to add a new filter to the service list API.

### What I'm Trying to Do

Add a `created_after` query parameter to filter services 
created after a specific date.

### What I've Tried

```python
@router.get("/services")
def list_services(created_after: Optional[datetime] = None):
    query = db.query(Service)
    if created_after:
        query = query.filter(Service.created_at > created_after)
    return query.all()
```

### The Problem

Getting error: `TypeError: can't compare datetime.datetime to NoneType`

### Environment

- Python 3.11
- FastAPI 0.109.0
- PostgreSQL 15

### Question

How should I handle the datetime comparison when `created_after` is None?
```

**Bad Question**:
```
Help! My code doesn't work!

[no code]
[no error message]
[no context]
```

---

### 8.3 Helping Others

**Be Welcoming**:
```
❌ "This is a dumb question"
✅ "Great question! Here's how..."

❌ "Read the docs"
✅ "This is covered in Section X of the docs: [link]"

❌ "Your code is terrible"
✅ "Here's a suggestion to improve this..."
```

**Provide Context**:
```markdown
The error you're seeing is because...

Here's a working example:
```python
[code example]
```

You might also want to check out:
- Documentation: [link]
- Similar issue: #123
```

---

## 9. **Getting Help**

### 9.1 Resources

**Documentation**:
```
Getting Started:
- 00-GETTING-STARTED.md
- 49-IDRM-COMPLETE-DEVELOPMENT-GUIDE.md

Reference:
- 44-API-REFERENCE-MATRIX-v3.1-SECURITY.md
- 45-DATABASE-QUERY-REFERENCE.md
- 47-FRONTEND-WORKFLOWS-REFERENCE.md

Standards:
- 41-CODE-STANDARDS.md
- 42-VERIFICATION-CHECKLISTS.md
```

**External Resources**:
```
Python:
- Official Docs: https://docs.python.org/3/
- FastAPI Docs: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/

Frontend:
- MDN Web Docs: https://developer.mozilla.org/
- Tailwind CSS: https://tailwindcss.com/
- Leaflet: https://leafletjs.com/

Git:
- Pro Git Book: https://git-scm.com/book/en/v2
- GitHub Docs: https://docs.github.com/
```

---

### 9.2 Mentorship Program

**Find a Mentor**:
```
1. Check mentors list in GitHub Discussions
2. Comment on their intro post
3. Schedule introductory call
4. Work together on issues
```

**Become a Mentor**:
```
Requirements:
- Contributed 3+ PRs
- Good understanding of codebase
- Patient and helpful
- Available 2-4 hours/week
```

---

### 🎉 **Ready to Contribute!**

**Your Journey**:
```
1. ✅ Read this guide
2. ⏳ Fork repository
3. ⏳ Set up development environment
4. ⏳ Find a good first issue
5. ⏳ Make your contribution
6. ⏳ Submit pull request
7. ⏳ Address feedback
8. ⏳ Get merged!
9. 🎉 Celebrate!
```

**Remember**:
- Everyone started as a beginner
- Questions are welcome
- Mistakes are learning opportunities
- Your contribution matters
- Be patient with yourself
- Have fun!

---

### 📊 **Contribution Stats**

Track your progress:
```
Contributions:
- [ ] First issue commented
- [ ] First PR submitted
- [ ] First PR merged
- [ ] Helped another contributor
- [ ] Reviewed a PR
- [ ] 5 PRs merged
- [ ] 10 PRs merged
- [ ] Became a mentor

Badges (coming soon):
🥉 Bronze Contributor (1 PR)
🥈 Silver Contributor (5 PRs)
🥇 Gold Contributor (10 PRs)
💎 Diamond Contributor (25 PRs)
```

---

### 🙏 **Thank You!**

**Every contribution matters**:
- Bug fixes save time
- Features help users
- Documentation helps newcomers
- Tests prevent regressions
- Code reviews improve quality

**You're helping save lives** by contributing to IDRM. 

**Welcome to the team!** 🚀

---

**Document Complete!**  
**Status**: ✅ Ready for Contributors  
**Version**: 3.0  
**Last Updated**: May 16, 2026

**Questions?** Open an issue on GitHub or join our Discord!

---

## IDRM MVP: Contributor Guide v3.0

### Making Disaster Response Technology Accessible - Multi-Platform Edition

**Version**: 3.0  
**Last Updated**: May 24, 2026  
**Platforms**: HTML/Tailwind + React SPA + React Native + Python Backend

Thank you for your interest in contributing to IDRM! This guide will help you get started with our multi-platform architecture.

---

### Project Vision

IDRM (Integrated Disaster Response Management) is building a unified, map-driven digital platform for coordinating disaster response in India. We believe disaster response technology should be:

- **Open**: Transparent code, open data standards
- **Accessible**: Easy to deploy, easy to contribute
- **Privacy-first**: Protect vulnerable populations
- **Community-driven**: Built by people who care
- **Multi-platform**: Web, admin dashboard, and mobile apps

---

### 🎯 What's New in v3.0

#### Three Frontend Interfaces

Contributors can now work on:

1. **HTML/Tailwind (Primary Web)** - `/frontend-html`
   - Main citizen-facing interface
   - Vanilla JS + Tailwind CSS
   - Built with Bun + Vite

2. **React SPA (Advanced Web)** - `/frontend-react`
   - Admin dashboards and analytics
   - TypeScript + React 18 + Tailwind
   - Built with Bun + Vite

3. **React Native (Mobile)** - `/mobile`
   - iOS and Android apps
   - TypeScript + Expo
   - Native features (GPS, offline, push)

#### Updated Tech Stack

- **Runtime**: Bun (replaced Node.js)
- **Python Env**: Miniconda (replaced venv)
- **Geospatial**: Python service (replaced Java GeoServer)
- **Cache**: Redis (NEW)
- **Three Frontends**: HTML, React, React Native

---

### Ways to Contribute

#### 1. Code Contributions

##### Backend (Python/FastAPI)
**What we need**:
- Add new API endpoints
- Improve database queries
- Implement geospatial features
- Add tests
- Improve error handling
- Add validation

**Skills needed**: Python, FastAPI, PostgreSQL, PostGIS

**Good first issues**:
- Add input validation to existing endpoints
- Write tests for uncovered code
- Improve API documentation
- Add error messages
- Optimize database queries

##### Frontend 1: HTML/Tailwind (Primary Web)
**What we need**:
- Improve UI/UX
- Add map visualizations
- Create responsive designs
- Accessibility improvements
- Progressive enhancement
- Offline capabilities

**Skills needed**: HTML, CSS, JavaScript, Tailwind, Leaflet

**Good first issues**:
- Fix accessibility issues (WCAG 2.1)
- Improve mobile responsiveness
- Add loading states
- Improve error messages
- Add keyboard navigation

##### Frontend 2: React SPA (Admin Dashboard)
**What we need**:
- Build admin components
- Create data visualizations
- Implement complex forms
- Add state management
- Build analytics dashboards
- Add charts and graphs

**Skills needed**: React, TypeScript, Tailwind, Redux/Zustand, Charts

**Good first issues**:
- Create reusable components
- Add TypeScript types
- Build data tables
- Implement filtering
- Add pagination

##### Frontend 3: React Native (Mobile)
**What we need**:
- Build mobile screens
- Implement offline functionality
- Add GPS/location features
- Implement push notifications
- Optimize performance
- Add native animations

**Skills needed**: React Native, TypeScript, Expo, Native APIs

**Good first issues**:
- Build basic screens
- Add form validation
- Implement offline queue
- Add loading indicators
- Improve navigation

##### Python Geospatial Service (NEW)
**What we need**:
- Tile generation optimization
- GeoJSON serving
- Spatial query optimization
- Caching strategies
- Map styling

**Skills needed**: Python, GeoPandas, Shapely, PostGIS

**Good first issues**:
- Add caching to tile endpoint
- Optimize spatial queries
- Add more map styles
- Improve error handling

##### DevOps/Infrastructure
**What we need**:
- CI/CD improvements
- Deployment automation
- Monitoring setup
- Performance optimization
- Security hardening

**Skills needed**: Docker, NGINX, systemd, Linux, GitHub Actions

**Good first issues**:
- Add health check endpoints
- Improve logging
- Add monitoring metrics
- Optimize Docker images
- Add security headers

#### 2. Documentation

**What we need**:
- API documentation
- User guides
- Deployment tutorials
- Architecture diagrams
- Code comments
- README improvements
- Translations (Hindi, regional languages)

**Good first issues**:
- Fix typos
- Improve code comments
- Add examples to API docs
- Create beginner tutorials
- Translate UI strings

#### 3. Testing

**What we need**:
- Unit tests (backend)
- Integration tests
- E2E tests (frontend)
- Mobile app tests
- Load testing
- Security testing
- Accessibility testing

**Good first issues**:
- Add tests for uncovered functions
- Write E2E test cases
- Add accessibility tests
- Test edge cases

#### 4. Design & UX

**What we need**:
- UI/UX improvements
- Accessibility enhancements
- Mobile-first designs
- Design system updates
- User research
- Usability testing

**Good first issues**:
- Improve color contrast
- Add loading states
- Improve error messages
- Create mockups
- Test on real devices

#### 5. Translation

**What we need**:
- Hindi translation
- Regional language support (Tamil, Telugu, Bengali, etc.)
- RTL support (if needed)

**Good first issues**:
- Translate UI strings
- Add language files
- Test translations

---

### Getting Started

#### Prerequisites

```bash
## Required software
- Ubuntu 22.04 or 24.04 (or WSL2 on Windows)
- Git
- Python 3.11 (via Miniconda)
- Bun 1.x
- PostgreSQL 16 + PostGIS 3.4
- Redis 7.2+
- Node.js 18+ (for React Native only)

## Optional
- VS Code / VSCodium
- DBeaver (database GUI)
- Expo Go app (for mobile testing)
```

#### Setup Development Environment

**1. Clone Repository**

```bash
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp
```

**2. Install Backend Dependencies**

```bash
## Create Miniconda environment
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

## Install Python packages
cd backend
pip install --break-system-packages -r requirements.txt

## Install geospatial libraries
conda install -c conda-forge geopandas shapely gdal fiona -y
```

**3. Setup Database**

```bash
## Create database and user
sudo -u postgres psql -c "CREATE USER idrm_user WITH PASSWORD 'idrm_pass';"
sudo -u postgres psql -c "CREATE DATABASE idrm_db OWNER idrm_user;"
sudo -u postgres psql -d idrm_db -c "CREATE EXTENSION postgis;"

## Run migrations
cd backend
alembic upgrade head
```

**4. Install Frontend Dependencies**

```bash
## HTML/Tailwind frontend
cd frontend-html
bun install

## React SPA frontend
cd ../frontend-react
bun install

## React Native mobile
cd ../mobile
npm install
```

**5. Start Development Servers**

```bash
## Terminal 1: Backend
cd backend
conda activate idrm-mvp
uvicorn app.main:app --reload --port 8000

## Terminal 2: HTML Frontend
cd frontend-html
bun run dev              # Port 5173

## Terminal 3: React Frontend
cd frontend-react
bun run dev              # Port 5174

## Terminal 4 (optional): Mobile
cd mobile
npx expo start
```

---

### Development Workflow

#### Git Workflow

We use **GitHub Flow** (simplified Git workflow):

```bash
## 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/add-search-filter

## 2. Make changes and commit
git add .
git commit -m "feat: add search filter to service list"

## 3. Push to your fork
git push origin feature/add-search-filter

## 4. Create Pull Request on GitHub
## - Add description
## - Link related issues
## - Request reviewers

## 5. Address review feedback
## Make changes
git add .
git commit -m "fix: address review comments"
git push origin feature/add-search-filter

## 6. Merge (after approval)
## Maintainers will merge your PR
```

#### Commit Message Convention

We follow **Conventional Commits**:

```bash
## Format
<type>(<scope>): <subject>

## Types
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Code style (formatting, no code change)
refactor: Code refactoring
test:     Add or update tests
chore:    Maintenance tasks

## Examples
feat(api): add search endpoint for services
fix(map): correct marker positioning
docs(readme): update installation steps
style(frontend): format code with prettier
refactor(db): optimize service query
test(api): add tests for auth endpoints
chore(deps): update dependencies
```

#### Code Style

##### Python (Backend)

```bash
## Format with black
black backend/

## Lint with ruff
ruff check backend/

## Type check with mypy
mypy backend/

## Before committing
black backend/ && ruff check backend/ && mypy backend/
```

**Code style**:
- Use type hints
- Max line length: 88 (black default)
- Follow PEP 8
- Use docstrings for functions

```python
## Good
async def get_service_by_id(
    service_id: int,
    db: Session = Depends(get_db)
) -> ServiceResponse:
    """
    Get service request by ID.
    
    Args:
        service_id: Unique service identifier
        db: Database session
        
    Returns:
        ServiceResponse with service details
        
    Raises:
        HTTPException: If service not found
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return ServiceResponse.from_orm(service)
```

##### JavaScript/TypeScript (Frontend)

```bash
## Format with Prettier
bun run format

## Lint with ESLint
bun run lint

## Type check (TypeScript)
bun run type-check

## Before committing
bun run format && bun run lint && bun run type-check
```

**Code style**:
- Use TypeScript for React projects
- Use const/let, not var
- Use arrow functions
- Use template literals
- Follow Airbnb style guide

```typescript
// Good (React component)
import { useState, useEffect } from 'react';
import { ServiceCard } from '@/components';
import { getServices } from '@/services/api';
import type { Service } from '@/types';

export const ServiceList = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const data = await getServices();
        setServices(data);
      } catch (error) {
        console.error('Failed to fetch services:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchServices();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="space-y-4">
      {services.map(service => (
        <ServiceCard key={service.id} service={service} />
      ))}
    </div>
  );
};
```

---

### Testing

#### Backend Tests (pytest)

```bash
cd backend

## Run all tests
pytest

## Run with coverage
pytest --cov=app --cov-report=html

## Run specific test file
pytest tests/api/test_services.py -v

## Run tests matching pattern
pytest -k "test_create" -v

## Run only failed tests
pytest --lf
```

**Writing tests**:

```python
## tests/api/test_services.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_service():
    """Test creating a service request"""
    response = client.post(
        "/api/v1/services",
        json={
            "title": "Medical supplies needed",
            "description": "Urgent medical supplies",
            "service_type": "medical",
            "priority": "high",
            "location": {
                "latitude": 19.0760,
                "longitude": 72.8777
            }
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Medical supplies needed"
    assert data["service_type"] == "medical"

def test_get_services():
    """Test listing services"""
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

#### Frontend Tests (Vitest)

```bash
cd frontend-react

## Run tests
bun test

## Watch mode
bun test:watch

## Coverage
bun test:coverage
```

**Writing tests**:

```typescript
// components/Button.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
  
  it('applies variant styles', () => {
    render(<Button variant="danger">Delete</Button>);
    const button = screen.getByText('Delete');
    expect(button).toHaveClass('bg-error');
  });
});
```

---

### Pull Request Guidelines

#### Before Submitting

- [ ] Code follows style guidelines (black, prettier, eslint)
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow convention
- [ ] No console.log or debug code
- [ ] Code is self-documenting or well-commented

#### PR Description Template

```markdown
### Description
Brief description of what this PR does.

### Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

### Related Issues
Closes #123

### How to Test
1. Start backend: `uvicorn app.main:app --reload`
2. Navigate to http://localhost:8000/docs
3. Test endpoint: POST /api/v1/services
4. Verify response

### Screenshots (if applicable)
[Add screenshots for UI changes]

### Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

### Code Review Process

#### As a Contributor

**When you submit a PR**:
1. Wait for automated checks (CI/CD) to pass
2. Address any failing tests or linting issues
3. Respond to reviewer comments
4. Make requested changes
5. Mark conversations as resolved
6. Request re-review when ready

**Responding to feedback**:
```markdown
## Good response
> Could we add error handling here?

Good catch! I've added try-catch and appropriate error messages.
Updated in commit abc123.

## Not helpful response
> Could we add error handling here?

Done.
```

#### As a Reviewer

**What to check**:
- [ ] Code solves the problem correctly
- [ ] Tests cover new functionality
- [ ] No obvious bugs or edge cases missed
- [ ] Code is readable and maintainable
- [ ] Follows project conventions
- [ ] Performance considerations addressed
- [ ] Security issues addressed
- [ ] Documentation updated

**Feedback guidelines**:
- Be kind and constructive
- Explain the "why" behind suggestions
- Distinguish between required changes and suggestions
- Praise good solutions
- Use "we" not "you"

```markdown
## Good feedback
We could improve performance here by caching the result. 
This endpoint might be called frequently.

Suggestion: Add Redis caching with 5-minute TTL.

## Not helpful feedback
This is slow.
```

---

### Platform-Specific Guidelines

#### HTML/Tailwind Frontend

**Component structure**:
```html
<!-- components/service-card.html -->
<div class="bg-white rounded-lg shadow-sm border-l-4 border-priority-high p-6">
  <div class="flex items-start justify-between">
    <div class="flex-1">
      <h3 class="text-lg font-medium text-neutral-900 mb-1">
        {title}
      </h3>
      <p class="text-sm text-neutral-600">
        {description}
      </p>
    </div>
  </div>
</div>
```

**JavaScript modules**:
```javascript
// js/api.js
export class ApiClient {
  constructor(baseURL = 'http://localhost:8000/api/v1') {
    this.baseURL = baseURL;
  }
  
  async getServices() {
    const response = await fetch(`${this.baseURL}/services`);
    if (!response.ok) throw new Error('Failed to fetch services');
    return response.json();
  }
}
```

#### React SPA Frontend

**Component structure**:
```typescript
// components/ServiceCard.tsx
import { Service } from '@/types';

interface ServiceCardProps {
  service: Service;
  onView?: (id: number) => void;
}

export const ServiceCard = ({ service, onView }: ServiceCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border-l-4 border-priority-high p-6">
      <h3 className="text-lg font-medium text-neutral-900">
        {service.title}
      </h3>
      <p className="text-sm text-neutral-600">
        {service.description}
      </p>
      {onView && (
        <button onClick={() => onView(service.id)}>
          View Details
        </button>
      )}
    </div>
  );
};
```

#### React Native Mobile

**Component structure**:
```typescript
// components/ServiceCard.tsx
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Colors, Typography } from '@/design-tokens';
import type { Service } from '@/types';

interface ServiceCardProps {
  service: Service;
  onPress?: () => void;
}

export const ServiceCard = ({ service, onPress }: ServiceCardProps) => {
  return (
    <TouchableOpacity 
      style={styles.card} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={styles.title}>{service.title}</Text>
      <Text style={styles.description}>{service.description}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: Colors.priority.high.default,
  },
  title: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.neutral[900],
    marginBottom: 4,
  },
  description: {
    fontSize: Typography.fontSize.sm,
    color: Colors.neutral[600],
  },
});
```

---

### Community

#### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions
- **Discord** (optional): Real-time chat (if set up)

#### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy towards other contributors
- Accept constructive criticism gracefully

**Not acceptable**:
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Unwelcome sexual attention

---

### Recognition

Contributors are recognized:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contributor badge
- Special recognition for major contributions

---

### Questions?

- Check existing [GitHub Issues](https://github.com/your-org/idrm-mvp/issues)
- Ask in [GitHub Discussions](https://github.com/your-org/idrm-mvp/discussions)
- Read the docs in `/docs`
- Reach out to maintainers

---

### Thank You!

Every contribution, no matter how small, helps make disaster response technology more accessible. Thank you for being part of this mission! 🙏

**Together, we're building technology that saves lives.** ❤️
