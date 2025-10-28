/**
 * Simulation Configs Service
 * Handles simulation configuration operations
 */

import api from './api';

export interface SimulationConfig {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  default_runs: number;
  default_turns: number;
  key_card_turn_limit: number;
  key_cards: string[];
  mulligan_strategy: any;
  ideal_setups: any[];
  sideboard_plans: any;
  is_default: boolean;
  is_public: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ConfigListResponse {
  total: number;
  configs: SimulationConfig[];
  page: number;
  page_size: number;
}

export interface ConfigCreateData {
  name: string;
  description?: string;
  default_runs: number;
  default_turns: number;
  key_card_turn_limit: number;
  key_cards: string[];
  mulligan_strategy: any;
  ideal_setups: any[];
  sideboard_plans?: any;
  is_default?: boolean;
  is_public?: boolean;
}

export interface ConfigUpdateData extends Partial<ConfigCreateData> {}

class ConfigsService {
  async getConfigs(page: number = 1, pageSize: number = 20): Promise<ConfigListResponse> {
    // Backend returns an array directly, not a paginated response
    const response = await api.get<SimulationConfig[]>('/api/configs/', {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
    
    // Transform to match expected interface
    return {
      total: response.data.length,
      configs: response.data,
      page: page,
      page_size: pageSize
    };
  }

  async getConfig(id: string): Promise<SimulationConfig> {
    const response = await api.get<SimulationConfig>(`/api/configs/${id}`);
    return response.data;
  }

  async createConfig(data: ConfigCreateData): Promise<SimulationConfig> {
    const response = await api.post<SimulationConfig>('/api/configs/', data);
    return response.data;
  }

  async updateConfig(id: string, data: ConfigUpdateData): Promise<SimulationConfig> {
    const response = await api.put<SimulationConfig>(`/api/configs/${id}`, data);
    return response.data;
  }

  async deleteConfig(id: string): Promise<void> {
    await api.delete(`/api/configs/${id}`);
  }

  async duplicateConfig(id: string): Promise<SimulationConfig> {
    const response = await api.post<SimulationConfig>(`/api/configs/${id}/duplicate`);
    return response.data;
  }

  async setDefaultConfig(id: string): Promise<SimulationConfig> {
    const response = await api.post<SimulationConfig>(`/api/configs/${id}/set-default`);
    return response.data;
  }
}

export const configsService = new ConfigsService();

