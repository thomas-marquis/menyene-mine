import api from './api';
import type {
  RecipeDraft,
  RecipeDraftListResponse,
  RecipeDraftStats,
  GenerateDraftRequest,
  RecipeDraftActionResponse,
} from '../types/recipe_draft.types';
import type { Recipe } from '../types/recipe.types';

const RECIPE_DRAFTS_BASE_URL = '/api/v1/recipe-drafts';

export const recipeDraftService = {
  /**
   * Generate recipe drafts from a user prompt
   */
  async generateDrafts(request: GenerateDraftRequest): Promise<RecipeDraft[]> {
    const response = await api.post<RecipeDraft[]>(`${RECIPE_DRAFTS_BASE_URL}/generate`, request);
    return response.data;
  },

  /**
   * List all recipe drafts with optional filtering
   */
  async listDrafts(
    skip: number = 0,
    limit: number = 10,
    status?: string
  ): Promise<RecipeDraftListResponse> {
    const params: Record<string, any> = { skip, limit };
    if (status) {
      params.status = status;
    }
    const response = await api.get<RecipeDraftListResponse>(RECIPE_DRAFTS_BASE_URL, { params });
    return response.data;
  },

  /**
   * Get a specific recipe draft by ID
   */
  async getDraftById(id: number): Promise<RecipeDraft> {
    const response = await api.get<RecipeDraft>(`${RECIPE_DRAFTS_BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Validate a draft (creates an actual recipe)
   */
  async validateDraft(id: number): Promise<RecipeDraftActionResponse> {
    const response = await api.post<RecipeDraftActionResponse>(
      `${RECIPE_DRAFTS_BASE_URL}/${id}/validate`
    );
    return response.data;
  },

  /**
   * Reject a draft
   */
  async rejectDraft(id: number): Promise<RecipeDraftActionResponse> {
    const response = await api.post<RecipeDraftActionResponse>(
      `${RECIPE_DRAFTS_BASE_URL}/${id}/reject`
    );
    return response.data;
  },

  /**
   * Delete a draft
   */
  async deleteDraft(id: number): Promise<void> {
    await api.delete(`${RECIPE_DRAFTS_BASE_URL}/${id}`);
  },

  /**
   * Get statistics about recipe drafts
   */
  async getDraftStats(): Promise<RecipeDraftStats> {
    const response = await api.get<RecipeDraftStats>(`${RECIPE_DRAFTS_BASE_URL}/stats`);
    return response.data;
  },
};
