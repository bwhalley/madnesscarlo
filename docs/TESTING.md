# Testing Strategy for MTG Madness Simulator

## Overview

This document outlines the comprehensive testing strategy for the MTG Madness Monte Carlo simulator. The test suite ensures that card data reading, game simulation mechanics, and statistical analysis remain reliable as the codebase evolves.

## Test Coverage

### 1. **Condition Parsing Tests** (`TestConditionParsing`)
Tests the parsing of condition strings from the CSV deck file.

**Coverage:**
- Empty/invalid conditions
- Land requirements (`requires:lands>=3`)
- Color requirements (`requires:color=U`)
- Effect parsing (`effect:mana_G`, `effect:draw2_discard2`)
- Multiple conditions separated by semicolons
- Timing and category conditions

**Why it matters:** Condition parsing is critical for determining when cards can be played and what effects they produce.

### 2. **Deck Class Tests** (`TestDeck`)
Tests the Deck class that loads and manages card data from CSV.

**Coverage:**
- Loading deck from CSV file
- Correct card quantity expansion
- Card metadata storage (type, mana cost, conditions)
- Shuffling randomization
- Drawing cards (normal, empty deck, partial draws)

**Why it matters:** The Deck class is the foundation of all simulations. Any bugs here would affect every game.

### 3. **Game State Tests** (`TestGameState`)
Tests the core game simulation mechanics.

**Coverage:**
- Initial state setup
- Drawing cards and hand management
- Turn-based card tracking
- Playing lands
- Mana color tracking
- Casting requirements (land count, color requirements)
- Color availability checking

**Why it matters:** GameState tracks everything that happens during a game. Errors here would produce invalid simulation results.

### 4. **Mulligan Logic Tests** (`TestMulliganLogic`)
Tests the London mulligan implementation.

**Coverage:**
- Counting lands in hand
- Detecting creatures in hand
- Mulligan decisions (0-1 lands, 5+ lands, no creatures)
- Keeping good hands
- Card removal preferences (land priority, key card protection)
- Full mulligan process integration

**Why it matters:** Mulligan logic significantly affects opening hand quality and simulation results.

### 5. **Simulation Tests** (`TestSimulation`)
Tests the end-to-end game simulation.

**Coverage:**
- Basic simulation execution
- Configuration integration
- Turn progression
- Mana color tracking throughout games
- Output format validation

**Why it matters:** Integration tests ensure all components work together correctly.

### 6. **Ideal Setup Evaluation Tests** (`TestIdealSetups`)
Tests the evaluation of specific card/color combinations.

**Coverage:**
- Successful setup detection
- Failure cases (missing cards, cards seen too late, wrong colors)
- Turn limit enforcement

**Why it matters:** Ideal setups are key metrics for deck evaluation.

### 7. **Configuration Tests** (`TestConfiguration`)
Tests loading and parsing configuration files.

**Coverage:**
- Valid configuration loading
- Missing file handling
- Configuration structure validation

**Why it matters:** Ensures config-driven behavior works reliably.

### 8. **Edge Cases Tests** (`TestEdgeCases`)
Tests unusual or boundary conditions.

**Coverage:**
- Empty decks
- Zero-quantity cards
- Malformed condition strings
- Zero-turn simulations
- Dual lands providing multiple colors

**Why it matters:** Edge cases often reveal hidden bugs.

### 9. **Statistical Tests** (`TestStatistics`)
Tests statistical properties of simulations.

**Coverage:**
- Mulligan rate distribution
- Card draw progression
- Variance across multiple runs

**Why it matters:** Validates that simulation results are statistically reasonable.

## Running the Tests

### Prerequisites

Install pytest:
```bash
pip install pytest pytest-cov
```

### Basic Test Execution

Run all tests:
```bash
pytest test_madness.py -v
```

Run specific test class:
```bash
pytest test_madness.py::TestConditionParsing -v
```

Run specific test:
```bash
pytest test_madness.py::TestDeck::test_deck_loading -v
```

### Coverage Report

Generate coverage report:
```bash
pytest test_madness.py --cov=madness --cov-report=html
```

View the report:
```bash
open htmlcov/index.html
```

### Test Output

Tests use verbose output showing:
- ✅ Passed tests with descriptions
- ❌ Failed tests with detailed error messages
- Test execution time
- Coverage statistics

## Test Data

The test suite includes fixtures that generate temporary test files:

### `simple_deck_csv`
A minimal deck with basic lands and creatures for testing core functionality.

### `complex_deck_csv`
A deck with card draw effects and dual lands for testing advanced features.

### `test_config`
Sample configuration for testing setup evaluation.

