# Web App UI Wireframes

## Visual Design Guide for MTG Madness Carlo Web App

This document describes the user interface and user experience for each major screen in the web application.

---

## Design Principles

1. **Clean & Minimal** - Focus on data, reduce clutter
2. **Card Game Aesthetic** - MTG-inspired colors (black, blue, green, red)
3. **Data-Dense** - Lots of statistics, but organized
4. **Responsive** - Works on desktop, tablet, and mobile
5. **Real-Time** - Live progress updates during simulations

### Color Palette

```
Primary:     #2563eb (Blue)
Secondary:   #10b981 (Green)
Accent:      #ef4444 (Red)
Background:  #f9fafb (Light Gray)
Card BG:     #ffffff (White)
Text:        #1f2937 (Dark Gray)
Border:      #e5e7eb (Light Border)
Success:     #10b981
Warning:     #f59e0b
Error:       #ef4444
```

---

## 1. Landing Page (Unauthenticated)

```
┌─────────────────────────────────────────────────────────────────┐
│  🎴 MTG Madness Carlo        [Login] [Sign Up]                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│              Monte Carlo Simulation for MTG Decks                │
│                                                                  │
│         Test your deck's consistency in seconds                  │
│                                                                  │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│    │   🎲 Simulate │  │ 🔬 Experiment │  │ ⚖️ Compare   │       │
│    │              │  │              │  │              │       │
│    │  Run 1000s   │  │  Auto-test   │  │  Side-by-    │       │
│    │  of games    │  │  variants    │  │  side decks  │       │
│    └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                                  │
│                      [Get Started Free]                          │
│                                                                  │
│  Features:                                                       │
│  ✓ Detailed statistics      ✓ Opening hand analysis             │
│  ✓ Parallel experiments     ✓ Real-time progress                │
│  ✓ Deck comparison          ✓ Export to Excel                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Dashboard (Main Page)

```
┌─────────────────────────────────────────────────────────────────┐
│  🎴 MTG Madness Carlo     [Dashboard] [Decks] [Sims] [Experiments]│
│  👤 brian@email.com ▼                                     [?] [⚙] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Welcome back, brian! 👋                                         │
│                                                                  │
│  Quick Stats                                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ 12 Decks     │ │ 45 Sims      │ │ 8 Experiments│            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                  │
│  Recent Activity                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ ⏰ 2 hours ago  • Simulation completed                │        │
│  │    "Madness v3" - 87% Survival Engine success        │        │
│  │    [View Results]                                     │        │
│  ├─────────────────────────────────────────────────────┤        │
│  │ ⏰ Yesterday    • Experiment finished                 │        │
│  │    "Land Count Test" - 7 Forests optimal             │        │
│  │    [View Results]                                     │        │
│  ├─────────────────────────────────────────────────────┤        │
│  │ ⏰ 2 days ago   • Deck created                        │        │
│  │    "Madness v4" - 60 cards                            │        │
│  │    [Edit] [Simulate]                                  │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  Quick Actions                                                   │
│  [➕ New Deck] [🎲 Run Simulation] [🔬 New Experiment]           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Deck List Page

