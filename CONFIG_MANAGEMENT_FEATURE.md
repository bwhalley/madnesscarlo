# Configuration Management Feature

**Branch**: `feature/config-management`  
**Date**: October 28, 2025  
**Status**: ✅ Complete - Ready for Testing

## Overview

This feature adds a complete UI for users to create, view, edit, duplicate, and delete simulation configurations. Previously, configurations were only manageable via direct database manipulation or JSON files. Now users can:

1. **View all their configurations** (plus public/default ones)
2. **Duplicate any configuration** to use as a starting template
3. **Edit configurations** with a comprehensive form
4. **Delete their own configurations**
5. **Set a configuration as their default**

## Technical Implementation

### Backend Changes

#### New Endpoint: `POST /api/configs/{config_id}/duplicate`

**Location**: `/Users/brian/madnesscarlo/backend/app/api/simulation_configs.py`

Creates a copy of an existing configuration (user's own or public) with the suffix " (Copy)" added to the name. The duplicate is owned by the current user and is not set as default or public.

**Request**: None (config_id in URL)  
**Response**: The newly created configuration

**Example**:
```bash
curl -X POST http://localhost:8000/api/configs/{config_id}/duplicate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Changes

#### 1. Enhanced Configs Service

**Location**: `/Users/brian/madnesscarlo/frontend/src/services/configs.ts`

**New Methods**:
- `createConfig(data: ConfigCreateData)` - Create a new configuration
- `updateConfig(id: string, data: ConfigUpdateData)` - Update an existing configuration
- `deleteConfig(id: string)` - Delete a configuration
- `duplicateConfig(id: string)` - Duplicate a configuration
- `setDefaultConfig(id: string)` - Set a configuration as default

**New Types**:
- `ConfigCreateData` - Data structure for creating configurations
- `ConfigUpdateData` - Partial data structure for updates

#### 2. ConfigList Component

**Location**: `/Users/brian/madnesscarlo/frontend/src/components/ConfigList.tsx`

A comprehensive list view showing all available configurations with:

**Features**:
- Card-based layout with configuration cards
- Shows configuration metadata (runs, turns, key cards count, ideal setups count)
- Visual indicators for DEFAULT and PUBLIC configs
- Actions per card: Edit, Duplicate, Set Default, Delete
- Detail panel on the right showing full configuration details
- Dark mode support

**User Actions**:
- Click a card to view its details
- Edit button - Opens the configuration in edit mode
- Duplicate button - Creates a copy immediately
- Set Default button - Makes this config the user's default
- Delete button - Removes the configuration (with confirmation)

#### 3. ConfigForm Component

**Location**: `/Users/brian/madnesscarlo/frontend/src/components/ConfigForm.tsx`

A comprehensive form for creating and editing configurations.

**Form Sections**:

1. **Basic Information**
   - Configuration Name (required)
   - Description (optional)
   - Set as default checkbox

2. **Simulation Settings**
   - Default Runs (100-10,000)
   - Default Turns (1-10)
   - Key Card Turn Limit (1-10)

3. **Key Cards**
   - Add/remove key cards
   - Visual tag display
   - Press Enter to add

4. **Mulligan Strategy**
   - Enable/disable checkbox
   - Min Lands (0-7)
   - Max Lands (0-7)
   - Max Mulligans (0-7)
   - Requires Creature checkbox

5. **Ideal Setups**
   - Dynamic list of setups
   - Add/remove setups
   - Per setup:
     - Setup name
     - Turn limit
     - Min lands
     - Requires creature in hand checkbox

**Validation**:
- All required fields validated
- Numeric bounds enforced
- Form state managed with React hooks

**Dark Mode**: Fully supported with appropriate color classes

#### 4. ConfigManagement Component

**Location**: `/Users/brian/madnesscarlo/frontend/src/components/ConfigManagement.tsx`

Orchestration component that manages the view state between list and form.

**Features**:
- Switches between list and form views
- Handles creation (new config) and editing flows
- Manages refresh triggers to update the list after changes
- Provides "New Configuration" button

#### 5. App.tsx Integration

**Location**: `/Users/brian/madnesscarlo/frontend/src/App.tsx`

**Changes**:
- Added `'configurations'` to the `Tab` type
- Imported `ConfigManagement` component
- Added "⚙️ Configurations" tab button in the navigation
- Added route for `activeTab === 'configurations'` rendering `<ConfigManagement />`

## User Workflow

### Creating a New Configuration

1. Navigate to "⚙️ Configurations" tab
2. Click "New Configuration" button
3. Fill out the form:
   - Enter a name and description
   - Set simulation parameters (runs, turns)
   - Add key cards to track
   - Configure mulligan strategy
   - Define ideal setups
4. Click "Create Configuration"
5. Returns to list view with new config visible

### Duplicating an Existing Configuration

1. Navigate to "⚙️ Configurations" tab
2. Find the configuration to duplicate (can be your own or a public one)
3. Click "Duplicate" button on the card
4. A new configuration is created with " (Copy)" suffix
5. Edit the duplicated configuration to customize it

### Editing a Configuration

1. Navigate to "⚙️ Configurations" tab
2. Find the configuration to edit (must be your own)
3. Click "Edit" button on the card
4. Make desired changes in the form
5. Click "Update Configuration"
6. Returns to list view with updated config

### Setting a Default Configuration

1. Navigate to "⚙️ Configurations" tab
2. Find the configuration to set as default
3. Click "Set Default" button
4. The DEFAULT badge appears on the card
5. This configuration will be selected by default in "Run Simulation"

### Deleting a Configuration

1. Navigate to "⚙️ Configurations" tab
2. Find the configuration to delete (must be your own, not public)
3. Click "Delete" button on the card
4. Confirm the deletion in the prompt
5. Configuration is removed from the list

## Database Schema

No database schema changes were required. The existing `simulation_configs` table already supports all necessary fields:

```sql
CREATE TABLE simulation_configs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR NOT NULL,
    description TEXT,
    default_runs INTEGER,
    default_turns INTEGER,
    key_card_turn_limit INTEGER,
    key_cards TEXT[],
    mulligan_strategy JSONB,
    ideal_setups JSONB,
    sideboard_plans JSONB,
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## API Endpoints Summary

All endpoints require authentication (`Authorization: Bearer <token>`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/configs/` | List all configs (user's + public) |
| GET | `/api/configs/default` | Get the default config |
| GET | `/api/configs/{id}` | Get a specific config |
| POST | `/api/configs/` | Create a new config |
| PUT | `/api/configs/{id}` | Update a config |
| DELETE | `/api/configs/{id}` | Delete a config |
| POST | `/api/configs/{id}/duplicate` | Duplicate a config |
| POST | `/api/configs/{id}/set-default` | Set as default |

## Design Decisions

### 1. Duplicate vs. Template System

**Chosen**: Duplicate existing configs  
**Rationale**: Simpler UX. Users can duplicate the default configuration or any other config and modify it. This is more intuitive than a separate template system.

### 2. Form Complexity vs. JSON Editor

**Chosen**: Structured form with specific fields  
**Rationale**: More user-friendly for non-technical users. Power users who need full control can still use the API directly or request features.

### 3. Simplified Ideal Setups

**Form Includes**:
- Setup name
- Turn limit
- Min lands
- Requires creature checkbox

**Not Included in Form** (uses defaults from original config):
- `requires_cards` array
- `requires_in_play` array
- `requires_in_graveyard` array
- `requires_colors` array

**Rationale**: These advanced fields require card knowledge and are better suited for power users. The simplified form covers 80% of use cases. Future enhancement could add an "Advanced" toggle.

### 4. Per-User Configurations

**Permissions**:
- Users can view: Their own configs + Public configs
- Users can edit/delete: Only their own configs
- Users cannot modify: Public configs (but can duplicate them)

**Rationale**: Allows for shared default configurations while giving users full control over their own setups.

## Testing Checklist

- [ ] Navigate to Configurations tab
- [ ] Verify default configuration is visible and marked as DEFAULT
- [ ] Click "New Configuration" and create a config
- [ ] Verify the new config appears in the list
- [ ] Edit the newly created configuration
- [ ] Verify changes are saved
- [ ] Duplicate the default configuration
- [ ] Verify the copy appears with " (Copy)" suffix
- [ ] Set a non-default config as default
- [ ] Verify DEFAULT badge moves to the new config
- [ ] Delete a user-created configuration
- [ ] Verify it's removed from the list
- [ ] Attempt to delete a public configuration (should not be possible)
- [ ] Test in dark mode - verify all components render correctly
- [ ] Run a simulation using a custom configuration
- [ ] Verify the custom config's parameters are applied

## Future Enhancements

1. **Advanced Ideal Setups Editor**
   - Full UI for `requires_cards`, `requires_in_play`, etc.
   - Card autocomplete from deck
   - Visual builder for conditions

2. **Configuration Templates**
   - Pre-built templates for common strategies (Aggro, Control, Combo)
   - Import/export configurations as JSON

3. **Configuration Sharing**
   - Share a link to a configuration
   - Make user configs public
   - Copy other users' public configs

4. **Configuration History**
   - Track changes to configurations
   - Revert to previous versions
   - Compare versions side-by-side

5. **Bulk Actions**
   - Select multiple configurations
   - Delete multiple at once
   - Apply settings to multiple configs

6. **Configuration Analytics**
   - Show which configs produce the best results
   - Track usage frequency
   - Suggest optimizations based on simulation data

## Related Files

### Backend
- `/Users/brian/madnesscarlo/backend/app/api/simulation_configs.py` - API endpoints
- `/Users/brian/madnesscarlo/backend/app/models/simulation_config.py` - Database model
- `/Users/brian/madnesscarlo/backend/app/schemas/simulation_config.py` - Pydantic schemas

### Frontend
- `/Users/brian/madnesscarlo/frontend/src/components/ConfigList.tsx` - List component
- `/Users/brian/madnesscarlo/frontend/src/components/ConfigForm.tsx` - Form component
- `/Users/brian/madnesscarlo/frontend/src/components/ConfigManagement.tsx` - Orchestration
- `/Users/brian/madnesscarlo/frontend/src/services/configs.ts` - API service
- `/Users/brian/madnesscarlo/frontend/src/App.tsx` - Main app integration

## Notes

- All components fully support dark mode
- Forms include client-side validation
- Backend includes permission checks to prevent unauthorized modifications
- Configuration duplication preserves all settings including complex nested structures
- The default configuration from `simulation_config.json` serves as the template for new users

---

**Ready for Testing**: All code is complete and linter-verified. Ready for user acceptance testing.

