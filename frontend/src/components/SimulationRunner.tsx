/**
 * Simulation Runner Component
 * Allows users to start new simulations
 */

import { useState, useEffect, useRef } from 'react';
import { decksService, Deck } from '../services/decks';
import { configsService, SimulationConfig } from '../services/configs';
import { simulationsService, CreateSimulationData } from '../services/simulations';
import { connectToSimulation, SimulationWebSocket, SimulationUpdate } from '../services/websocket';

interface SimulationRunnerProps {
  onSimulationStarted?: (simulationId: string) => void;
}

export function SimulationRunner({ onSimulationStarted }: SimulationRunnerProps) {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [configs, setConfigs] = useState<SimulationConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Progress tracking
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [isSimulating, setIsSimulating] = useState(false);
  const wsRef = useRef<SimulationWebSocket | null>(null);

  const [formData, setFormData] = useState({
    deck_id: '',
    config_id: '',
    runs: 1000,
    turns: 4,
  });

  useEffect(() => {
    loadData();
    
    // Cleanup WebSocket on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
        wsRef.current = null;
      }
    };
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [decksResponse, configsResponse] = await Promise.all([
        decksService.getDecks(),
        configsService.getConfigs(),
      ]);
      setDecks(decksResponse.decks);
      setConfigs(configsResponse.configs);

      // Auto-select first deck and config if available
      if (decksResponse.decks.length > 0 && !formData.deck_id) {
        setFormData((prev) => ({ ...prev, deck_id: decksResponse.decks[0].id }));
      }
      if (configsResponse.configs.length > 0 && !formData.config_id) {
        setFormData((prev) => ({ ...prev, config_id: configsResponse.configs[0].id }));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.deck_id) {
      setError('Please select a deck');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const simulationData: CreateSimulationData = {
        deck_id: formData.deck_id,
        runs: formData.runs,
        turns: formData.turns,
      };
      
      // Only include config_id if it's actually set
      if (formData.config_id) {
        simulationData.config_id = formData.config_id;
      }

      const simulation = await simulationsService.createSimulation(simulationData);
      
      // Connect to WebSocket for real-time updates
      setIsSimulating(true);
      setProgress(0);
      setProgressMessage('Connecting to simulation...');
      
      wsRef.current = connectToSimulation(simulation.id, (update: SimulationUpdate) => {
        console.log('📊 Simulation update:', update);
        
        if (update.type === 'progress') {
          setProgress(update.progress || 0);
          setProgressMessage(update.message || '');
        } else if (update.type === 'status') {
          setProgress(update.progress || 0);
          setProgressMessage(update.message || '');
        } else if (update.type === 'completed') {
          setProgress(100);
          setProgressMessage('Simulation completed!');
          setSuccess('Simulation completed successfully!');
          setIsSimulating(false);
          
          // Disconnect WebSocket
          if (wsRef.current) {
            wsRef.current.disconnect();
            wsRef.current = null;
          }
          
          // Notify parent
          if (onSimulationStarted) {
            onSimulationStarted(simulation.id);
          }
          
          // Reset after delay
          setTimeout(() => {
            setSuccess(null);
            setProgress(0);
            setProgressMessage('');
          }, 3000);
        } else if (update.type === 'error') {
          setError(update.error || 'Simulation failed');
          setIsSimulating(false);
          
          // Disconnect WebSocket
          if (wsRef.current) {
            wsRef.current.disconnect();
            wsRef.current = null;
          }
        }
      });
    } catch (err: any) {
      // Handle Pydantic validation errors (422)
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // Pydantic validation error format
          const errorMessages = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
          setError(`Validation error: ${errorMessages}`);
        } else if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError('Failed to start simulation');
        }
      } else {
        setError(err.message || 'Failed to start simulation');
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto mt-8 p-6 text-center">
        <p className="text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    );
  }

  if (decks.length === 0) {
    return (
      <div className="max-w-2xl mx-auto mt-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-2">No Decks Found</h3>
        <p className="text-yellow-700 mb-4">
          You need to create a deck before running simulations.
        </p>
        <p className="text-sm text-yellow-600">
          Go to the "Create Deck" tab to add your first deck.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Run Simulation</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Deck *
          </label>
          <select
            value={formData.deck_id}
            onChange={(e) => setFormData({ ...formData, deck_id: e.target.value })}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a deck --</option>
            {decks && decks.length > 0 ? (
              decks.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name} ({deck.card_count || deck.cards?.length || 0} cards)
                </option>
              ))
            ) : null}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Configuration (Optional)
          </label>
          <select
            value={formData.config_id}
            onChange={(e) => setFormData({ ...formData, config_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Select a configuration (optional) --</option>
            {configs && configs.length > 0 ? (
              configs.map((config) => (
                <option key={config.id} value={config.id}>
                  {config.name} ({config.default_runs} runs, {config.default_turns} turns)
                </option>
              ))
            ) : null}
          </select>
          {configs && configs.length === 0 && (
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              No configurations found. Using default settings.
            </p>
          )}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Number of Runs
            </label>
            <input
              type="number"
              min="100"
              max="100000"
              step="100"
              value={formData.runs}
              onChange={(e) => setFormData({ ...formData, runs: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              More runs = more accurate results
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Turns to Simulate
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={formData.turns}
              onChange={(e) => setFormData({ ...formData, turns: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Typically 4-6 turns
            </p>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-900 mb-2">📊 What This Does</h4>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>• Simulates {formData.runs.toLocaleString()} games with your deck</li>
            <li>• Tracks card draw rates and key card access</li>
            <li>• Evaluates ideal setup success rates</li>
            <li>• Analyzes mulligan patterns</li>
            <li>• Provides detailed statistics</li>
          </ul>
          <p className="text-xs text-blue-600 mt-2">
            Estimated time: ~{Math.ceil(formData.runs / 500)} seconds
          </p>
        </div>

        {/* Progress Bar */}
        {isSimulating && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="mb-2">
              <div className="flex justify-between text-sm font-medium text-blue-900 mb-1">
                <span>Simulation Progress</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-blue-200 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
            {progressMessage && (
              <p className="text-sm text-blue-700 mt-2 animate-pulse">
                {progressMessage}
              </p>
            )}
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
          disabled={submitting || !formData.deck_id}
          className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium text-lg"
        >
          {submitting ? '🚀 Starting Simulation...' : '🎲 Run Simulation'}
        </button>
      </form>

      <div className="mt-6 pt-6 border-t">
        <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
          Simulations run in the background. You can navigate away and check back later.
        </p>
      </div>
    </div>
  );
}

