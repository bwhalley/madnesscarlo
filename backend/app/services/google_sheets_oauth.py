"""
Google Sheets OAuth Export Service

Exports simulation results to Google Sheets using user's OAuth tokens.
Sheets are created in the USER'S Google Drive!
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class GoogleSheetsOAuthExporter:
    """
    Service for exporting simulations to Google Sheets using user's OAuth tokens.
    
    This creates spreadsheets in the user's own Google Drive, bypassing
    organization policies that would block service accounts!
    """
    
    def export_simulation(
        self,
        access_token: str,
        simulation_data: Dict[str, Any],
        deck_name: str,
        user_email: str = None
    ) -> Dict[str, str]:
        """
        Export simulation results to user's Google Drive.
        
        Args:
            access_token: User's Google OAuth access token
            simulation_data: Simulation results dictionary
            deck_name: Name of the deck
            user_email: User's email (optional, for title)
        
        Returns:
            Dictionary with spreadsheet_id and spreadsheet_url
        """
        try:
            # Create credentials from user's OAuth token
            credentials = Credentials(token=access_token)
            
            # Build Sheets API service with user's credentials
            sheets_service = build('sheets', 'v4', credentials=credentials)
            
            # Create spreadsheet title
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            title = f"MTG Simulation - {deck_name} - {timestamp}"
            
            logger.info(f"Creating spreadsheet: {title}")
            
            # Create spreadsheet with multiple tabs
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {'properties': {'title': 'Summary', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Card Statistics', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Key Cards', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Ideal Setups', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Opening Hands', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Mulligan Analysis', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Graveyard Stats', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Battlefield Stats', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Madness Casts', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Flashback Casts', 'gridProperties': {'frozenRowCount': 1}}},
                    {'properties': {'title': 'Tutored Cards', 'gridProperties': {'frozenRowCount': 1}}}
                ]
            }
            
            spreadsheet = sheets_service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,sheets.properties'
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            logger.info(f"Created spreadsheet with ID: {spreadsheet_id}")
            
            # DEBUG: Log the simulation data structure
            logger.info(f"📊 Simulation data keys: {list(simulation_data.keys())}")
            logger.info(f"📊 Summary data: {simulation_data.get('summary', {})}")
            if 'card_stats' in simulation_data:
                logger.info(f"📊 Card stats type: {type(simulation_data['card_stats'])}")
                if isinstance(simulation_data['card_stats'], list) and len(simulation_data['card_stats']) > 0:
                    logger.info(f"📊 First card stat: {simulation_data['card_stats'][0]}")
                elif isinstance(simulation_data['card_stats'], dict):
                    logger.info(f"📊 Card stats keys (first 5): {list(simulation_data['card_stats'].keys())[:5]}")
            
            # Get the actual sheet IDs (Google assigns them, not necessarily 0,1,2,3)
            sheet_ids = {}
            for sheet in spreadsheet.get('sheets', []):
                sheet_title = sheet['properties']['title']
                sheet_id = sheet['properties']['sheetId']
                sheet_ids[sheet_title] = sheet_id
                logger.info(f"Sheet '{sheet_title}' has ID: {sheet_id}")
            
            # Populate all tabs with data
            self._populate_summary(sheets_service, spreadsheet_id, simulation_data, deck_name)
            self._populate_card_statistics(sheets_service, spreadsheet_id, simulation_data)
            self._populate_key_cards(sheets_service, spreadsheet_id, simulation_data)
            self._populate_ideal_setups(sheets_service, spreadsheet_id, simulation_data)
            self._populate_opening_hands(sheets_service, spreadsheet_id, simulation_data)
            self._populate_mulligan(sheets_service, spreadsheet_id, simulation_data)
            self._populate_graveyard(sheets_service, spreadsheet_id, simulation_data)
            self._populate_battlefield(sheets_service, spreadsheet_id, simulation_data)
            self._populate_madness(sheets_service, spreadsheet_id, simulation_data)
            self._populate_flashback(sheets_service, spreadsheet_id, simulation_data)
            self._populate_tutored(sheets_service, spreadsheet_id, simulation_data)
            
            # Format the spreadsheet with correct sheet IDs
            self._format_spreadsheet(sheets_service, spreadsheet_id, sheet_ids)
            
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            logger.info(f"Successfully exported simulation to: {spreadsheet_url}")
            
            return {
                'spreadsheet_id': spreadsheet_id,
                'spreadsheet_url': spreadsheet_url,
                'message': f'Spreadsheet created in your Google Drive!'
            }
            
        except Exception as e:
            logger.error(f"Failed to export to Google Sheets: {e}")
            raise
    
    def _populate_summary(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any],
        deck_name: str
    ):
        """Populate Summary tab"""
        summary_data = data.get('summary', {})
        
        values = [
            ['MTG Madness Carlo - Simulation Results'],
            [''],
            ['Deck Name', deck_name],
            ['Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Runs', summary_data.get('simulations_run', 0)],
            ['Turns Simulated', summary_data.get('turns_simulated', 0)],
            [''],
            ['Key Statistics', ''],
            ['Average Lands in Play', summary_data.get('average_lands_in_play', 0)],
            ['Average Cards Seen', summary_data.get('average_cards_seen', 0)],
            ['Average Mulligans', summary_data.get('average_mulligans', 0)],
            ['Games with 0 Mulligans %', summary_data.get('games_with_0_mulligans_percentage', 0)],
            ['Average Graveyard Size', summary_data.get('average_graveyard_size', 0)],
            ['Average Creatures on Board', summary_data.get('average_creatures_on_board', 0)],
            ['Total Madness Casts', summary_data.get('total_madness_casts', 0)],
            ['Total Flashback Casts', summary_data.get('total_flashback_casts', 0)],
        ]
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Summary!A1',
            valueInputOption='RAW',
            body={'values': values}
        ).execute()
    
    def _populate_card_statistics(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Card Statistics tab"""
        card_stats = data.get('card_stats', [])
        
        # Header row
        values = [
            ['Card Name', 'Seen %', 'Cast %']
        ]
        
        # card_stats is a list of dicts with: card, seen_percentage, cast_percentage
        if isinstance(card_stats, list):
            # Sort by seen percentage (descending)
            sorted_cards = sorted(
                card_stats,
                key=lambda x: x.get('seen_percentage', 0) if isinstance(x, dict) else 0,
                reverse=True
            )
            
            for item in sorted_cards:
                if isinstance(item, dict):
                    card_name = item.get('card', 'Unknown')
                    seen_pct = item.get('seen_percentage', 0)
                    cast_pct = item.get('cast_percentage', 0)
                    
                    values.append([
                        card_name,
                        f"{seen_pct:.1f}%",
                        f"{cast_pct:.1f}%"
                    ])
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Card Statistics!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_key_cards(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Key Cards tab"""
        key_cards = data.get('key_card_stats', [])
        
        if not key_cards or len(key_cards) == 0:
            values = [['No key cards tracked in this simulation']]
        else:
            values = [
                ['Card Name', 'Seen %']
            ]
            
            # key_card_stats is a list of dicts with: card, seen_percentage
            if isinstance(key_cards, list):
                for item in sorted(key_cards, key=lambda x: x.get('seen_percentage', 0) if isinstance(x, dict) else 0, reverse=True):
                    if isinstance(item, dict):
                        card_name = item.get('card', 'Unknown')
                        seen_pct = item.get('seen_percentage', 0)
                        
                        values.append([
                            card_name,
                            f"{seen_pct:.1f}%"
                        ])
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Key Cards!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_ideal_setups(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Ideal Setups tab"""
        setup_stats = data.get('setup_stats', [])
        
        if not setup_stats or len(setup_stats) == 0:
            values = [['No ideal setups configured for this simulation']]
        else:
            values = [
                ['Setup Name', 'Success %']
            ]
            
            # setup_stats is a list of dicts with: setup_name, success_percentage
            if isinstance(setup_stats, list):
                for item in sorted(setup_stats, key=lambda x: x.get('success_percentage', 0) if isinstance(x, dict) else 0, reverse=True):
                    if isinstance(item, dict):
                        setup_name = item.get('setup_name', 'Unknown')
                        success_pct = item.get('success_percentage', 0)
                        
                        values.append([
                            setup_name,
                            f"{success_pct:.1f}%"
                        ])
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Ideal Setups!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_opening_hands(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Opening Hands tab"""
        opening_hands_stats = data.get('opening_hands_stats', [])
        
        if not opening_hands_stats or len(opening_hands_stats) == 0:
            values = [['No opening hand patterns found']]
        else:
            # Get all setup names for column headers
            setup_names = []
            if opening_hands_stats and len(opening_hands_stats) > 0:
                for pattern_data in opening_hands_stats:
                    if isinstance(pattern_data, dict):
                        setup_rates = pattern_data.get('setup_success_rates', {})
                        for setup_name in setup_rates.keys():
                            if setup_name not in setup_names:
                                setup_names.append(setup_name)
            
            setup_names = sorted(setup_names)
            
            # Build header row
            header = ['Pattern', 'Games', 'Median Mulligans', 'Avg Success %']
            header.extend([f"{name} %" for name in setup_names])
            values = [header]
            
            # opening_hands_stats is a list of dicts with: pattern, games, median_mulligans, 
            # setup_success_rates (dict), avg_success_percentage
            if isinstance(opening_hands_stats, list):
                for item in opening_hands_stats:
                    if isinstance(item, dict):
                        pattern = item.get('pattern', 'Unknown')
                        games = item.get('games', 0)
                        median_mulligans = item.get('median_mulligans', 0)
                        avg_success = item.get('avg_success_percentage', 0)
                        setup_rates = item.get('setup_success_rates', {})
                        
                        row = [
                            pattern,
                            games,
                            f"{median_mulligans:.1f}",
                            f"{avg_success:.1f}%"
                        ]
                        
                        # Add success rate for each setup (in same order as headers)
                        for setup_name in setup_names:
                            rate = setup_rates.get(setup_name, 0)
                            row.append(f"{rate:.1f}%")
                        
                        values.append(row)
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Opening Hands!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_mulligan(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Mulligan Analysis tab"""
        mulligan_stats = data.get('mulligan_stats', [])
        
        values = [
            ['Mulligan Count', 'Games', 'Percentage']
        ]
        
        # mulligan_stats is a list of dicts with: mulligan_count, games, percentage
        if isinstance(mulligan_stats, list):
            for item in mulligan_stats:
                if isinstance(item, dict):
                    mull_count = item.get('mulligan_count', 0)
                    games = item.get('games', 0)
                    percentage = item.get('percentage', 0)
                    
                    # Format the label
                    if mull_count == 0:
                        label = "No mulligans (7 cards)"
                    else:
                        hand_size = 7 - mull_count
                        label = f"{mull_count} mulligan(s) ({hand_size} cards)"
                    
                    values.append([
                        label,
                        games,
                        f"{percentage:.1f}%"
                    ])
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Mulligan Analysis!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_graveyard(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Graveyard Stats tab"""
        graveyard_stats = data.get('graveyard_stats', [])
        
        values = [
            ['Card', 'Avg in Graveyard', 'In Graveyard %']
        ]
        
        if isinstance(graveyard_stats, list):
            for item in graveyard_stats:
                if isinstance(item, dict):
                    card = item.get('card', 'Unknown')
                    avg = item.get('avg_in_graveyard', 0)
                    pct = item.get('percentage', 0)
                    
                    values.append([
                        card,
                        f"{avg:.2f}",
                        f"{pct:.1f}%"
                    ])
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Graveyard Stats!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_battlefield(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Battlefield Stats tab"""
        battlefield_stats = data.get('battlefield_stats', [])
        
        values = [
            ['Card', 'Avg on Battlefield', 'On Battlefield %']
        ]
        
        if isinstance(battlefield_stats, list):
            for item in battlefield_stats:
                if isinstance(item, dict):
                    card = item.get('card', 'Unknown')
                    avg = item.get('avg_on_battlefield', 0)
                    pct = item.get('percentage', 0)
                    
                    values.append([
                        card,
                        f"{avg:.2f}",
                        f"{pct:.1f}%"
                    ])
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Battlefield Stats!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_madness(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Madness Casts tab"""
        madness_stats = data.get('madness_stats', [])
        
        values = [
            ['Card', 'Madness Casts', 'Madness Cast %']
        ]
        
        if isinstance(madness_stats, list) and len(madness_stats) > 0:
            for item in madness_stats:
                if isinstance(item, dict):
                    card = item.get('card', 'Unknown')
                    casts = item.get('madness_casts', 0)
                    pct = item.get('percentage', 0)
                    
                    values.append([
                        card,
                        casts,
                        f"{pct:.1f}%"
                    ])
        else:
            values = [['No madness casts in this simulation']]
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Madness Casts!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_flashback(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Flashback Casts tab"""
        flashback_stats = data.get('flashback_stats', [])
        
        values = [
            ['Card', 'Flashback Casts', 'Flashback Cast %']
        ]
        
        if isinstance(flashback_stats, list) and len(flashback_stats) > 0:
            for item in flashback_stats:
                if isinstance(item, dict):
                    card = item.get('card', 'Unknown')
                    casts = item.get('flashback_casts', 0)
                    pct = item.get('percentage', 0)
                    
                    values.append([
                        card,
                        casts,
                        f"{pct:.1f}%"
                    ])
        else:
            values = [['No flashback casts in this simulation']]
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Flashback Casts!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _populate_tutored(
        self,
        sheets_service,
        spreadsheet_id: str,
        data: Dict[str, Any]
    ):
        """Populate Tutored Cards tab"""
        tutored_stats = data.get('tutored_stats', [])
        
        values = [
            ['Card', 'Times Tutored', 'Tutored %']
        ]
        
        if isinstance(tutored_stats, list) and len(tutored_stats) > 0:
            for item in tutored_stats:
                if isinstance(item, dict):
                    card = item.get('card', 'Unknown')
                    times = item.get('times_tutored', 0)
                    pct = item.get('percentage', 0)
                    
                    values.append([
                        card,
                        times,
                        f"{pct:.1f}%"
                    ])
        else:
            values = [['No tutored cards in this simulation']]
        
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Tutored Cards!A1',
            valueInputOption='USER_ENTERED',
            body={'values': values}
        ).execute()
    
    def _format_spreadsheet(self, sheets_service, spreadsheet_id: str, sheet_ids: Dict[str, int]):
        """Apply formatting to make the spreadsheet look nice"""
        requests = []
        
        # Get actual sheet IDs
        summary_id = sheet_ids.get('Summary')
        card_stats_id = sheet_ids.get('Card Statistics')
        key_cards_id = sheet_ids.get('Key Cards')
        setups_id = sheet_ids.get('Ideal Setups')
        opening_hands_id = sheet_ids.get('Opening Hands')
        mulligan_id = sheet_ids.get('Mulligan Analysis')
        graveyard_id = sheet_ids.get('Graveyard Stats')
        battlefield_id = sheet_ids.get('Battlefield Stats')
        madness_id = sheet_ids.get('Madness Casts')
        flashback_id = sheet_ids.get('Flashback Casts')
        tutored_id = sheet_ids.get('Tutored Cards')
        
        # Bold headers in Summary
        if summary_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': summary_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True, 'fontSize': 14}
                        }
                    },
                    'fields': 'userEnteredFormat.textFormat'
                }
            })
        
        # Bold headers in Card Statistics
        if card_stats_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': card_stats_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Key Cards
        if key_cards_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': key_cards_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Ideal Setups
        if setups_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': setups_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Opening Hands
        if opening_hands_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': opening_hands_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Mulligan
        if mulligan_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': mulligan_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Graveyard Stats
        if graveyard_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': graveyard_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Battlefield Stats
        if battlefield_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': battlefield_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Madness Casts
        if madness_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': madness_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Flashback Casts
        if flashback_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': flashback_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Bold headers in Tutored Cards
        if tutored_id is not None:
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': tutored_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            })
        
        # Auto-resize columns in all sheets
        for sheet_id in [summary_id, card_stats_id, key_cards_id, setups_id, mulligan_id, 
                         graveyard_id, battlefield_id, madness_id, flashback_id, tutored_id]:
            if sheet_id is not None:
                requests.append({
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 10
                        }
                    }
                })
        
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': requests}
        ).execute()


def get_sheets_oauth_exporter() -> GoogleSheetsOAuthExporter:
    """Get singleton instance of GoogleSheetsOAuthExporter"""
    return GoogleSheetsOAuthExporter()

