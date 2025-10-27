/**
 * Deck List Component
 * Displays all user's decks
 */

import { useState, useEffect } from 'react';
import { decksService, Deck } from '../services/decks';

export function DeckList() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null);

  const loadDecks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await decksService.getDecks();
      setDecks(response.decks);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load decks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDecks();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this deck?')) {
      return;
    }

    try {
      await decksService.deleteDeck(id);
      setDecks(decks.filter((deck) => deck.id !== id));
      if (selectedDeck?.id === id) {
        setSelectedDeck(null);
      }
    } catch (err: any) {
      alert('Failed to delete deck: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto mt-8 p-6 text-center">
        <p className="text-gray-600 dark:text-gray-400">Loading decks...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto mt-8 p-6">
        <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 rounded">
          {error}
        </div>
        <button
          onClick={loadDecks}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto mt-8 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">My Decks ({decks.length})</h2>
        <button
          onClick={loadDecks}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {decks.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <p className="text-gray-600 dark:text-gray-400 mb-4">You haven't created any decks yet.</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Switch to the "Create Deck" tab to build your first deck!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Deck Cards */}
          <div className="space-y-4">
            {decks.map((deck) => (
              <div
                key={deck.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedDeck?.id === deck.id
                    ? 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 bg-white dark:bg-gray-800'
                }`}
                onClick={() => setSelectedDeck(deck)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white">{deck.name}</h3>
                    {deck.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{deck.description}</p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                      <span>{deck.cards.length} unique cards</span>
                      <span>{deck.card_count || '0'} total cards</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      Created: {new Date(deck.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(deck.id);
                    }}
                    className="ml-4 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Deck Details */}
          <div className="lg:sticky lg:top-6 h-fit">
            {selectedDeck ? (
              <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-6 bg-white dark:bg-gray-800">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">{selectedDeck.name}</h3>
                {selectedDeck.description && (
                  <p className="text-gray-700 dark:text-gray-300 mb-4">{selectedDeck.description}</p>
                )}
                
                <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    <strong>Total Cards:</strong> {selectedDeck.card_count || '0'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    <strong>Unique Cards:</strong> {selectedDeck.cards.length}
                  </p>
                </div>

                <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">Decklist:</h4>
                <div className="max-h-96 overflow-y-auto bg-gray-50 dark:bg-gray-900 rounded p-3">
                  {selectedDeck.cards.map((card, index) => (
                    <div
                      key={index}
                      className="font-mono text-sm py-1 border-b border-gray-200 dark:border-gray-700 last:border-0 text-gray-900 dark:text-gray-100"
                    >
                      {card.quantity}x {card.name}
                      {card.type && (
                        <span className="text-gray-500 dark:text-gray-400 ml-2">({card.type})</span>
                      )}
                    </div>
                  ))}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    <strong>Deck ID:</strong> {selectedDeck.id}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    <strong>Created:</strong>{' '}
                    {new Date(selectedDeck.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ) : (
              <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-6 bg-gray-50 dark:bg-gray-900 text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  Select a deck to view its details
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

