/**
 * Simulations List Component
 * Displays all user's simulations with status
 */

import { useState, useEffect } from 'react';
import { simulationsService, Simulation } from '../services/simulations';

interface SimulationsListProps {
  onSelectSimulation: (simulation: Simulation) => void;
  refreshTrigger?: number;
}

export function SimulationsList({ onSelectSimulation, refreshTrigger }: SimulationsListProps) {
  const [simulations, setSimulations] = useState<Simulation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    loadSimulations();
  }, [refreshTrigger]);

  const loadSimulations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await simulationsService.getSimulations();
      setSimulations(response.simulations);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load simulations');
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (simulation: Simulation) => {
    setSelectedId(simulation.id);
    onSelectSimulation(simulation);
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this simulation?')) {
      return;
    }

    try {
      await simulationsService.deleteSimulation(id);
      setSimulations(simulations.filter((sim) => sim.id !== id));
      if (selectedId === id) {
        setSelectedId(null);
      }
    } catch (err: any) {
      alert('Failed to delete simulation: ' + (err.response?.data?.detail || err.message));
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { bg: string; text: string; icon: string }> = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: '⏳' },
      running: { bg: 'bg-blue-100', text: 'text-blue-800', icon: '▶️' },
      completed: { bg: 'bg-green-100', text: 'text-green-800', icon: '✅' },
      failed: { bg: 'bg-red-100', text: 'text-red-800', icon: '❌' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', icon: '🚫' },
    };

    const badge = badges[status] || badges.pending;
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
        {badge.icon} {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-600 dark:text-gray-400">Loading simulations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 rounded">
          {error}
        </div>
        <button
          onClick={loadSimulations}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (simulations.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg m-6">
        <p className="text-gray-600 dark:text-gray-400 mb-4">No simulations yet.</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Go to the "Run Simulation" tab to start your first simulation!
        </p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">My Simulations ({simulations.length})</h2>
        <button
          onClick={loadSimulations}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
        >
          🔄 Refresh
        </button>
      </div>

      <div className="space-y-4">
        {simulations.map((simulation) => (
          <div
            key={simulation.id}
            className={`border rounded-lg p-4 cursor-pointer transition-all ${
              selectedId === simulation.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400 bg-white'
            }`}
            onClick={() => handleSelect(simulation)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  {getStatusBadge(simulation.status)}
                  {simulation.status === 'running' && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${simulation.progress}%` }}
                        />
                      </div>
                      <span>{simulation.progress}%</span>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Runs:</span>
                    <span className="ml-2 font-medium">{simulation.runs.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Turns:</span>
                    <span className="ml-2 font-medium">{simulation.turns}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Created:</span>
                    <span className="ml-2 font-medium">
                      {new Date(simulation.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {simulation.completed_at && (
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Completed:</span>
                      <span className="ml-2 font-medium">
                        {new Date(simulation.completed_at).toLocaleTimeString()}
                      </span>
                    </div>
                  )}
                </div>

                {simulation.error_message && (
                  <div className="mt-2 text-sm text-red-600">
                    Error: {simulation.error_message}
                  </div>
                )}
              </div>

              <button
                onClick={(e) => handleDelete(simulation.id, e)}
                className="ml-4 text-red-600 hover:text-red-800 dark:text-red-200 text-sm"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

