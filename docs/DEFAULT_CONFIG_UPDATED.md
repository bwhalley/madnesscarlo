# ✅ Default Configuration Updated

## What Was Done

Successfully reloaded the default simulation configuration from `simulation_config.json` to ensure all ideal setups and settings are properly configured in the database.

---

## 📊 Current Default Configuration

### Key Cards (4 total)
1. **Naturalize** - Enchantment removal
2. **Counterspell** - Counter protection
3. **Waterfront Bouncer** - Creature bounce
4. **Survival of the Fittest** - Tutor engine

### Ideal Setups (5 total)

#### 1. Survival Engine
- **Requires**: Survival of the Fittest
- **Must be in play**: Survival of the Fittest
- **Colors needed**: Green
- **Min lands**: 2
- **Needs creature in hand**: Yes
- **Turn limit**: 4

#### 2. Counter Protection
- **Requires**: Counterspell
- **Colors needed**: Blue
- **Turn limit**: 2

#### 3. Naturalize Access
- **Requires**: Naturalize
- **Colors needed**: Green
- **Turn limit**: 2

#### 4. Wonder in Graveyard
- **Requires**: Wonder
- **Must be in graveyard**: Wonder
- **Must be in play**: Island
- **Turn limit**: 4

#### 5. Roar Flashback Available
- **Requires**: Roar of the Wurm
- **Must be in graveyard**: Roar of the Wurm
- **Colors needed**: Green
- **Turn limit**: 4

### Sideboard Plans (3 total)
1. **vs_combo** - Counterspells and Blue Elemental Blast
2. **vs_aggro** - Cave-In and Chill
3. **vs_enchantments** - Reverent Silence and more Naturalize

### Other Settings
- **Default Runs**: 1000
- **Default Turns**: 4
- **Mulligan Strategy**: Enabled with detailed rules
- **Is Public**: Yes (available to all users)
- **Is Default**: Yes (automatically selected)

---

## 🎯 How to See This in Action

### 1. Run a New Simulation

**IMPORTANT**: You must run a **NEW simulation** with the updated default config!

```bash
1. Go to http://localhost:5173
2. Navigate to "🎲 Run Simulation"
3. Select your deck
4. Select "Default Madness Configuration" (or leave it as default)
5. Click "Run Simulation"
6. Wait for completion ✅
```

### 2. Export to Google Sheets

```bash
1. Go to "📊 Simulations" tab
2. Click on your completed simulation
3. Click "📊 Export to Google Sheets"
4. Wait 3-5 seconds
5. Click "📊 Open in Google Sheets"
```

### 3. Check the "Ideal Setups" Tab

You should now see **5 setups** with their success percentages:

```
Setup Name                    | Success %
Survival Engine               | 23.4%
Counter Protection            | 67.8%
Naturalize Access             | 45.2%
Wonder in Graveyard           | 34.6%
Roar Flashback Available      | 28.9%
```

*(Percentages are examples - actual values depend on your deck and simulation)*

---

## 🔧 Technical Changes

### 1. Updated `load_default_config.py`

**Added `--force` flag for non-interactive updates:**

```python
def load_default_config(force_update=False):
    """Load default configuration from simulation_config.json
    
    Args:
        force_update: If True, update existing config without prompting
    """
```

**Usage:**
```bash
# Interactive mode (prompts for confirmation)
python load_default_config.py

# Non-interactive mode (force update)
python load_default_config.py --force
```

### 2. Configuration Source

The configuration is loaded from:
- **Path**: `/Users/brian/madnesscarlo/backend/simulation_config.json`
- **Format**: JSON with all settings
- **Includes**: key_cards, ideal_setups, mulligan_strategy, sideboard_plans

### 3. Database Storage

Stored in `simulation_configs` table:
- **ID**: 4d414913-c59b-42c0-9402-a7fa53d1e846
- **User**: system (ID: 98beeb55-04e7-4596-9f8d-691f0d99b442)
- **Name**: "Default Madness Configuration"
- **Is Default**: true
- **Is Public**: true

---

## 📈 What Gets Tracked

### For Each Ideal Setup:

The simulation engine evaluates each setup every turn to see if the conditions are met:

1. **Card Requirements**: Do you have the required cards in hand/play/graveyard?
2. **Color Requirements**: Do you have the necessary mana colors available?
3. **Land Requirements**: Do you have enough lands in play?
4. **Turn Limit**: Is it within the specified turn window?

### Results Include:

- **Success Percentage**: % of games where the setup was achieved
- **Turn Distribution**: What turn the setup was typically achieved
- **Correlation Analysis**: Which cards together enable the setup

---

## 🎯 Example Use Cases

### Survival Engine Setup (23.4% success)

**What it measures:**
- Can I get Survival of the Fittest into play?
- Do I have 2+ lands (including green mana)?
- Do I have a creature in hand to pitch?
- Can I achieve this by turn 4?

**Why it matters:**
- Survival is your deck's engine
- 23.4% means it comes together in ~1 in 4 games
- If too low, consider adding more enablers or mulliganing differently

### Wonder in Graveyard Setup (34.6% success)

**What it measures:**
- Did Wonder end up in the graveyard?
- Do I have an Island in play?
- Was this achieved by turn 4?

**Why it matters:**
- Wonder gives all your creatures flying
- 34.6% means it's active in ~1 in 3 games
- If too low, add more discard outlets or card draw

---

## 🚀 Next Steps

### 1. Run Test Simulation

Run a simulation to see your ideal setups in action:
- Use your actual deck
- Select "Default Madness Configuration"
- Check the results

### 2. Review Setup Success Rates

In the Google Sheets export:
- Go to "Ideal Setups" tab
- See which setups work well
- Identify which need improvement

### 3. Adjust Your Deck

Based on the data:
- If "Survival Engine" is too low, add more green sources
- If "Wonder in Graveyard" is too low, add more discard
- If "Counter Protection" is too high, you might be drawing it too often

### 4. Iterate and Improve

- Modify your deck
- Run new simulations
- Compare results
- Keep refining!

---

## ✅ Verification Checklist

After running a new simulation, verify:

- [x] Default config is selected automatically
- [ ] Simulation completes successfully
- [ ] Export to Google Sheets works
- [ ] "Ideal Setups" tab shows 5 setups
- [ ] All setups have success percentages
- [ ] Data makes sense for your deck

---

## 💡 Pro Tips

### 1. Track Setup Trends

Run multiple simulations and track how setup success rates change:
- After adding/removing cards
- After adjusting land count
- After changing mulligan strategy

### 2. Compare Setups

Use the success percentages to prioritize:
- High success = reliable, deck is built around it
- Low success = inconsistent, needs support
- Medium success = good balance, often the sweet spot

### 3. Use Setups for Deck Building

When building a new deck:
1. Define your ideal setups first
2. Run simulations to test
3. Adjust card counts based on setup success rates
4. Repeat until you hit your target percentages

---

## 🎊 Summary

Your default configuration now includes:
- ✅ **4 key cards** tracked
- ✅ **5 ideal setups** evaluated
- ✅ **3 sideboard plans** ready
- ✅ **Detailed mulligan strategy**
- ✅ **All settings from simulation_config.json**

**The "Ideal Setups" tab in your Google Sheets exports will now show all 5 configured setups!**

Run a new simulation to see it in action! 🚀

