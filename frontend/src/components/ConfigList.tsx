/**
 * Configuration List Component
 * Displays all user's configs with management actions
 */

import { useState, useEffect } from 'react';
import {
  configsService,
  SimulationConfig,
} from '../services/configs';

interface ConfigListProps {
  onEdit: (config: SimulationConfig) => void;
  onDuplicate: (config: SimulationConfig) => void;
}

export function ConfigList({ onEdit, onDuplicate }: ConfigListProps) {
  const [configs, setConfigs] = useState<SimulationConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedConfig, setSelectedConfig] = useState<SimulationConfig | null>(null);

  const loadConfigs = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await configsService.getConfigs();
      setConfigs(response.configs);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || 'Failed to load configs'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfigs();
  }, []);

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) {
      return;
    }

    try {
      await configsService.deleteConfig(id);
      setConfigs(configs.filter((config) => config.id !== id));
      if (selectedConfig?.id === id) {
        setSelectedConfig(null);
      }
    } catch (err: any) {
      alert(
        'Failed to delete config: ' +
          (err.response?.data?.detail || err.message)
      );
    }
  };

  const handleDuplicate = async (config: SimulationConfig) => {
    try {
      const newConfig = await configsService.duplicateConfig(config.id);
      setConfigs([newConfig, ...configs]);
      onDuplicate(newConfig);
    } catch (err: any) {
      alert(
        'Failed to duplicate config: ' +
          (err.response?.data?.detail || err.message)
      );
    }
  };

  const handleSetDefault = async (id: string) => {
    try {
      const updatedConfig = await configsService.setDefaultConfig(id);
      // Update the configs list to reflect the new default
      setConfigs(
        configs.map((config) =>
          config.id === id
            ? { ...config, is_default: true }
            : { ...config, is_default: false }
        )
      );
    } catch (err: any) {
      alert(
        'Failed to set default: ' + (err.response?.data?.detail || err.message)
      );
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto mt-8 p-6 text-center">
        <p className="text-gray-600 dark:text-gray-400">Loading configurations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto mt-8 p-6">
        <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-200 rounded">
          {error}
        </div>
        <button
          onClick={loadConfigs}
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Simulation Configurations ({configs.length})
        </h2>
        <button
          onClick={loadConfigs}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          Refresh
        </button>
      </div>

      {configs.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg">
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            You haven't created any configurations yet.
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Duplicate the default configuration to get started!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Config Cards */}
          <div className="space-y-4">
            {configs.map((config) => (
              <div
                key={config.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedConfig?.id === config.id
                    ? 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 bg-white dark:bg-gray-800'
                }`}
                onClick={() => setSelectedConfig(config)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-lg text-gray-900 dark:text-white">
                        {config.name}
                      </h3>
                      {config.is_default && (
                        <span className="px-2 py-1 text-xs font-semibold bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                          DEFAULT
                        </span>
                      )}
                      {config.is_public && (
                        <span className="px-2 py-1 text-xs font-semibold bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                          PUBLIC
                        </span>
                      )}
                    </div>
                    {config.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {config.description}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
                      <span>{config.default_runs} runs</span>
                      <span>{config.default_turns} turns</span>
                      <span>{config.key_cards.length} key cards</span>
                      <span>{config.ideal_setups.length} ideal setups</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      Created: {new Date(config.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="ml-4 flex flex-col gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onEdit(config);
                      }}
                      className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 text-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDuplicate(config);
                      }}
                      className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300 text-sm"
                    >
                      Duplicate
                    </button>
                    {!config.is_default && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleSetDefault(config.id);
                        }}
                        className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300 text-sm"
                      >
                        Set Default
                      </button>
                    )}
                    {!config.is_public && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(config.id, config.name);
                        }}
                        className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Config Details */}
          <div className="lg:sticky lg:top-6 h-fit">
            {selectedConfig ? (
              <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-6 bg-white dark:bg-gray-800">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                  {selectedConfig.name}
                </h3>
                {selectedConfig.description && (
                  <p className="text-gray-700 dark:text-gray-300 mb-4">
                    {selectedConfig.description}
                  </p>
                )}

                <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                  <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">
                    Settings:
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    <strong>Runs:</strong> {selectedConfig.default_runs}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    <strong>Turns:</strong> {selectedConfig.default_turns}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    <strong>Key Card Turn Limit:</strong>{' '}
                    {selectedConfig.key_card_turn_limit}
                  </p>
                </div>

                <div className="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                  <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">
                    Key Cards ({selectedConfig.key_cards.length}):
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedConfig.key_cards.map((card, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded"
                      >
                        {card}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="font-semibold mb-2 text-gray-900 dark:text-white">
                    Ideal Setups ({selectedConfig.ideal_setups.length}):
                  </h4>
                  <div className="space-y-3">
                    {selectedConfig.ideal_setups.map((setup: any, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-gray-50 dark:bg-gray-900 rounded text-sm border border-gray-200 dark:border-gray-700"
                      >
                        <div className="font-semibold text-gray-900 dark:text-gray-100 mb-2">{setup.name}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                          <div><strong>Turn limit:</strong> {setup.turn_limit}</div>
                          {setup.requires_min_lands > 0 && (
                            <div><strong>Min lands:</strong> {setup.requires_min_lands}</div>
                          )}
                          {setup.requires_cards && setup.requires_cards.length > 0 && (
                            <div>
                              <strong>Required cards:</strong>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {setup.requires_cards.map((card: string, i: number) => (
                                  <span key={i} className="px-1.5 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-xs">
                                    {card}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {setup.requires_in_play && setup.requires_in_play.length > 0 && (
                            <div>
                              <strong>In play:</strong>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {setup.requires_in_play.map((card: string, i: number) => (
                                  <span key={i} className="px-1.5 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
                                    {card}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {setup.requires_in_graveyard && setup.requires_in_graveyard.length > 0 && (
                            <div>
                              <strong>In graveyard:</strong>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {setup.requires_in_graveyard.map((card: string, i: number) => (
                                  <span key={i} className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded text-xs">
                                    {card}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {setup.requires_colors && setup.requires_colors.length > 0 && (
                            <div>
                              <strong>Mana colors:</strong>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {setup.requires_colors.map((color: string, i: number) => (
                                  <span 
                                    key={i} 
                                    className={`px-1.5 py-0.5 rounded text-xs ${
                                      color === 'W' ? 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200' :
                                      color === 'U' ? 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200' :
                                      color === 'B' ? 'bg-gray-800 dark:bg-gray-700 text-white' :
                                      color === 'R' ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200' :
                                      color === 'G' ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' :
                                      'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
                                    }`}
                                  >
                                    {color === 'W' ? '⚪' : color === 'U' ? '🔵' : color === 'B' ? '⚫' : color === 'R' ? '🔴' : color === 'G' ? '🟢' : ''} {color}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {setup.requires_any_creature_in_hand && (
                            <div>✓ Requires creature in hand</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="border border-gray-300 dark:border-gray-600 rounded-lg p-6 bg-gray-50 dark:bg-gray-900 text-center">
                <p className="text-gray-500 dark:text-gray-400">
                  Select a configuration to view its details
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

