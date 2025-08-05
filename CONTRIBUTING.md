# Contributing to CPRA Processor Demo

Thank you for your interest in contributing to the CPRA Processor Demo! This project aims to help public agencies leverage AI for transparency while maintaining data privacy.

## 🤝 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## 🚀 Getting Started

### Prerequisites

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/cpra-processor-demo.git
   cd cpra-processor-demo
   ```

3. Set up development environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Install Ollama and required models:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull gemma3:latest
   ```

### Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test thoroughly:
   ```bash
   python -m pytest tests/ -v
   ```

3. Commit with clear messages:
   ```bash
   git commit -m "feat: add new feature description"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a Pull Request on GitHub

## 📝 Contribution Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add type hints where appropriate
- Maximum line length: 100 characters

### Documentation

- Add docstrings to all functions and classes
- Update README.md if adding new features
- Include inline comments for complex logic
- Update tests to cover new functionality

### Commit Messages

We follow conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or changes
- `chore:` Maintenance tasks

Example:
```
feat: add batch processing for large email sets

- Implement chunking for datasets over 100 emails
- Add progress callback for batch operations
- Update tests for batch functionality
```

### Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting PR
- Aim for >90% code coverage
- Include both unit and integration tests

Run tests:
```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html

# Specific test file
python -m pytest tests/test_email_parser.py -v
```

## 🎯 Areas for Contribution

### Priority Areas

1. **Additional Document Formats**
   - PDF parsing support
   - Word document processing
   - CSV/Excel handling

2. **Enhanced AI Analysis**
   - Additional exemption types
   - Multi-language support
   - Improved confidence scoring

3. **Performance Optimizations**
   - Parallel processing
   - Caching mechanisms
   - Memory usage optimization

4. **User Interface**
   - Accessibility improvements
   - Mobile responsive design
   - Dark mode support

5. **Export Formats**
   - Additional export templates
   - Customizable privilege logs
   - Batch export capabilities

### Good First Issues

Look for issues labeled `good first issue` on GitHub. These are typically:
- Documentation improvements
- Simple bug fixes
- Test additions
- Code cleanup tasks

## 🔄 Pull Request Process

### Before Submitting

1. **Test thoroughly**: Run all tests and ensure they pass
2. **Update documentation**: Include relevant documentation changes
3. **Check code style**: Ensure PEP 8 compliance
4. **Rebase if needed**: Keep your branch up to date with main

### PR Template

When opening a PR, please include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Tested with demo data

## Checklist
- [ ] Code follows style guidelines
- [ ] Added/updated documentation
- [ ] No sensitive data included
- [ ] Updated CHANGELOG.md (if applicable)
```

### Review Process

1. Automated tests must pass
2. At least one maintainer review required
3. Address all review comments
4. Maintain clean commit history

## 🐛 Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Ollama version and models
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Describe:
- Use case and motivation
- Proposed solution
- Alternative approaches considered
- Potential impact on existing features

## 📚 Development Resources

### Project Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for:
- System design overview
- Module responsibilities
- Data flow diagrams
- API documentation

### AI Model Integration

When working with Ollama:
- Test with multiple models
- Handle timeout gracefully
- Implement retry logic
- Document prompt engineering

### Testing Guidelines

- Unit tests: `tests/test_*.py`
- Integration tests: `tests/test_integration.py`
- End-to-end tests: `test_end_to_end.py`
- Mock external dependencies

## 🔒 Security Considerations

### Important Guidelines

- **Never commit sensitive data** (API keys, passwords, real emails)
- **Use synthetic data** for testing
- **Validate all inputs** to prevent injection attacks
- **Handle errors gracefully** without exposing system details
- **Document security implications** of changes

### Privacy Focus

This project prioritizes privacy:
- Ensure all processing remains local
- Don't add external API calls
- Avoid telemetry or analytics
- Document any network requirements

## 📞 Getting Help

### Resources

- Review existing issues and PRs
- Check [PROGRESS_TRACKER.md](PROGRESS_TRACKER.md) for development history
- Read [DEMO_GUIDE.md](DEMO_GUIDE.md) for functionality overview
- Consult [README.md](README.md) for setup instructions

### Communication

- Open an issue for bugs or features
- Use discussions for questions
- Tag maintainers for urgent items
- Be patient and respectful

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Acknowledged in documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make government transparency tools more accessible! 🙏