```
┌─────────────────────────────────────────────────────────────────┐
│  My Decks                                   [+ New Deck] [Import]│
├─────────────────────────────────────────────────────────────────┤
│  [Search decks...]                     [Sort: Recent ▼] [Filter] │
│                                                                  │
│  ┌────────────────────────────────────┐  ┌──────────────────┐   │
│  │ 🎴 Madness v4                      │  │ 🎴 Madness v3    │   │
│  │                                    │  │                  │   │
│  │ "Latest iteration with more counter│  │ "Previous build" │   │
│  │  spells"                           │  │                  │   │
│  │                                    │  │ 60 cards         │   │
│  │ 60 cards • Updated 2h ago          │  │ Updated 3d ago   │   │
│  │                                    │  │                  │   │
│  │ 🔵🔵🔵🟢🟢 (WUBRG indicator)         │  │ 🔵🔵🔵🟢🟢       │   │
│  │                                    │  │                  │   │
│  │ [Edit] [Simulate] [Duplicate] [⋮]  │  │ [Edit] [Simulate]│   │
│  └────────────────────────────────────┘  └──────────────────┘   │
│                                                                  │
│  ┌────────────────────────────────────┐  ┌──────────────────┐   │
│  │ 🎴 Control Deck                    │  │ 🎴 Combo Test    │   │
│  │                                    │  │                  │   │
│  │ "Testing counter-heavy build"      │  │ "Experimental"   │   │
│  │                                    │  │                  │   │
│  │ 60 cards • Updated 1w ago          │  │ 60 cards         │   │
│  │                                    │  │                  │   │
│  │ 🔵🔵🔵                              │  │ 🟢🟢🔴🔴        │   │
│  │                                    │  │                  │   │
│  │ [Edit] [Simulate] [Duplicate] [⋮]  │  │ [Edit] [Simulate]│   │
│  └────────────────────────────────────┘  └──────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Deck Editor

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Decks                                      [Export ▼] │
├─────────────────────────────────────────────────────────────────┤
│  Deck Name: [Madness v4                           ]              │
│  Description: [Latest iteration with more counterspells...]      │
│                                                                  │
│  [✓] Public deck                                                 │
│                                                                  │
│  ┌────────────────────────┬────────────────────────┐            │
│  │  DECK EDITOR           │  STATS                 │            │
│  │                        │                        │            │
│  │ [🔍 Add card...]       │  Total Cards: 60       │            │
│  │                        │  Lands: 22 (37%)       │            │
│  │ ┌──────────────────┐   │  Creatures: 18 (30%)   │            │
│  │ │ Qty │ Card       │   │  Spells: 20 (33%)      │            │
│  │ ├─────┼────────────┤   │                        │            │
│  │ │  7  │ Island     │   │  Mana Curve:           │            │
│  │ │  7  │ Forest     │   │  █ (7 cards)           │            │
│  │ │  4  │ Yavimaya C.│   │  ███ (12 cards)        │            │
│  │ │  4  │ Survival...│   │  ██ (9 cards)          │            │
│  │ │  4  │ Wild Mong. │   │  █ (5 cards)           │            │
│  │ │  4  │ Basking R. │   │                        │            │
│  │ │  3  │ Careful S. │   │  Colors:               │            │
│  │ │  3  │ Frantic S. │   │  🔵 Blue: 45%          │            │
│  │ │  2  │ Arrogant W.│   │  🟢 Green: 55%         │            │
│  │ │  2  │ Squee      │   │                        │            │
│  │ │ ... │ ...        │   └────────────────────────┘            │
│  │ └─────┴────────────┘                                          │
│  │                                                                │
│  │ [Add Card] [Import CSV] [Clear All]                           │
│  └───────────────────────────────────────────────────────────────┤
│  [Cancel]                              [Save] [Save & Simulate]  │
└─────────────────────────────────────────────────────────────────┘

Card Row (Expanded):
┌─────────────────────────────────────────────────────────────────┐
│ [4▼] Wild Mongrel                                    [✏️] [🗑]   │
│ Type: Creature   Mana: 1G                                        │
│ Conditions: requires:lands>=2;color=G;category:creature          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Simulation Setup

```
┌─────────────────────────────────────────────────────────────────┐
│  New Simulation                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Select Deck                                             │
│  ┌─────────────────────────────────────────────────┐            │
│  │ [Madness v4                              ▼]     │            │
│  │                                                  │            │
│  │ 60 cards • Last simulated 2 hours ago           │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Step 2: Configuration                                           │
│  ┌─────────────────────────────────────────────────┐            │
│  │ Number of runs:    [1000        ]               │            │
│  │ Turns to simulate: [4           ]               │            │
│  │                                                  │            │
│  │ Configuration:     [Default ▼] [Edit Config]    │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Step 3: Sideboard (Optional)                                    │
│  ┌─────────────────────────────────────────────────┐            │
│  │ [ ] Post-sideboard                               │            │
│  │ Sideboard plan: [vs_combo ▼]                    │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Estimated runtime: ~45 seconds                                  │
│                                                                  │
│  [Cancel]                          [Start Simulation]            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Simulation Progress (Real-time)

