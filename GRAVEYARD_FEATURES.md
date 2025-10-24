# Graveyard & Advanced Mechanics Implementation

## Overview
This document describes the graveyard state tracking and advanced game mechanics added to the madness simulator.

## New Condition/Effect Types Supported

### 1. **Madness** (`madness_COST`)
- **Format**: `effect:madness_2G`, `effect:madness_0`
- **Behavior**: When a card with madness is discarded, it can be cast for its madness cost instead of going to the graveyard
- **Implementation**: Automatically triggered during discard effects
- **Mana Check**: Verifies color requirements are available before casting
- **Examples**: 
  - Basking Rootwalla (madness_0)
  - Arrogant Wurm (madness_2G)

### 2. **Flashback** (`flashback_COST`)
- **Format**: `effect:flashback_3G`
- **Behavior**: Cast spell from graveyard for flashback cost, then exile
- **Implementation**: Checked during activated abilities phase
- **Token Creation**: Roar of the Wurm creates Wurm Token on battlefield
- **Examples**: 
  - Roar of the Wurm (flashback_3G)

### 3. **Returns** (`returns`)
- **Format**: `effect:returns`
- **Behavior**: At the start of each turn, returns from graveyard to hand
- **Implementation**: Processed at beginning of turn step
- **Examples**: 
  - Squee, Goblin Nabob

### 4. **Discard + Tutor** (`discard1_tutor1`)
- **Format**: `effect:discard1_tutor1`
- **Behavior**: Discard a creature card, search deck for another creature and put it in hand
- **Madness Interaction**: Discarded creatures can trigger madness
- **Examples**: 
  - Survival of the Fittest

### 5. **Discard** (`discard1`)
- **Format**: `effect:discard1`
- **Behavior**: Discard a card (used for activated abilities)
- **Madness Interaction**: Discarded cards can trigger madness
- **Examples**: 
  - Wild Mongrel
  - Waterfront Bouncer

### 6. **Flying** (`flying`)
- **Format**: `effect:flying`
- **Behavior**: Grants flying to creatures while in graveyard
- **Implementation**: Tracked in graveyard for analytics (not affecting combat)
- **Examples**: 
  - Wonder

## New GameState Tracking

### Core Zone Tracking
```python
state.graveyard = Counter()      # Cards in graveyard
state.battlefield = Counter()    # Creatures/permanents in play
```

### Mechanic Tracking
```python
state.madness_casts = Counter()      # Cards cast via madness
state.flashback_casts = Counter()    # Cards cast via flashback
state.cards_tutored = Counter()      # Cards tutored to hand
```

## New Helper Methods

### Zone Movement
- `move_to_graveyard(card_name, from_hand=True)` - Move card from hand/battlefield to graveyard
- `play_creature(card_name)` - Play creature from hand to battlefield
- `cast_with_madness(card_name)` - Cast card using madness (to battlefield/graveyard)
- `cast_with_flashback(card_name)` - Cast from graveyard using flashback (exile after)

### Effect Queries
- `has_effect(card_name, effect_name)` - Check if card has specific effect
- `get_card_effect(card_name, effect_prefix)` - Extract effect value (e.g., cost)

## Turn Structure Updates

### New Turn Sequence
1. **Start of Turn**: Process returns (Squee, etc.)
2. **Main Phase**: Play land, cast spells from hand
3. **Activated Abilities**: Use creature/enchantment abilities
4. **Flashback Check**: Cast spells from graveyard
5. **End of Turn**: Draw card

## Card Actions Added

### Spells
- `play_careful_study()` - Draw 2, discard 2 with madness
- `play_frantic_search()` - Draw 2, discard 2 with madness
- `play_survival()` - Play Survival enchantment
- `activate_survival()` - Discard creature, tutor creature

### Creatures
- `play_basking_rootwalla()` - Play from hand
- `play_arrogant_wurm()` - Play from hand  
- `play_wild_mongrel()` - Play from hand
- `activate_wild_mongrel()` - Discard to pump (with madness)
- `play_waterfront_bouncer()` - Play from hand
- `activate_waterfront_bouncer()` - Discard to bounce (with madness)
- `play_wonder()` - Play from hand

### Flashback
- `play_roar_flashback()` - Cast Roar from graveyard, create token

## New Statistics Output

### Excel Sheets Added

#### 1. **Graveyard Stats**
- Card name
- Average count in graveyard
- Percentage of games with card in graveyard

#### 2. **Battlefield Stats**  
- Card name
- Average count on battlefield
- Percentage of games with card on battlefield

#### 3. **Madness Casts**
- Card name
- Total madness casts
- Percentage of games with madness cast

#### 4. **Flashback Casts**
- Card name  
- Total flashback casts
- Percentage of games with flashback cast

#### 5. **Tutored Cards**
- Card name
- Times tutored
- Percentage of games tutored

### Summary Statistics Added
```
Average Graveyard Size: 3.897 cards
Average Creatures on Board: 3.39 creatures
Total Madness Casts: 248 (across 1000 games)
Total Flashback Casts: 86 (across 1000 games)
```

## Example Results (1000 games, 4 turns)

### Key Findings
- **Graveyard Usage**: Average of ~4 cards in graveyard by turn 4
- **Board Presence**: Average of ~3.4 creatures on battlefield
- **Madness Efficiency**: ~25% of games successfully cast cards via madness
- **Flashback Usage**: ~9% of games used flashback abilities
- **Mulligan Rate**: 29% mulligan rate with default strategy

### Top Cards in Graveyard
1. Careful Study (card draw spell)
2. Frantic Search (card draw spell)
3. Forest/Island (discarded lands)
4. Squee, Goblin Nabob (returns to hand)

### Top Cards on Battlefield
1. Basking Rootwalla (madness creature)
2. Arrogant Wurm (madness creature)
3. Wild Mongrel (discard outlet)
4. Wurm Token (from flashback)

## Technical Notes

### Madness Trigger Logic
1. Card is discarded (via Careful Study, Wild Mongrel, etc.)
2. Check if card has `madness_X` effect
3. Parse madness cost for color requirements
4. If colors available, cast with madness → battlefield/graveyard
5. Otherwise, goes to graveyard normally

### Flashback Logic
1. During activated abilities phase
2. Check graveyard for cards with `flashback_X`
3. Verify can pay flashback cost
4. Cast spell, apply effects
5. Exile card (removed from tracking)

### Returns Logic
1. At start of turn, before land drop
2. Check graveyard for cards with `returns` effect
3. Move each matching card from graveyard to hand
4. Continue with normal turn

## Configuration

No additional configuration required. All new mechanics work automatically based on card conditions in `deck.csv`.

### Example Deck Entry
```csv
Card Name,Quantity,Type,Mana Cost,Conditions
Arrogant Wurm,4,Creature,2G,requires:lands>=2;color=G;effect:madness_2G
Squee, Goblin Nabob,4,Creature,2R,requires:lands>=2;color=R;effect:returns
Survival of the Fittest,4,Enchantment,1G,requires:lands>=2;color=G;effect:discard1_tutor1
```

## Future Enhancements

Potential additions for deeper analysis:
- Turn-by-turn graveyard snapshots
- Graveyard composition by card type
- Madness opportunity vs usage rate (had madness card but no outlet)
- Flashback timing analysis (turn flashback was used)
- Flying grant tracking (Wonder in graveyard = flying bonus)
- Mana efficiency with Frantic Search untapping

