# Testing Strategy Summary

## ✅ Test Suite Complete

Your MTG Madness Simulator now has a comprehensive test suite that validates all critical functionality.

## Test Coverage: 80%

```
Name         Stmts   Miss  Cover
--------------------------------
madness.py     289     58    80%
```

## Test Statistics

- **Total Tests**: 49
- **All Passing**: ✅
- **Execution Time**: < 0.5 seconds
- **Test Categories**: 9

## What's Being Tested

### 1. Condition Parsing (7 tests)
- ✅ Empty/invalid conditions
- ✅ Land requirements (`requires:lands>=3`)
- ✅ Color requirements (`requires:color=U`)
- ✅ Effect parsing (`effect:mana_G`)
- ✅ Multiple conditions
- ✅ Timing conditions
- ✅ Category conditions

**Protects against:** Breaking card requirements, mana cost parsing errors

### 2. Deck Loading (7 tests)
- ✅ CSV file loading
- ✅ Card quantity expansion
- ✅ Metadata storage
- ✅ Shuffling
- ✅ Drawing cards (normal, empty, partial)

**Protects against:** Incorrect deck sizes, broken shuffle, draw logic errors

### 3. Game State Management (8 tests)
- ✅ Initial state setup
- ✅ Card drawing
- ✅ Turn-based tracking
- ✅ Land playing
- ✅ Mana color tracking
- ✅ Casting requirements
- ✅ Color availability

**Protects against:** Hand tracking bugs, mana calculation errors, turn progression issues

### 4. Mulligan Logic (10 tests)
- ✅ Land counting
- ✅ Creature detection
- ✅ Mulligan decisions (0-1 lands, 5+ lands, no creatures)
- ✅ Good hand keeping
- ✅ Card removal priorities
- ✅ Full mulligan process

**Protects against:** Keeping unplayable hands, incorrect mulligan decisions, broken card removal

### 5. Game Simulation (4 tests)
- ✅ Basic simulation
- ✅ Configuration integration
- ✅ Turn progression
- ✅ Mana color tracking

**Protects against:** Integration failures, config not applied, missing output fields

### 6. Ideal Setup Evaluation (3 tests)
- ✅ Successful setup detection
- ✅ Missing card failures
- ✅ Turn limit enforcement

**Protects against:** False positives/negatives in combo detection

### 7. Configuration Loading (3 tests)
- ✅ Valid config files
- ✅ Missing file handling
- ✅ Structure validation

**Protects against:** Config parsing errors, missing required fields

### 8. Edge Cases (5 tests)
- ✅ Empty decks
- ✅ Zero quantity cards
- ✅ Malformed conditions
- ✅ Zero turn simulations
- ✅ Dual land colors

**Protects against:** Crashes on unusual input, malformed data

### 9. Statistical Validation (2 tests)
- ✅ Mulligan rate distribution
- ✅ Card draw progression

**Protects against:** Unrealistic simulation results, broken randomization

## Running Tests

### Quick Test
```bash
./run_tests.sh
```

### With Coverage Report
```bash
./run_tests.sh coverage
```

### Fast Tests Only
```bash
./run_tests.sh quick
```

### Watch Mode (auto-rerun on changes)
```bash
./run_tests.sh watch
```

## Test Files Created

1. **`test_madness.py`** (682 lines)
   - Comprehensive test suite
   - 49 tests covering all major functionality
   - Uses pytest fixtures for test data

2. **`test_data/minimal_deck.csv`**
   - Sample deck for manual testing
   - Simple 2-color deck

3. **`test_data/test_config.json`**
   - Sample configuration file
   - Test ideal setups

4. **`pytest.ini`**
   - Pytest configuration
   - Coverage settings
   - Test markers

5. **`run_tests.sh`**
   - Convenient test runner
   - Multiple test modes

6. **`.github/workflows/tests.yml`**
   - CI/CD workflow for GitHub Actions
   - Tests on Python 3.9-3.12

7. **`TESTING.md`** (comprehensive guide)
   - Detailed testing strategy
   - Test categories explained
   - Usage instructions

## What's NOT Tested (By Design)

The following are intentionally not tested as they are UI/formatting concerns:
- Excel export formatting
- CLI argument parsing
- Terminal output/colors
- Progress bar display (tqdm)

These areas don't affect simulation accuracy and are lower risk.

## Test Philosophy

### Why 80% Coverage is Sufficient

The 20% uncovered code consists primarily of:
- Main entry point (`if __name__ == "__main__"`)
- CLI argument handling
- Excel formatting
- Console output

These are UI/formatting concerns that don't affect core simulation logic.

### What We Prioritized

We focused testing on:
1. **Data integrity** - Card reading and parsing
2. **Game logic** - State management, casting, mana
3. **Mulligan correctness** - Decision making
4. **Statistical accuracy** - Simulation results

## Continuous Integration

Tests run automatically on:
- Every push to `main` or `develop`
- Every pull request
- Python versions: 3.9, 3.10, 3.11, 3.12

## Pre-Commit Hook (Optional)

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pytest test_madness.py --tb=short
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Future Test Additions

When adding new features, add tests for:
- New card effects
- New condition types
- New mulligan strategies
- New ideal setup configurations
- Edge cases discovered

## Maintenance

### Running Tests Before Commits
```bash
./run_tests.sh
```

### Checking Coverage After Changes
```bash
./run_tests.sh coverage
open htmlcov/index.html
```

### Debugging Failed Tests
```bash
pytest test_madness.py::TestName::test_specific_test -vv --pdb
```

## Success Criteria

Your test suite achieves:
- ✅ 80% code coverage (target met)
- ✅ All critical paths tested
- ✅ Fast execution (< 0.5s)
- ✅ Clear test descriptions
- ✅ Good edge case coverage
- ✅ Statistical validation

## Questions?

See `TESTING.md` for detailed documentation on:
- How each test works
- What each test protects against
- How to add new tests
- Debugging strategies
- Best practices

## Summary

Your MTG Madness Simulator is now protected by a comprehensive test suite that:
1. **Validates card data reading** - Ensures deck files parse correctly
2. **Tests simulation mechanics** - Verifies game state and turn logic
3. **Checks mulligan logic** - Confirms hand decisions are correct
4. **Verifies statistical accuracy** - Ensures simulation results are valid

**You can now make changes confidently**, knowing that the test suite will catch any regressions in core functionality! 🎉