### Static Test Data
Located in `test_data/` directory:
- `minimal_deck.csv` - Minimal valid deck for manual testing
- `test_config.json` - Sample configuration file

## Continuous Testing

### Pre-Commit Testing

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pytest test_madness.py --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### Automated Testing

For CI/CD, use GitHub Actions or similar:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest test_madness.py --cov=madness
```

## What Each Test Protects Against

| Test Category | Protects Against |
|--------------|------------------|
| Condition Parsing | Breaking card effect/requirement parsing, invalid mana costs |
| Deck Class | Incorrect card quantities, broken shuffle, draw logic errors |
| Game State | Hand tracking bugs, mana calculation errors, turn progression issues |
| Mulligan Logic | Keeping unplayable hands, over-mulliganing, incorrect card removal |
| Simulation | Integration failures, config not applied, missing output fields |
| Ideal Setups | False positives/negatives in combo detection, turn limit bugs |
| Configuration | Config file format changes, missing required fields |
| Edge Cases | Crashes on unusual input, malformed data handling |
| Statistics | Unrealistic simulation results, broken randomization |

## Adding New Tests

When adding new functionality:

1. **Add tests first** (TDD approach)
2. **Test the happy path** - Normal expected usage
3. **Test edge cases** - Boundaries, empty inputs, maximum values
4. **Test error cases** - Invalid input, missing data
5. **Test integration** - How it works with existing code

Example:
```python
def test_new_card_effect(self, complex_deck_csv):
    """Test new card effect implementation."""
    deck = Deck(complex_deck_csv)
    state = GameState(deck)
    
    # Setup test conditions
    state.hand["New Card"] = 1
    
    # Execute the action
    play_new_card(state)
    
    # Verify expected behavior
    assert state.expected_property == expected_value
```

## Test Maintenance

### When to Update Tests

- **Card mechanics change** → Update game state tests
- **Mulligan rules change** → Update mulligan tests
- **New condition types added** → Update condition parsing tests
- **Configuration format changes** → Update config tests
- **New statistics tracked** → Add new statistical tests

### Red-Green-Refactor Cycle

1. **Red** - Write a failing test for new functionality
2. **Green** - Implement minimal code to pass the test
3. **Refactor** - Improve code while keeping tests green

## Known Limitations

Current tests do NOT cover:
- Excel export formatting (would require openpyxl validation)
- CLI argument parsing (argparse)
- Terminal output formatting
- Progress bar display (tqdm)
- Performance benchmarks

These are acceptable limitations as they involve UI/formatting rather than core logic.

## Test Performance

Expected test execution time: **< 5 seconds**

If tests take longer:
- Check for expensive operations in test setup
- Consider reducing simulation iterations in statistical tests
- Use mocking for slow external dependencies

## Debugging Failed Tests

When a test fails:

1. **Read the error message** - Shows expected vs actual
2. **Check the test description** - Explains what should happen
3. **Run with `-vv`** - Extra verbose output
4. **Run single test** - Isolate the failure
5. **Use `pytest --pdb`** - Drop into debugger on failure

Example debugging session:
```bash
# Run single failing test with debugger
pytest test_madness.py::TestDeck::test_deck_loading --pdb -v

# When it fails, you'll drop into pdb
# Use 'p variable_name' to inspect values
# Use 'l' to see current code location
# Use 'c' to continue execution
```

## Success Criteria

Tests are successful when:
- ✅ All tests pass consistently
- ✅ Code coverage > 80% for core modules
- ✅ Tests run in < 5 seconds
- ✅ No flaky tests (random failures)
- ✅ Clear error messages on failures

## Integration with Development

### Workflow

```
1. Write test for new feature
2. Run tests (should fail)
3. Implement feature
4. Run tests (should pass)
5. Refactor if needed
6. Run tests (should still pass)
7. Commit changes
```

### Best Practices

- Keep tests independent (no shared state)
- Use descriptive test names
- One assertion per test (when possible)
- Fast tests are better tests
- Test behavior, not implementation

## Questions or Issues?

If tests fail unexpectedly:
1. Ensure all dependencies are installed
2. Check Python version (3.7+)
3. Verify test data files exist
4. Run with `-v` for details
5. Check if changes broke assumptions

## Summary

This testing strategy ensures that:
- ✅ **Card data reading works correctly** - All deck parsing and condition logic is validated
- ✅ **Game simulation is accurate** - Turn progression, mana, and card interactions work properly
- ✅ **Mulligan logic is sound** - Opening hands meet quality standards
- ✅ **Statistics are reliable** - Aggregation and reporting produce correct results
- ✅ **Changes don't break existing functionality** - Regression testing prevents bugs

By running these tests before commits, you can confidently make changes knowing that core functionality remains intact.

