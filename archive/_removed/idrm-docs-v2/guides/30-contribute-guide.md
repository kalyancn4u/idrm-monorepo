> *Type: Guide (novice / how-to) · Audience: Contributors · Status: Archived — v2 historical generation*

# IDRM MVP: Contributor Guide

<!-- IDRM-CLEANUP doc=v2-g30-contribute status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — contributor guide → current
> Superseded by [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> (+ [`git-github-101`](../../../../guides/mvp/learn/git-github-101.md), [`sdlc-101`](../../../../guides/mvp/learn/sdlc-101.md)). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Making Disaster Response Technology Accessible

Thank you for your interest in contributing to IDRM! This guide will help you get started.

---

## Project Vision

IDRM (Integrated Disaster Response Management) is building a unified, map-driven digital platform for coordinating disaster response in India. We believe disaster response technology should be:

- **Open**: Transparent code, open data standards
- **Accessible**: Easy to deploy, easy to contribute
- **Privacy-first**: Protect vulnerable populations
- **Community-driven**: Built by people who care

---

## Ways to Contribute

### 1. Code Contributions

**Backend (Python/FastAPI)**
- Add new API endpoints
- Improve database queries
- Implement geospatial features
- Add tests

**Frontend (HTML/JavaScript/Leaflet)**
- Improve UI/UX
- Add map visualizations
- Create responsive designs
- Accessibility improvements

**DevOps/Infrastructure**
- Docker improvements
- CI/CD pipelines
- Deployment automation
- Monitoring setup

### 2. Documentation

- API documentation
- User guides
- Deployment tutorials
- Architecture diagrams
- Translations

### 3. Testing

- Write unit tests
- Integration tests
- Load testing
- Security testing
- User acceptance testing

### 4. Design

- UI/UX design
- Logo and branding
- Map styling
- Wireframes
- User flows

### 5. Domain Expertise

- Disaster management best practices
- Privacy/security audit
- Accessibility audit
- Legal/compliance review
- Translation (Hindi, regional languages)

---

## Getting Started

### Prerequisites

- **For Backend**: Python 3.11+, basic SQL knowledge
- **For Frontend**: HTML/CSS/JavaScript basics, Leaflet experience helpful
- **For DevOps**: Docker, Linux basics
- **For All**: Git basics, enthusiasm!

### Setup Development Environment

1. **Fork the Repository**
   ```bash
   # On GitHub, click "Fork" button
   # Then clone your fork
   git clone https://github.com/YOUR_USERNAME/idrm-mvp.git
   cd idrm-mvp
   ```

2. **Follow Week 1 Setup Guide**
   - See `docs/week-1-implementation-guide.md`
   - This sets up your local environment
   - Takes ~2-3 hours first time

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-123
   ```

### Making Your First Contribution

**Good First Issues**: Look for issues tagged `good-first-issue` or `help-wanted`

**Easy Wins**:
- Fix typos in documentation
- Add code comments
- Write tests for existing code
- Improve error messages
- Add validation

---

## Development Workflow

### 1. Pick an Issue

- Check [GitHub Issues](https://github.com/yourusername/idrm-mvp/issues)
- Comment "I'd like to work on this"
- Wait for maintainer confirmation
- Ask questions if unclear

### 2. Write Code

**Code Style**:
- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use ES6+, consistent indentation
- **SQL**: Uppercase keywords, descriptive names

**Commit Messages**:
```
feat: Add service request filtering by date range
fix: Correct spatial query for nearby providers
docs: Update API documentation for auth endpoints
test: Add unit tests for user service
```

### 3. Test Your Code

**Backend Tests**:
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

**Manual Testing**:
- Test API endpoints using Swagger UI
- Verify database changes
- Check logs for errors

### 4. Submit Pull Request

```bash
# Commit your changes
git add .
git commit -m "feat: Your feature description"

# Push to your fork
git push origin feature/your-feature-name
```

**In GitHub**:
- Create Pull Request from your branch
- Fill in PR template
- Link related issue
- Wait for review

### 5. Code Review Process

- Maintainer reviews code
- Address feedback
- Update based on comments
- Get approval
- Merged! 🎉

---

## Code Standards

### Python (Backend)

**File Structure**:
```python
"""
Module docstring explaining purpose.
"""
from typing import Optional, List
from uuid import UUID

# Standard library imports
# Third-party imports  
# Local imports

class ServiceExample:
    """Class docstring."""
    
    async def method_name(self, param: str) -> Optional[dict]:
        """
        Method docstring.
        
        Args:
            param: Parameter description
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When parameter is invalid
        """
        # Implementation
        pass
```

**Type Hints**: Always use type hints
**Async/Await**: Use for database operations
**Error Handling**: Specific exceptions, descriptive messages
**Testing**: Write tests for new code

### JavaScript (Frontend)

**Style**:
```javascript
// Use const/let, not var
const apiUrl = 'http://localhost:8000/api/v1';

// Arrow functions
const fetchServices = async () => {
  try {
    const response = await fetch(`${apiUrl}/services`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching services:', error);
    throw error;
  }
};

// Descriptive names
function displayServiceOnMap(service) {
  // Implementation
}
```

### SQL

**Style**:
```sql
-- Uppercase keywords
SELECT 
    s.service_id,
    s.service_type,
    ST_AsGeoJSON(s.location) AS location_geojson,
    u.full_name AS requestor_name
FROM service_requests s
INNER JOIN users u ON s.requestor_id = u.user_id
WHERE s.status = 'APPROVED'
    AND s.created_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY s.created_at DESC;

-- Add comments for complex queries
-- This query finds all approved services from last week
```

---

## Testing Guidelines

### Unit Tests

**Backend (pytest)**:
```python
import pytest
from app.services.user_service import UserService

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test user creation"""
    user_data = {
        "email": "test@example.com",
        "password": "secure123",
        "full_name": "Test User"
    }
    
    user = await UserService.create_user(db_session, user_data)
    
    assert user.email == "test@example.com"
    assert user.is_active is True
```

### Integration Tests

Test API endpoints end-to-end:
```python
@pytest.mark.asyncio
async def test_register_and_login(client):
    """Test complete auth flow"""
    # Register
    register_response = await client.post(
        "/api/v1/users/register",
        json={"email": "new@example.com", "password": "pass123", ...}
    )
    assert register_response.status_code == 201
    
    # Login
    login_response = await client.post(
        "/api/v1/users/login",
        json={"email": "new@example.com", "password": "pass123"}
    )
    assert "access_token" in login_response.json()
```

### Test Coverage

Aim for:
- **Critical paths**: 90%+ coverage
- **Business logic**: 80%+ coverage
- **Overall**: 70%+ coverage

---

## Documentation Standards

### Code Documentation

**Python Docstrings** (Google style):
```python
def calculate_distance(point1: tuple, point2: tuple) -> float:
    """
    Calculate distance between two geographic points.
    
    Uses Haversine formula for great-circle distance.
    
    Args:
        point1: Tuple of (latitude, longitude) in degrees
        point2: Tuple of (latitude, longitude) in degrees
        
    Returns:
        Distance in meters
        
    Example:
        >>> distance = calculate_distance((17.385, 78.486), (17.390, 78.490))
        >>> print(f"Distance: {distance:.2f} meters")
    """
```

**API Documentation**:
- Use FastAPI's automatic OpenAPI docs
- Add response examples
- Document error codes
- Include authentication requirements

### README Files

Each major component should have a README:
- `backend/README.md` - Backend setup
- `frontend/README.md` - Frontend setup
- `database/README.md` - Database schema
- `docs/README.md` - Documentation index

---

## Security Guidelines

### Do's

✅ **Validate all inputs**
```python
from pydantic import BaseModel, EmailStr, Field

class UserInput(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
```

✅ **Use parameterized queries**
```python
# Good
result = await db.execute(
    select(User).where(User.email == email)
)

# Never do string concatenation with user input!
```

✅ **Hash passwords**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash(password)
```

✅ **Check authorization**
```python
if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
    raise HTTPException(status_code=403, detail="Insufficient permissions")
```

### Don'ts

❌ Don't commit secrets (`.env` files, API keys)
❌ Don't expose internal errors to users
❌ Don't trust client-side validation alone
❌ Don't store passwords in plain text
❌ Don't skip input validation

### Security Checklist for PRs

- [ ] No secrets in code
- [ ] Input validation added
- [ ] Authorization checks present
- [ ] SQL injection prevented
- [ ] XSS risks mitigated
- [ ] Error handling doesn't leak info

---

## Git Workflow

### Branch Naming

```
feature/user-authentication
feature/geospatial-search
bugfix/issue-123-login-error
docs/api-documentation
test/service-endpoints
hotfix/critical-security-patch
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add service request filtering
fix: Resolve spatial query timeout
docs: Update deployment guide
test: Add user service tests
refactor: Simplify auth middleware
style: Format code with Black
chore: Update dependencies
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issue
Fixes #123

## Testing Done
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
- [ ] Tests pass
```

---

## Communication

### Where to Ask Questions

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code-specific questions
- **Email**: Private/security concerns

### Response Times

- **Issues**: ~48 hours
- **Pull Requests**: ~72 hours  
- **Urgent Security**: ~24 hours

### Being a Good Community Member

✅ Be respectful and inclusive
✅ Provide constructive feedback
✅ Help others learn
✅ Celebrate contributions
✅ Assume good intentions

❌ No harassment or discrimination
❌ No spam or self-promotion
❌ No hostile or aggressive behavior

---

## Recognition

### Contributors

All contributors are listed in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes

### Types of Contributions Recognized

- Code contributions
- Documentation improvements
- Bug reports with reproduction steps
- Thoughtful issue discussions
- Helping other contributors
- Testing and QA
- Design and UX
- Translation

---

## Project Roadmap

### Current Phase: MVP (Months 1-3)

- [x] Core database schema
- [ ] Authentication system
- [ ] Service request CRUD
- [ ] Basic geospatial features
- [ ] Simple map interface
- [ ] Basic RBAC

### Next Phase: Enhancement (Months 4-6)

- [ ] Advanced spatial queries
- [ ] Real-time notifications
- [ ] Analytics dashboard
- [ ] Mobile-responsive UI
- [ ] Automated matching
- [ ] Advanced privacy controls

### Future Phase: Scale (Months 7-12)

- [ ] Mobile applications
- [ ] Multi-language support
- [ ] Chatbot integration
- [ ] Predictive analytics
- [ ] Third-party integrations
- [ ] Advanced reporting

---

## Resources

### Learning Resources

**Python/FastAPI**:
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Async Python](https://realpython.com/async-io-python/)

**PostGIS/Geospatial**:
- [PostGIS Documentation](https://postgis.net/documentation/)
- [Introduction to PostGIS](https://postgis.net/workshops/postgis-intro/)
- [Leaflet Documentation](https://leafletjs.com/reference.html)

**Docker**:
- [Docker Getting Started](https://docs.docker.com/get-started/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

**Testing**:
- [pytest Documentation](https://docs.pytest.org/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)

### Similar Projects

- [Sahana Eden](https://sahanafoundation.org/) - Disaster management platform
- [CogniCity](https://cognicity.info/) - Community-led disaster response
- [Ushahidi](https://www.ushahidi.com/) - Crowdsourcing platform

---

## FAQ for Contributors

**Q: I'm new to open source. Can I contribute?**  
A: Absolutely! Start with documentation, tests, or issues tagged `good-first-issue`.

**Q: Do I need to know everything to contribute?**  
A: No! You can contribute to areas you know. We'll help you learn.

**Q: How long until my PR is reviewed?**  
A: Usually 2-3 days. Be patient, we're volunteers too!

**Q: My PR got rejected. What now?**  
A: Don't worry! Address the feedback and resubmit. It's part of learning.

**Q: Can I work on something not in the issues?**  
A: Yes, but create an issue first to discuss it with maintainers.

**Q: I found a security vulnerability. What should I do?**  
A: Email us privately (see SECURITY.md), don't create a public issue.

**Q: How can I become a maintainer?**  
A: Consistent, quality contributions over time. We'll reach out!

---

## License

This project is licensed under [LICENSE TO BE DETERMINED - suggest MIT or Apache 2.0 for open source].

By contributing, you agree that your contributions will be licensed under the same license.

---

## Thank You!

Every contribution, no matter how small, makes a difference. Together, we're building technology that can save lives during disasters.

**Let's build something meaningful! 🚀**

---

## Contact

- **Project Maintainer**: [Your Name/Contact]
- **GitHub**: [Repository URL]
- **Email**: [Contact Email]
- **Documentation**: [Docs URL]

---

*Last Updated: [Date]*
*Version: 1.0*
