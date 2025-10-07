# Contributing to eChama Backend

Thank you for your interest in contributing to the eChama Backend project! This guide will help you get started with contributing to our Django REST Framework API for managing digital chamas.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Click the "Fork" button on GitHub, then clone your fork
   git clone https://github.com/your-username/echama-backend.git
   cd echama-backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django djangorestframework djangorestframework-simplejwt drf-yasg
   ```

4. **Set up the database**
   ```bash
   cd echama_backend/echama_project
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Development Workflow

### Branch Naming Convention
- `feature/description` - for new features
- `bugfix/description` - for bug fixes
- `docs/description` - for documentation updates
- `refactor/description` - for code refactoring

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow Python PEP 8 style guidelines
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   ```bash
   python manage.py test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

### Commit Message Guidelines
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Examples:
- `Add: user authentication endpoints`
- `Fix: loan approval validation bug`
- `Update: API documentation for contributions`

## Code Standards

### Python/Django Guidelines
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to classes and functions
- Keep functions small and focused
- Use Django best practices for models, views, and serializers

### Model Guidelines
- Add `__str__` methods to all models
- Use appropriate field types and constraints
- Add help_text for complex fields
- Follow Django naming conventions

### API Guidelines
- Use appropriate HTTP status codes
- Implement proper error handling
- Add appropriate permissions and authentication
- Document endpoints with docstrings

## Testing

### Running Tests
```bash
python manage.py test
```

### Writing Tests
- Write tests for new features and bug fixes
- Use Django's TestCase class
- Test both success and failure scenarios
- Mock external dependencies

### Test Coverage
- Aim for at least 80% test coverage
- Focus on testing business logic and edge cases

## Pull Request Process

1. **Ensure your branch is up to date**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Create a pull request**
   - Use a clear and descriptive title
   - Describe what changes you made and why
   - Reference any related issues
   - Include screenshots for UI changes

3. **Pull Request Checklist**
   - [ ] Code follows the style guidelines
   - [ ] Self-review of the code completed
   - [ ] Tests added for new functionality
   - [ ] All tests pass
   - [ ] Documentation updated if needed
   - [ ] No merge conflicts

## Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

### Feature Requests
Include:
- Clear description of the feature
- Use cases and benefits
- Possible implementation approach

## Documentation

### When to Update Documentation
- Adding new API endpoints
- Changing existing functionality
- Adding new features
- Fixing bugs that affect usage

### Documentation Standards
- Use clear, concise language
- Include code examples
- Update README.md for major changes
- Add docstrings to new functions and classes

## Getting Help

- Check existing issues and pull requests
- Read the project documentation
- Ask questions in issue comments
- Be respectful and patient

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Report unacceptable behavior

Thank you for contributing to eChama Backend! 🚀