```
┌─────────────────────────────────────────────────────────────────┐
│  Simulation in Progress...                             [Cancel] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Running simulation for: Madness v4                              │
│  Started: 2 minutes ago                                          │
│                                                                  │
│  Progress                                                        │
│  ┌──────────────────────────────────────────────────┐           │
│  │ ████████████████████████████░░░░░░░░░░░ 67%      │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  670 / 1000 games completed                                      │
│  Estimated time remaining: 22 seconds                            │
│                                                                  │
│  Preliminary Results (updating live):                            │
│  ┌─────────────────────────────────────────────────┐            │
│  │ Survival Engine Success:    85.2%               │            │
│  │ Average Mulligan Count:     0.4                 │            │
│  │ Games Kept Opening Hand:    68%                 │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Console Output:                                                 │
│  ┌─────────────────────────────────────────────────┐            │
│  │ [12:34:01] Starting simulation...                │            │
│  │ [12:34:02] Loaded deck: Madness v4               │            │
│  │ [12:34:02] Running 1000 games, 4 turns           │            │
│  │ [12:34:15] 500/1000 complete...                  │            │
│  │ [12:35:30] 670/1000 complete...                  │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Simulation Results Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│  Simulation Results: Madness v4                    [Export ▼]   │
│  Completed: 2m 45s ago • 1000 games • 4 turns                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Summary Metrics                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Survival Eng.│ │ Mulligan Rate│ │ Key Cards    │            │
│  │   87.2%      │ │   0.42       │ │   92% by T4  │            │
│  │   ✓ +2.1%    │ │   ✓ -0.05    │ │   ✓ +5%      │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│                                                                  │
│  [Card Stats] [Key Cards] [Ideal Setups] [Opening Hands]        │
│  [Graveyard] [Battlefield] [Madness] [Flashback] [Summary]      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  IDEAL SETUPS                                           │    │
│  │                                                          │    │
│  │  Setup Name              Success Rate    By Turn        │    │
│  │  ───────────────────────────────────────────────────    │    │
│  │  Survival Engine            87.2%         Turn 4        │    │
│  │  ████████████████████░░░░                               │    │
│  │                                                          │    │
│  │  Counter Protection         94.1%         Turn 2        │    │
│  │  ██████████████████████░░                               │    │
│  │                                                          │    │
│  │  Naturalize Access          76.3%         Turn 2        │    │
│  │  ███████████████░░░░░                                   │    │
│  │                                                          │    │
│  │  Wonder in Graveyard        52.8%         Turn 4        │    │
│  │  ███████████░░░░░░░░░                                   │    │
│  │                                                          │    │
│  │  Roar Flashback             48.2%         Turn 4        │    │
│  │  ██████████░░░░░░░░░░                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Opening Hand Analysis (Top Patterns)                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Pattern           Games    Avg Success    Details      │    │
│  │  ─────────────────────────────────────────────────────  │    │
│  │  3L 2C +Survival     47      100.0%       [View]        │    │
│  │  3L 2C +Squee        38       94.7%       [View]        │    │
│  │  2L 3C +Survival     52       88.5%       [View]        │    │
│  │  3L 3C               124      78.2%       [View]        │    │
│  │  2L 2C               89       65.2%       [View]        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  [Compare to Another Deck] [Run Again] [Share Results]          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Card Stats Table (Interactive)

```
┌─────────────────────────────────────────────────────────────────┐
│  Card Statistics                              [Search...] [↓CSV] │
├─────────────────────────────────────────────────────────────────┤
│  [All Cards ▼] [Filter by Type ▼] [Show: 25 ▼]                  │
│                                                                  │
│  ┌────┬───────────────────┬──────┬────────┬─────────┬────────┐  │
│  │ #  │ Card Name         │ Seen │ See %  │ Cast %  │ Trend  │  │
│  ├────┼───────────────────┼──────┼────────┼─────────┼────────┤  │
│  │ 1  │ Island            │ 3.2  │ 92.3%  │  -      │ ━━━━━  │  │
│  │ 2  │ Forest            │ 3.1  │ 91.8%  │  -      │ ━━━━━  │  │
│  │ 3  │ Survival of...    │ 2.8  │ 85.2%  │ 72.1%   │ ━━━━░  │  │
│  │ 4  │ Wild Mongrel      │ 2.6  │ 78.4%  │ 65.3%   │ ━━━░░  │  │
│  │ 5  │ Careful Study     │ 2.1  │ 72.8%  │ 68.2%   │ ━━━░░  │  │
│  │ 6  │ Squee, Goblin...  │ 1.8  │ 64.2%  │ 18.4%   │ ━━░░░  │  │
│  │ 7  │ Basking Rootw...  │ 2.4  │ 76.1%  │ 52.3%   │ ━━━░░  │  │
│  │ 8  │ Wonder            │ 0.9  │ 48.2%  │  8.1%   │ ━░░░░  │  │
│  │ ...│ ...               │ ...  │ ...    │ ...     │ ...    │  │
│  └────┴───────────────────┴──────┴────────┴─────────┴────────┘  │
│                                                                  │
│  Showing 1-25 of 60                        [◄] 1 [2] [3] [►]    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

