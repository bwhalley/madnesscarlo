/**
 * Simulation Results Component
 * Displays detailed simulation results with statistics and charts
 */

import { Simulation } from '../services/simulations';
import { ExportToSheetsButton } from './ExportToSheetsButton';

interface SimulationResultsProps {
  simulation: Simulation;
}

export function SimulationResults({ simulation }: SimulationResultsProps) {
  if (!simulation) {
    return (
      <div className="p-6 text-center bg-gray-50 rounded-lg">
        <p className="text-gray-500">Select a simulation to view results</p>
      </div>
    );
  }

  if (simulation.status === 'pending') {
    return (
      <div className="p-6 text-center">
        <div className="inline-block p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 font-medium">⏳ Simulation Pending</p>
          <p className="text-sm text-yellow-600 mt-2">This simulation is waiting to start...</p>
        </div>
      </div>
    );
  }

  if (simulation.status === 'running') {
    return (
      <div className="p-6 text-center">
        <div className="inline-block p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-800 font-medium mb-3">▶️ Simulation Running</p>
          <div className="w-64 bg-gray-200 rounded-full h-3 mb-2">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${simulation.progress}%` }}
            />
          </div>
          <p className="text-sm text-blue-600">{simulation.progress}% complete</p>
          <p className="text-xs text-blue-500 mt-3">This usually takes a few seconds...</p>
        </div>
      </div>
    );
  }

  if (simulation.status === 'failed') {
    return (
      <div className="p-6">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">❌ Simulation Failed</p>
          <p className="text-sm text-red-600 mt-2">
            {simulation.error_message || 'An unknown error occurred'}
          </p>
        </div>
      </div>
    );
  }

  if (simulation.status === 'cancelled') {
    return (
      <div className="p-6">
        <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-gray-800 font-medium">🚫 Simulation Cancelled</p>
          <p className="text-sm text-gray-600 mt-2">This simulation was cancelled before completion.</p>
        </div>
      </div>
    );
  }

  // Simulation completed - show results
  const results = simulation.results || {};
  const summary = results.summary || {};
  const cardStats = results.card_stats || [];
  const keyCardStats = results.key_card_stats || [];
  const setupStats = results.setup_stats || [];
  const mulliganStats = results.mulligan_stats || [];
  const graveyardStats = results.graveyard_stats || [];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-green-900">✅ Simulation Complete</h2>
            <p className="text-sm text-green-700 mt-1">
              Completed on {new Date(simulation.completed_at!).toLocaleString()}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-green-700">Runs: {simulation.runs.toLocaleString()}</p>
            <p className="text-sm text-green-700">Turns: {simulation.turns}</p>
          </div>
        </div>
        
        {/* Export to Sheets Button */}
        <div className="border-t border-green-200 pt-4">
          <ExportToSheetsButton
            simulationId={simulation.id}
            simulationName={`Simulation-${new Date(simulation.completed_at!).toLocaleDateString()}`}
          />
        </div>
      </div>

      {/* Summary Statistics */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold mb-4">📊 Summary Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <StatCard
            label="Avg Lands in Play"
            value={summary.average_lands_in_play?.toFixed(2) || '0'}
          />
          <StatCard
            label="Avg Cards Seen"
            value={summary.average_cards_seen?.toFixed(2) || '0'}
          />
          <StatCard
            label="Avg Mulligans"
            value={summary.average_mulligans?.toFixed(2) || '0'}
          />
          <StatCard
            label="0 Mulligan %"
            value={`${summary.games_with_0_mulligans_percentage?.toFixed(1) || '0'}%`}
          />
          <StatCard
            label="Avg Graveyard Size"
            value={summary.average_graveyard_size?.toFixed(2) || '0'}
          />
          <StatCard
            label="Total Madness Casts"
            value={summary.total_madness_casts || '0'}
          />
        </div>
      </div>

      {/* Key Cards */}
      {keyCardStats.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">🎯 Key Card Statistics</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Card</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Seen %</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {keyCardStats.map((stat: any, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">{stat.card}</td>
                    <td className="px-4 py-3 text-right">
                      <span className={getPercentageColor(stat.seen_percentage)}>
                        {stat.seen_percentage.toFixed(1)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Ideal Setups */}
      {setupStats.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">✨ Ideal Setup Success Rates</h3>
          <div className="space-y-3">
            {setupStats.map((stat: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span className="font-medium">{stat.setup_name}</span>
                <div className="flex items-center gap-3">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${Math.min(100, stat.success_percentage)}%` }}
                    />
                  </div>
                  <span className={`font-bold ${getPercentageColor(stat.success_percentage)}`}>
                    {stat.success_percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mulligan Distribution */}
      {mulliganStats.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">🔄 Mulligan Distribution</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Mulligans</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Games</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Percentage</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {mulliganStats.map((stat: any, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">{stat.mulligan_count}</td>
                    <td className="px-4 py-3 text-right">{stat.games.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right">{stat.percentage.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Card Statistics */}
      {cardStats.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">🎴 Card Statistics</h3>
          <p className="text-sm text-gray-600 mb-4">Top cards by seen percentage</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Card</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Seen %</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Cast %</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {cardStats
                  .sort((a: any, b: any) => b.seen_percentage - a.seen_percentage)
                  .slice(0, 20)
                  .map((stat: any, index: number) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3">{stat.card}</td>
                      <td className="px-4 py-3 text-right">{stat.seen_percentage.toFixed(1)}%</td>
                      <td className="px-4 py-3 text-right">{stat.cast_percentage.toFixed(1)}%</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Graveyard Statistics */}
      {graveyardStats.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold mb-4">🪦 Graveyard Statistics</h3>
          <p className="text-sm text-gray-600 mb-4">Average cards in graveyard</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Card</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Avg Count</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">%</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {graveyardStats.slice(0, 15).map((stat: any, index: number) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">{stat.card}</td>
                    <td className="px-4 py-3 text-right">{stat.avg_in_graveyard.toFixed(2)}</td>
                    <td className="px-4 py-3 text-right">{stat.percentage.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// Helper Components
function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <p className="text-xs text-gray-600 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}

function getPercentageColor(percentage: number): string {
  if (percentage >= 75) return 'text-green-600 font-bold';
  if (percentage >= 50) return 'text-blue-600 font-semibold';
  if (percentage >= 25) return 'text-yellow-600';
  return 'text-gray-600';
}

