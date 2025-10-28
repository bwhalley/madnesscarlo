/**
 * WebSocket Service
 * 
 * Real-time updates for simulations via WebSocket.
 */

export interface SimulationUpdate {
  type: 'connected' | 'status' | 'progress' | 'completed' | 'error' | 'pong';
  simulation_id: string;
  status?: string;
  progress?: number;
  current?: number;
  total?: number;
  message?: string;
  error?: string;
}

export type UpdateCallback = (update: SimulationUpdate) => void;

export class SimulationWebSocket {
  private ws: WebSocket | null = null;
  private simulationId: string;
  private callbacks: Set<UpdateCallback> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second

  constructor(simulationId: string) {
    this.simulationId = simulationId;
  }

  /**
   * Connect to the WebSocket endpoint.
   */
  connect(onUpdate: UpdateCallback): void {
    this.callbacks.add(onUpdate);

    // Construct WebSocket URL - use current protocol and hostname
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const envUrl = import.meta.env.VITE_WS_URL;
    
    let wsUrl: string;
    if (envUrl) {
      // Use env URL but replace protocol to match current page
      const cleanUrl = envUrl.replace(/^wss?:\/\//, '');
      wsUrl = `${protocol}//${cleanUrl}/ws/simulations/${this.simulationId}`;
    } else {
      // Default to same host as current page
      wsUrl = `${protocol}//${window.location.hostname}:8000/ws/simulations/${this.simulationId}`;
    }

    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log(`✅ WebSocket connected for simulation ${this.simulationId}`);
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
      };

      this.ws.onmessage = (event) => {
        try {
          const update: SimulationUpdate = JSON.parse(event.data);
          console.log('📨 WebSocket message:', update);

          // Notify all callbacks
          this.callbacks.forEach(callback => callback(update));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      this.ws.onclose = (event) => {
        console.log(`🔌 WebSocket closed for simulation ${this.simulationId}`, event);

        // Attempt to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Reconnecting (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

          setTimeout(() => {
            if (this.callbacks.size > 0) {
              const callback = Array.from(this.callbacks)[0];
              this.connect(callback);
            }
          }, this.reconnectDelay);

          // Exponential backoff
          this.reconnectDelay *= 2;
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
    }
  }

  /**
   * Send a ping message to keep the connection alive.
   */
  ping(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send('ping');
    }
  }

  /**
   * Disconnect from the WebSocket.
   */
  disconnect(): void {
    if (this.ws) {
      console.log(`🔌 Disconnecting WebSocket for simulation ${this.simulationId}`);
      this.ws.close();
      this.ws = null;
    }
    this.callbacks.clear();
  }

  /**
   * Remove a callback.
   */
  removeCallback(callback: UpdateCallback): void {
    this.callbacks.delete(callback);
  }
}

/**
 * Create a WebSocket connection for a simulation.
 */
export function connectToSimulation(
  simulationId: string,
  onUpdate: UpdateCallback
): SimulationWebSocket {
  const ws = new SimulationWebSocket(simulationId);
  ws.connect(onUpdate);
  return ws;
}