Sortable columns, filterable, searchable
Hover for tooltips with detailed stats
Click row to see card details
```

---

## 9. Charts & Visualizations

```
┌─────────────────────────────────────────────────────────────────┐
│  Mulligan Distribution                                           │
│                                                                  │
│          Keep                                                    │
│          68.2%        ╱╲                                         │
│                     ╱    ╲                                       │
│                   ╱        ╲                                     │
│                 ╱            ╲                                   │
│               ╱                ╲                                 │
│             ╱      Mull 6        ╲                               │
│           ╱        21.4%           ╲                             │
│         ╱                            ╲                           │
│       ╱         Mull 5                 ╲                         │
│     ╱            7.8%                    ╲                       │
│   ╱                                        ╲                     │
│ ╱             Mull 4+: 2.6%                 ╲                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Success Rate by Turn                                            │
│                                                                  │
│  100% ┼                                           ●              │
│       │                                     ●                    │
│   80% ┼                            ●                             │
│       │                   ●                                      │
│   60% ┼          ●                                               │
│       │    ●                                                     │
│   40% ┼                                                          │
│       │                                                          │
│   20% ┼                                                          │
│       │                                                          │
│    0% └────┬────┬────┬────┬────┬────┬────┬────                  │
│           T1   T2   T3   T4   T5   T6   T7                      │
│                                                                  │
│  Legend:  ● Survival Engine  ▪ Counter Protection               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Experiment Setup

```
┌─────────────────────────────────────────────────────────────────┐
│  New Experiment                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Experiment Name: [Land Count Optimization              ]        │
│  Base Deck:       [Madness v4 ▼]                                │
│                                                                  │
│  Experiment Type: [Replace Quantity ▼]                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Card to vary:      [Forest ▼]                         │    │
│  │  Test quantities:   [5, 6, 7, 8, 9, 10            ]    │    │
│  │  Compensate with:   [Island ▼]                         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Configuration                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Runs per variant:     [1000        ]                   │    │
│  │  Optimization goal:    [Minimize Mulligans ▼]          │    │
│  │  Secondary goals:      [+ Add goal]                     │    │
│  │                        ☑ Maximize Survival Engine       │    │
│  │  Parallel workers:     [Auto (7) ▼]                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Preview: This will test 6 variants with 6,000 total runs        │
│  Estimated runtime: ~8 minutes                                   │
│                                                                  │
│  [Cancel]                               [Start Experiment]       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Experiment Progress (Multi-Variant)

```
┌─────────────────────────────────────────────────────────────────┐
│  Experiment: Land Count Optimization                  [Cancel]  │
│  Started 3 minutes ago                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Overall Progress                                                │
│  ┌──────────────────────────────────────────────────┐           │
│  │ ███████████████████████░░░░░░░░░░░░░░ 58%        │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
│  Variants: 4 of 6 completed                                      │
│  Estimated time remaining: 5 minutes                             │
│                                                                  │
│  Variant Progress                                                │
│  ┌─────────────────────────────────────────────────┐            │
│  │ ✓ 5 Forests (baseline)      100% ████████████   │            │
│  │ ✓ 6 Forests                 100% ████████████   │            │
│  │ ✓ 7 Forests                 100% ████████████   │            │
│  │ ✓ 8 Forests                 100% ████████████   │            │
│  │ ⏳ 9 Forests                  67% ████████░░░░   │            │
│  │ ⏸ 10 Forests                   0% ░░░░░░░░░░░░   │            │
│  └─────────────────────────────────────────────────┘            │
│                                                                  │
│  Live Rankings (preliminary):                                    │
│  ┌─────────────────────────────────────────────────┐            │
│  │  Rank  Variant        Mulligan  Survival Eng.   │            │
│  │  ───────────────────────────────────────────    │            │
│  │   🥇   7 Forests        0.38      88.2%         │            │
│  │   🥈   8 Forests        0.42      87.8%         │            │
│  │   🥉   6 Forests        0.46      85.1%         │            │
│  │   4    9 Forests*       0.51      82.3%         │            │
│  │   ...  ...              ...       ...           │            │
│  └─────────────────────────────────────────────────┘            │
│  * In progress                                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Experiment Results

