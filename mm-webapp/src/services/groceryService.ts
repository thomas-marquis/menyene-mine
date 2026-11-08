import api from './api';
import type {
  GroceryItem,
  GroceryItemListResponse,
  GroceryItemCreate,
  GroceryItemUpdate,
} from '../types/grocery.types';

const GROCERIES_BASE_URL = '/api/v1/groceries';

export const groceryService = {
  async getAllGroceryItems(skip: number = 0, limit: number = 100): Promise<GroceryItemListResponse> {
    const response = await api.get<GroceryItemListResponse>(GROCERIES_BASE_URL, {
      params: { skip, limit },
    });
    return response.data;
  },

  async getGroceryItemById(id: number): Promise<GroceryItem> {
    const response = await api.get<GroceryItem>(`${GROCERIES_BASE_URL}/${id}`);
    return response.data;
  },

  async createGroceryItem(item: GroceryItemCreate): Promise<GroceryItem> {
    const response = await api.post<GroceryItem>(GROCERIES_BASE_URL, item);
    return response.data;
  },

  async updateGroceryItem(id: number, item: GroceryItemUpdate): Promise<GroceryItem> {
    const response = await api.put<GroceryItem>(`${GROCERIES_BASE_URL}/${id}`, item);
    return response.data;
  },

  async deleteGroceryItem(id: number): Promise<void> {
    await api.delete(`${GROCERIES_BASE_URL}/${id}`);
  },

  async toggleGroceryItemCompletion(id: number, isCompleted: boolean): Promise<GroceryItem> {
    const response = await api.put<GroceryItem>(`${GROCERIES_BASE_URL}/${id}`, {
      name: '', // Will be ignored, but required by schema
      is_completed: isCompleted,
    });
    return response.data;
  },
};
