import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import './App.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto px-4 py-6">
              <h1 className="text-3xl font-bold text-gray-900">
                🎴 MTG Madness Carlo
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                Monte Carlo Simulator for Magic: The Gathering Decks
              </p>
            </div>
          </header>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 py-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-semibold mb-4">Welcome! 🚀</h2>
              
              <div className="space-y-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900">✅ Frontend Running</h3>
                  <p className="text-sm text-green-700 mt-1">
                    React + TypeScript + TailwindCSS
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900">🔗 Testing Backend Connection</h3>
                  <p className="text-sm text-blue-700 mt-1">
                    API URL: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}
                  </p>
                  <p className="text-sm text-blue-700">
                    Check: <a href="http://localhost:8000" target="_blank" rel="noopener noreferrer" className="underline">http://localhost:8000</a>
                  </p>
                  <p className="text-sm text-blue-700">
                    API Docs: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="underline">http://localhost:8000/docs</a>
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900">📦 Next Steps</h3>
                  <ul className="text-sm text-purple-700 mt-2 space-y-1">
                    <li>• Create authentication pages (login/register)</li>
                    <li>• Build deck editor component</li>
                    <li>• Add simulation UI</li>
                    <li>• Implement results dashboard</li>
                  </ul>
                </div>

                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-2">Quick Links:</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
                      View Decks
                    </button>
                    <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition">
                      New Simulation
                    </button>
                    <button className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition">
                      Experiments
                    </button>
                    <button className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 transition">
                      Compare Decks
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </main>

          {/* Footer */}
          <footer className="mt-12 pb-8 text-center text-gray-600 text-sm">
            MTG Madness Carlo v1.0.0 • Built with FastAPI + React
          </footer>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

