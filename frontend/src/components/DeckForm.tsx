/**
 * Deck Creation Form Component
 */

import { useState } from 'react';
import { decksService, CreateDeckData, CardInDeck } from '../services/decks';

interface DeckFormProps {
  onSuccess: () => void;
}

export function DeckForm({ onSuccess }: DeckFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [deckName, setDeckName] = useState('');
  const [deckDescription, setDeckDescription] = useState('');
  const [cardInput, setCardInput] = useState('');
  const [cards, setCards] = useState<CardInDeck[]>([]);

  const parseCardInput = () => {
    const lines = cardInput.trim().split('\n');
    const parsedCards: CardInDeck[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;

      // Parse format like "4 Lightning Bolt" or "4x Lightning Bolt"
      const match = trimmed.match(/^(\d+)x?\s+(.+)$/);
      if (match) {
        const quantity = parseInt(match[1], 10);
        const name = match[2].trim();
        parsedCards.push({ name, quantity });
      }
    }

    return parsedCards;
  };

  const handleAddCards = () => {
    const newCards = parseCardInput();
    if (newCards.length === 0) {
      setError('No valid cards found. Use format like "4 Lightning Bolt"');
      return;
    }
    setCards([...cards, ...newCards]);
    setCardInput('');
    setError(null);
  };

  const handleRemoveCard = (index: number) => {
    setCards(cards.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (cards.length === 0) {
      setError('Please add at least one card to your deck');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const deckData: CreateDeckData = {
        name: deckName,
        description: deckDescription || undefined,
        cards: cards,
      };

      await decksService.createDeck(deckData);
      setSuccess('Deck created successfully!');
      
      // Reset form
      setDeckName('');
      setDeckDescription('');
      setCards([]);
      setCardInput('');
      
      setTimeout(() => {
        onSuccess();
      }, 500);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create deck');
    } finally {
      setLoading(false);
    }
  };

  const totalCards = cards.reduce((sum, card) => sum + card.quantity, 0);

  return (
    <div className="max-w-2xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Create New Deck</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Deck Name *
          </label>
          <input
            type="text"
            value={deckName}
            onChange={(e) => setDeckName(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="My Awesome Deck"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            value={deckDescription}
            onChange={(e) => setDeckDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Describe your deck strategy..."
            rows={3}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Add Cards
          </label>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
            Enter cards one per line in format: "4 Lightning Bolt" or "4x Mountain"
          </p>
          <textarea
            value={cardInput}
            onChange={(e) => setCardInput(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            placeholder="4 Lightning Bolt&#10;20 Mountain&#10;4 Lava Spike"
            rows={5}
          />
          <button
            type="button"
            onClick={handleAddCards}
            className="mt-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
          >
            Add These Cards
          </button>
        </div>

        {cards.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Current Decklist ({totalCards} cards)
            </h3>
            <div className="border border-gray-300 dark:border-gray-600 rounded-md p-3 max-h-64 overflow-y-auto bg-gray-50 dark:bg-gray-900">
              {cards.map((card, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-1 hover:bg-gray-100 dark:bg-gray-700 px-2 rounded"
                >
                  <span className="font-mono text-sm">
                    {card.quantity}x {card.name}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleRemoveCard(index)}
                    className="text-red-600 hover:text-red-800 dark:text-red-200 text-sm"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-100 dark:bg-green-900 border border-green-400 text-green-700 rounded">
            {success}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || cards.length === 0}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Creating Deck...' : 'Create Deck'}
        </button>
      </form>
    </div>
  );
}