```
┌─────────────────────────────────────────────────────────────────┐
│  Experiment Results: Land Count Optimization       [Export ▼]   │
│  Completed 5m ago • 6 variants • 6000 total runs                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Rankings] [Comparison] [Statistical Analysis] [Insights]       │
│                                                                  │
│  🎯 Optimization Goal: Minimize Mulligans                        │
│                                                                  │
│  Winner: 7 Forests (0.38 avg mulligan)                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  VARIANT RANKINGS                                       │    │
│  │                                                          │    │
│  │  Rank  Variant      Mulligan  Survival  Delta vs Base  │    │
│  │  ──────────────────────────────────────────────────     │    │
│  │  🥇 1  7 Forests     0.38      88.2%    -0.04 / +1.0%   │    │
│  │  🥈 2  8 Forests     0.42      87.8%     0.00 / +0.6%   │    │
│  │  🥉 3  6 Forests     0.46      85.1%    +0.04 / -2.1%   │    │
│  │     4  9 Forests     0.51      84.2%    +0.09 / -3.0%   │    │
│  │     5  10 Forests    0.58      81.8%    +0.16 / -5.4%   │    │
│  │     6  5 Forests     0.64      78.2%    +0.22 / -9.0%   │    │
│  │                                                          │    │
│  │  Baseline: 8 Forests (from original deck)               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Key Insights                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  💡 7 Forests is optimal for minimizing mulligans       │    │
│  │  💡 Also improves Survival Engine success by 1%         │    │
│  │  💡 10 Forests causes significant flood (58% mulligan)  │    │
│  │  💡 5 Forests causes mana screw (64% mulligan)          │    │
│  │  💡 Recommendation: Change -1 Forest, +1 Island         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  [Apply Winner to Deck] [Compare Top 3] [Run New Experiment]    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 13. Deck Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│  Deck Comparison                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Select Decks to Compare                                         │
│  ┌─────────────────────────────┬─────────────────────────────┐  │
│  │ Baseline:                   │ Variant:                    │  │
│  │ [Madness v3 ▼]              │ [Madness v4 ▼]              │  │
│  └─────────────────────────────┴─────────────────────────────┘  │
│                                                                  │
│  Configuration: [Default ▼]  Runs: [1000]                       │
│                                                                  │
│  [Compare Decks]                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

After comparison:
┌─────────────────────────────────────────────────────────────────┐
│  Comparison: Madness v3 vs Madness v4              [Export ▼]   │
│  Completed 3m ago • 2000 total runs                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Deck Changes                                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  -2 Naturalize          +2 Counterspell                 │    │
│  │  -1 Waterfront Bouncer  +1 Frantic Search               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  [Overview] [Ideal Setups] [Opening Hands] [Card Impact]        │
│                                                                  │
│  Ideal Setup Comparison                                          │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Setup              Baseline  Variant   Delta           │    │
│  │  ────────────────────────────────────────────────────   │    │
│  │  Survival Engine     85.1%    87.2%    +2.1% ✓         │    │
│  │  Counter Protection  91.2%    94.1%    +2.9% ✓         │    │
│  │  Naturalize Access   78.2%    76.3%    -1.9% ✗         │    │
│  │  Wonder in Grave     54.1%    52.8%    -1.3% ≈         │    │
│  │  Roar Flashback      49.2%    48.2%    -1.0% ≈         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Summary: 2 improvements, 2 slight declines, 1 neutral           │
│                                                                  │
│  Opening Hand Pattern Changes                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Pattern            Change      Impact                  │    │
│  │  ──────────────────────────────────────────────────     │    │
│  │  3L 2C +Counter     +12 games   +5.2% success           │    │
│  │  3L 2C +Survival    -2 games    +1.8% success           │    │
│  │  2L 3C              +8 games    -1.2% success           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  💡 Net positive: +2.1% Survival Engine, +2.9% Counter Prot.    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 14. Configuration Editor

```
┌─────────────────────────────────────────────────────────────────┐
│  Edit Configuration: Default                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [General] [Key Cards] [Ideal Setups] [Mulligan] [Sideboard]    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  GENERAL SETTINGS                                       │    │
│  │                                                          │    │
│  │  Default Runs:           [1000        ]                 │    │
│  │  Default Turns:          [4           ]                 │    │
│  │  Key Card Turn Limit:    [4           ]                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  KEY CARDS                                              │    │
│  │                                                          │    │
│  │  Cards to track:                                        │    │
│  │  • Survival of the Fittest                   [Remove]   │    │
│  │  • Squee, Goblin Nabob                       [Remove]   │    │
│  │  • Counterspell                              [Remove]   │    │
│  │                                                          │    │
│  │  [+ Add Key Card]                                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  IDEAL SETUPS                                           │    │
│  │                                                          │    │
│  │  Setup: Survival Engine                      [Edit] [×] │    │
│  │  • Requires: Survival of the Fittest                    │    │
│  │  • Colors: G                                            │    │
│  │  • Turn limit: 4                                        │    │
│  │  • In play: Survival of the Fittest                     │    │
│  │  • Creature in hand: Yes                                │    │
│  │                                                          │    │
│  │  [+ Add Setup]                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  [Cancel]                                            [Save]      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15. Mobile View (Responsive)

