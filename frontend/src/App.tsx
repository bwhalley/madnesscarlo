/**
 * Main Application Component
 */

import { useState, useEffect } from 'react';
import { authService } from './services/auth';
import { AuthForm } from './components/AuthForm';
import { DeckForm } from './components/DeckForm';
import { DeckList } from './components/DeckList';
import { SimulationRunner } from './components/SimulationRunner';
import { SimulationsList } from './components/SimulationsList';
import { SimulationResults } from './components/SimulationResults';
import { DarkModeToggle } from './components/DarkModeToggle';
import './App.css';

type Tab = 'decks' | 'create' | 'simulations' | 'run-simulation' | 'profile';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('decks');
  const [user, setUser] = useState<any>(null);
  const [selectedSimulation, setSelectedSimulation] = useState<any>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    const authenticated = authService.isAuthenticated();
    setIsAuthenticated(authenticated);
    if (authenticated) {
      setUser(authService.getUser());
    }
  }, []);

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
    setUser(authService.getUser());
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setUser(null);
    setActiveTab('decks');
  };

  const handleDeckCreated = () => {
    setActiveTab('decks');
  };

  const handleSimulationStarted = (simulationId: string) => {
    // Refresh simulations list and switch to simulations tab
    setRefreshTrigger(prev => prev + 1);
    setActiveTab('simulations');
  };

  const handleSelectSimulation = (simulation: any) => {
    setSelectedSimulation(simulation);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          <div className="absolute top-4 right-4">
            <DarkModeToggle />
          </div>
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-2">
              ⚡ MTG Madness Carlo
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Monte Carlo Simulation for Magic: The Gathering Decks
            </p>
          </div>
          <AuthForm onSuccess={handleAuthSuccess} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
                ⚡ MTG Madness Carlo
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                Welcome back, {user?.full_name || user?.username}!
              </p>
            </div>
            <div className="flex items-center gap-3">
              <DarkModeToggle />
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="container mx-auto px-4">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('decks')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'decks'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              📚 My Decks
            </button>
            <button
              onClick={() => setActiveTab('create')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'create'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              ➕ Create Deck
            </button>
            <button
              onClick={() => setActiveTab('run-simulation')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'run-simulation'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              🎲 Run Simulation
            </button>
            <button
              onClick={() => setActiveTab('simulations')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'simulations'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              📊 Simulations
            </button>
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'profile'
                  ? 'border-blue-600 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              👤 Profile
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'decks' && <DeckList />}
        {activeTab === 'create' && <DeckForm onSuccess={handleDeckCreated} />}
        {activeTab === 'run-simulation' && (
          <SimulationRunner onSimulationStarted={handleSimulationStarted} />
        )}
        {activeTab === 'simulations' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <SimulationsList
                onSelectSimulation={handleSelectSimulation}
                refreshTrigger={refreshTrigger}
              />
            </div>
            <div className="lg:sticky lg:top-6 h-fit">
              <SimulationResults simulation={selectedSimulation} />
            </div>
          </div>
        )}
        {activeTab === 'profile' && (
          <div className="max-w-2xl mx-auto mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">Profile Information</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300 font-medium">User ID:</span>
                <span className="text-gray-800 dark:text-gray-100 font-mono text-sm">{user?.id}</span>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Username:</span>
                <span className="text-gray-800 dark:text-gray-100">{user?.username}</span>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Email:</span>
                <span className="text-gray-800 dark:text-gray-100">{user?.email}</span>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Full Name:</span>
                <span className="text-gray-800 dark:text-gray-100">{user?.full_name}</span>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Account Status:</span>
                <span className={`px-3 py-1 rounded text-sm font-medium ${
                  user?.is_active 
                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' 
                    : 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
                }`}>
                  {user?.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Verified:</span>
                <span className={`px-3 py-1 rounded text-sm font-medium ${
                  user?.is_verified 
                    ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200' 
                    : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                }`}>
                  {user?.is_verified ? 'Verified' : 'Not Verified'}
                </span>
              </div>
              <div className="flex items-center justify-between py-3">
                <span className="text-gray-600 dark:text-gray-300 font-medium">Member Since:</span>
                <span className="text-gray-800 dark:text-gray-100">
                  {new Date(user?.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 text-center text-gray-600 dark:text-gray-300 text-sm">
          <p>
            MTG Madness Carlo - Phase 1 Testing Environment
          </p>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Backend: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
