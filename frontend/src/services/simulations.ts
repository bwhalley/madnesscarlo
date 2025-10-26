/**
 * Simulations Service
 * Handles simulation CRUD operations and status polling
 */

import api from './api';

export interface CreateSimulationData {
  deck_id: string;
  config_id: string;
  runs?: number;
  turns?: number;
  sideboard_plan?: string;
}

export interface Simulation {
  id: string;
  user_id: string;
  deck_id: string;
  config_id: string;
  runs: number;
  turns: number;
  sideboard_plan?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  results?: any;
  error_message?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export interface SimulationListResponse {
  total: number;
  simulations: Simulation[];
  page: number;
  page_size: number;
}

export interface SimulationStatus {
  simulation_id: string;
  status: string;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  message?: string;
}

class SimulationsService {
  async createSimulation(data: CreateSimulationData): Promise<Simulation> {
    const response = await api.post<Simulation>('/api/simulations/', data);
    return response.data;
  }

  async getSimulations(page: number = 1, pageSize: number = 20): Promise<SimulationListResponse> {
    const response = await api.get<SimulationListResponse>('/api/simulations/', {
      params: { skip: (page - 1) * pageSize, limit: pageSize },
    });
    return response.data;
  }

  async getSimulation(id: string): Promise<Simulation> {
    const response = await api.get<Simulation>(`/api/simulations/${id}`);
    return response.data;
  }

  async getSimulationStatus(id: string): Promise<SimulationStatus> {
    const response = await api.get<SimulationStatus>(`/api/simulations/${id}/status`);
    return response.data;
  }

  async cancelSimulation(id: string): Promise<void> {
    await api.post(`/api/simulations/${id}/cancel`);
  }

  async deleteSimulation(id: string): Promise<void> {
    await api.delete(`/api/simulations/${id}`);
  }

  /**
   * Export simulation results to Google Sheets
   * @param id Simulation ID
   * @returns Object with spreadsheet URL
   */
  async exportToSheets(id: string): Promise<{
    spreadsheet_id: string;
    spreadsheet_url: string;
    message: string;
  }> {
    const response = await api.post(`/api/simulations/${id}/export-to-sheets`);
    return response.data;
  }

  /**
   * Poll simulation status until it's complete
   * @param id Simulation ID
   * @param onProgress Callback for progress updates
   * @param interval Polling interval in milliseconds
   */
  async pollSimulationStatus(
    id: string,
    onProgress: (status: SimulationStatus) => void,
    interval: number = 2000
  ): Promise<Simulation> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getSimulationStatus(id);
          onProgress(status);

          if (status.status === 'completed') {
            const simulation = await this.getSimulation(id);
            resolve(simulation);
          } else if (status.status === 'failed' || status.status === 'cancelled') {
            const simulation = await this.getSimulation(id);
            reject(new Error(status.error_message || 'Simulation failed'));
          } else {
            // Continue polling
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }
}

export const simulationsService = new SimulationsService();

