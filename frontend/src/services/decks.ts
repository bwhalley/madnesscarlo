/**
 * Decks Service
 * Handles deck CRUD operations
 */

import api from './api';

export interface CardInDeck {
  name: string;
  quantity: number;
  type?: string;
  mana_cost?: string;
  conditions?: string;
}

export interface CreateDeckData {
  name: string;
  description?: string;
  cards: CardInDeck[];
  card_count?: string;
  format?: string;
  colors?: string[];
  is_public?: boolean;
  tags?: string[];
}

export interface Deck {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  cards: CardInDeck[];
  card_count?: string;
  format?: string;
  colors?: string[];
  is_public: boolean;
  tags?: string[];
  created_at: string;
  updated_at?: string;
}

export interface DeckListResponse {
  total: number;
  decks: Deck[];
  page: number;
  page_size: number;
}

class DecksService {
  async createDeck(data: CreateDeckData): Promise<Deck> {
    const response = await api.post<Deck>('/api/decks/', data);
    return response.data;
  }

  async getDecks(page: number = 1, pageSize: number = 20): Promise<DeckListResponse> {
    const response = await api.get<DeckListResponse>('/api/decks/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  async getDeck(id: string): Promise<Deck> {
    const response = await api.get<Deck>(`/api/decks/${id}`);
    return response.data;
  }

  async updateDeck(id: string, data: Partial<CreateDeckData>): Promise<Deck> {
    const response = await api.put<Deck>(`/api/decks/${id}`, data);
    return response.data;
  }

  async deleteDeck(id: string): Promise<void> {
    await api.delete(`/api/decks/${id}`);
  }
}

export const decksService = new DecksService();

