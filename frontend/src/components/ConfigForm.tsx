/**
 * Configuration Form Component
 * Create and edit simulation configurations
 */

import { useState, useEffect } from 'react';
import {
  configsService,
  SimulationConfig,
  ConfigCreateData,
} from '../services/configs';

interface ConfigFormProps {
  config?: SimulationConfig | null;
  onSuccess: () => void;
  onCancel: () => void;
}

export function ConfigForm({ config, onSuccess, onCancel }: ConfigFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    default_runs: 1000,
    default_turns: 4,
    key_card_turn_limit: 4,
    key_cards: [] as string[],
    is_default: false,
  });

  const [mulliganStrategy, setMulliganStrategy] = useState({
    enabled: true,
    min_lands: 2,
    max_lands: 4,
    requires_creature: true,
    max_mulligans: 7,
  });

  const [idealSetups, setIdealSetups] = useState<any[]>([]);
  const [keyCardInput, setKeyCardInput] = useState('');

  // Load config data if editing
  useEffect(() => {
    if (config) {
      setFormData({
        name: config.name,
        description: config.description || '',
        default_runs: config.default_runs,
        default_turns: config.default_turns,
        key_card_turn_limit: config.key_card_turn_limit,
        key_cards: config.key_cards,
        is_default: config.is_default,
      });
      
      if (config.mulligan_strategy) {
        setMulliganStrategy(config.mulligan_strategy);
      }
      
      if (config.ideal_setups) {
        setIdealSetups(config.ideal_setups);
      }
    }
  }, [config]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const configData: ConfigCreateData = {
        ...formData,
        mulligan_strategy: mulliganStrategy,
        ideal_setups: idealSetups,
        sideboard_plans: {},
      };

      if (config) {
        // Update existing
        await configsService.updateConfig(config.id, configData);
      } else {
        // Create new
        await configsService.createConfig(configData);
      }

      onSuccess();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || 'Failed to save config'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : type === 'number' ? Number(value) : value,
    });
  };

  const handleMulliganChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value, type } = e.target;
    const checked = e.target.checked;
    setMulliganStrategy({
      ...mulliganStrategy,
      [name]: type === 'checkbox' ? checked : Number(value),
    });
  };

  const addKeyCard = () => {
    if (keyCardInput.trim() && !formData.key_cards.includes(keyCardInput.trim())) {
      setFormData({
        ...formData,
        key_cards: [...formData.key_cards, keyCardInput.trim()],
      });
      setKeyCardInput('');
    }
  };

  const removeKeyCard = (card: string) => {
    setFormData({
      ...formData,
      key_cards: formData.key_cards.filter((c) => c !== card),
    });
  };

  const addIdealSetup = () => {
    setIdealSetups([
      ...idealSetups,
      {
        name: 'New Setup',
        requires_cards: [],
        requires_in_play: [],
        requires_in_graveyard: [],
        requires_colors: [],
        requires_min_lands: 0,
        requires_any_creature_in_hand: false,
        turn_limit: 4,
      },
    ]);
  };

  const updateIdealSetup = (index: number, field: string, value: any) => {
    const updated = [...idealSetups];
    updated[index] = { ...updated[index], [field]: value };
    setIdealSetups(updated);
  };

  const removeIdealSetup = (index: number) => {
    setIdealSetups(idealSetups.filter((_, i) => i !== index));
  };

  return (
    <div className="max-w-4xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
        {config ? 'Edit Configuration' : 'New Configuration'}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Basic Information
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Configuration Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                placeholder="My Custom Configuration"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                placeholder="Description of this configuration..."
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_default"
                checked={formData.is_default}
                onChange={handleChange}
                className="mr-2"
              />
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Set as default configuration
              </label>
            </div>
          </div>
        </div>

        {/* Simulation Settings */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Simulation Settings
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Default Runs *
              </label>
              <input
                type="number"
                name="default_runs"
                value={formData.default_runs}
                onChange={handleChange}
                required
                min="100"
                max="10000"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Default Turns *
              </label>
              <input
                type="number"
                name="default_turns"
                value={formData.default_turns}
                onChange={handleChange}
                required
                min="1"
                max="10"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Key Card Turn Limit *
              </label>
              <input
                type="number"
                name="key_card_turn_limit"
                value={formData.key_card_turn_limit}
                onChange={handleChange}
                required
                min="1"
                max="10"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
              />
            </div>
          </div>
        </div>

        {/* Key Cards */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Key Cards
          </h3>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={keyCardInput}
              onChange={(e) => setKeyCardInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addKeyCard())}
              placeholder="Card name"
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
            />
            <button
              type="button"
              onClick={addKeyCard}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Add
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {formData.key_cards.map((card, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full"
              >
                {card}
                <button
                  type="button"
                  onClick={() => removeKeyCard(card)}
                  className="text-blue-600 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-100"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Mulligan Strategy */}
        <div className="border-b border-gray-200 dark:border-gray-700 pb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            Mulligan Strategy
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                name="enabled"
                checked={mulliganStrategy.enabled}
                onChange={handleMulliganChange}
                className="mr-2"
              />
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Enable Mulligan
              </label>
            </div>

            {mulliganStrategy.enabled && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Min Lands
                  </label>
                  <input
                    type="number"
                    name="min_lands"
                    value={mulliganStrategy.min_lands}
                    onChange={handleMulliganChange}
                    min="0"
                    max="7"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Max Lands
                  </label>
                  <input
                    type="number"
                    name="max_lands"
                    value={mulliganStrategy.max_lands}
                    onChange={handleMulliganChange}
                    min="0"
                    max="7"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Max Mulligans
                  </label>
                  <input
                    type="number"
                    name="max_mulligans"
                    value={mulliganStrategy.max_mulligans}
                    onChange={handleMulliganChange}
                    min="0"
                    max="7"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="requires_creature"
                    checked={mulliganStrategy.requires_creature}
                    onChange={handleMulliganChange}
                    className="mr-2"
                  />
                  <label className="text-sm text-gray-700 dark:text-gray-300">
                    Requires Creature
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Ideal Setups */}
        <div className="pb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Ideal Setups ({idealSetups.length})
            </h3>
            <button
              type="button"
              onClick={addIdealSetup}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
            >
              Add Setup
            </button>
          </div>

          <div className="space-y-4">
            {idealSetups.map((setup, idx) => (
              <div
                key={idx}
                className="p-4 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900"
              >
                <div className="flex items-start justify-between mb-4">
                  <input
                    type="text"
                    value={setup.name}
                    onChange={(e) => updateIdealSetup(idx, 'name', e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    placeholder="Setup name"
                  />
                  <button
                    type="button"
                    onClick={() => removeIdealSetup(idx)}
                    className="ml-2 px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                  >
                    Remove
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Turn Limit
                    </label>
                    <input
                      type="number"
                      value={setup.turn_limit}
                      onChange={(e) => updateIdealSetup(idx, 'turn_limit', Number(e.target.value))}
                      min="1"
                      max="10"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Min Lands
                    </label>
                    <input
                      type="number"
                      value={setup.requires_min_lands || 0}
                      onChange={(e) => updateIdealSetup(idx, 'requires_min_lands', Number(e.target.value))}
                      min="0"
                      max="10"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                    />
                  </div>
                </div>

                <div className="mt-2 flex items-center">
                  <input
                    type="checkbox"
                    checked={setup.requires_any_creature_in_hand || false}
                    onChange={(e) => updateIdealSetup(idx, 'requires_any_creature_in_hand', e.target.checked)}
                    className="mr-2"
                  />
                  <label className="text-sm text-gray-700 dark:text-gray-300">
                    Requires creature in hand
                  </label>
                </div>
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-200 rounded">
            {error}
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Saving...' : config ? 'Update Configuration' : 'Create Configuration'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