```
┌────────────────────────┐
│  ≡  MTG Madness        │
│     👤 brian ▼         │
├────────────────────────┤
│                        │
│  My Decks              │
│                        │
│  ┌──────────────────┐  │
│  │ 🎴 Madness v4    │  │
│  │                  │  │
│  │ 60 cards         │  │
│  │ 2h ago           │  │
│  │                  │  │
│  │ [Edit][Simulate] │  │
│  └──────────────────┘  │
│                        │
│  ┌──────────────────┐  │
│  │ 🎴 Madness v3    │  │
│  │                  │  │
│  │ 60 cards         │  │
│  │ 3d ago           │  │
│  │                  │  │
│  │ [Edit][Simulate] │  │
│  └──────────────────┘  │
│                        │
│  [+ New Deck]          │
│                        │
└────────────────────────┘

Mobile navigation:
- Hamburger menu (≡)
- Tap cards for actions
- Swipe between tabs
- Responsive tables (scroll)
- Touch-friendly buttons
```

---

## Interaction Patterns

### Loading States
```
┌────────────────────────┐
│     ⏳ Loading...       │
│   ○ ○ ○ ○ ○ (spinner) │
└────────────────────────┘
```

### Empty States
```
┌────────────────────────────────┐
│     📂 No decks yet            │
│                                │
│  Create your first deck to     │
│  start running simulations     │
│                                │
│     [+ Create Deck]            │
└────────────────────────────────┘
```

### Error States
```
┌────────────────────────────────┐
│     ⚠️ Error                    │
│                                │
│  Failed to load simulation     │
│  results. Please try again.    │
│                                │
│     [Retry] [Go Back]          │
└────────────────────────────────┘
```

### Toasts/Notifications
```
┌────────────────────────────────┐
│ ✓ Deck saved successfully!  [×]│
└────────────────────────────────┘

┌────────────────────────────────┐
│ ⚠️ Simulation cancelled     [×]│
└────────────────────────────────┘

┌────────────────────────────────┐
│ ❌ Failed to save deck      [×]│
└────────────────────────────────┘
```

---

## Animation & Transitions

- **Page transitions**: Smooth fade (200ms)
- **Modal dialogs**: Slide up from bottom (300ms)
- **Progress bars**: Smooth animation with easing
- **Card hover**: Subtle lift and shadow (150ms)
- **Button clicks**: Scale down slightly (100ms)
- **Toasts**: Slide in from top (250ms)

---

## Accessibility

- ✓ Keyboard navigation (Tab, Enter, Esc)
- ✓ Screen reader support (ARIA labels)
- ✓ High contrast mode support
- ✓ Focus indicators on interactive elements
- ✓ Skip to main content link
- ✓ Alt text for all images/icons
- ✓ Proper heading hierarchy (H1, H2, H3)

---

## Conclusion

These wireframes provide a visual guide for implementing the MTG Madness Carlo web application. The design emphasizes:

1. **Clean data presentation** - Tables, charts, cards
2. **Real-time feedback** - Progress bars, live updates
3. **Easy navigation** - Clear tabs, breadcrumbs
4. **Responsive design** - Works on all devices
5. **Familiar patterns** - Similar to modern web apps

Use these as a starting point and iterate based on user feedback!

