/**
 * Configuration Management Component
 * Manages the list and form views for configurations
 */

import { useState } from 'react';
import { ConfigList } from './ConfigList';
import { ConfigForm } from './ConfigForm';
import { SimulationConfig } from '../services/configs';

export function ConfigManagement() {
  const [view, setView] = useState<'list' | 'form'>('list');
  const [editingConfig, setEditingConfig] = useState<SimulationConfig | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleNew = () => {
    setEditingConfig(null);
    setView('form');
  };

  const handleEdit = (config: SimulationConfig) => {
    setEditingConfig(config);
    setView('form');
  };

  const handleDuplicate = (config: SimulationConfig) => {
    // When duplicated, the ConfigList already created it
    // Just refresh the list
    setRefreshTrigger(prev => prev + 1);
  };

  const handleSuccess = () => {
    setView('list');
    setEditingConfig(null);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleCancel = () => {
    setView('list');
    setEditingConfig(null);
  };

  if (view === 'form') {
    return (
      <ConfigForm
        config={editingConfig}
        onSuccess={handleSuccess}
        onCancel={handleCancel}
      />
    );
  }

  return (
    <div>
      <div className="max-w-6xl mx-auto mt-8 px-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              Configurations
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Manage your simulation configurations
            </p>
          </div>
          <button
            onClick={handleNew}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
          >
            New Configuration
          </button>
        </div>
      </div>
      
      <ConfigList
        key={refreshTrigger}
        onEdit={handleEdit}
        onDuplicate={handleDuplicate}
      />
    </div>
  );
}

