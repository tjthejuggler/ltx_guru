# 📌 Sequence Maker - Automated Testing Guide

This guide explains how to run, add, and maintain automated tests for the **Sequence Maker PyQt6 application**.

## ⚙️ Testing Framework & Tools:

- **Pytest:** Simple and powerful Python testing framework.
- **pytest-qt:** Extends pytest for Qt-based application testing.

**Install required tools**:
```bash
pip install pytest pytest-qt
```

## 🚀 Running Tests:

- Run all tests from the project root directory:
```bash
pytest
```

- Run specific tests:
```bash
pytest tests/test_timeline.py
pytest tests/test_audio.py
```

- Verbose output:
```bash
pytest -v
```

## 🧩 Test Structure:

Organize tests in the tests/ directory as follows:

```
sequence-maker/
├── app/
├── resources/
├── ui/
├── main_window.py
└── tests/
    ├── __init__.py
    ├── conftest.py  # pytest-qt configuration and fixtures
    ├── test_main_window.py
    ├── test_timeline.py
    ├── test_audio.py
    └── test_utils.py
```

- **Unit Tests** (test_utils.py): Test individual methods (e.g., formatting functions).

- **Integration Tests** (test_audio.py, test_timeline.py): Ensure component interactions are stable.

- **UI/Functional Tests** (test_main_window.py): Verify GUI interactions (playback, dialogs, etc.).

## 🔨 Adding New Tests:

- Follow existing naming conventions: test_<module_name>.py.

- Each test should start with test_ and clearly describe its purpose:
```python
def test_playback_starts_audio(qtbot, app_fixture):
    ...
```

- Utilize fixtures (app_fixture) to simplify repeated setup.

## 📝 Updating Existing Tests:

When modifying application code:

- Always run tests before pushing changes.

- Update failing tests to align with new functionality if needed.

- Add tests covering any new features or significant changes.

## 🚧 Test Fixtures (conftest.py):

- Provide reusable test setups.
- Example:
```python
@pytest.fixture
def app_fixture(qtbot):
    from app.main import MyApp
    app = MyApp()
    window = MainWindow(app)
    qtbot.addWidget(window)
    return window
```

## ✅ Good Practices:

- Short, independent tests that verify one aspect each.

- Clear, descriptive names for test methods.

- Regularly run full test suite to catch regressions early.

For further questions, refer to this README or ask future programming LLM instances to review or extend the tests according to project needs.