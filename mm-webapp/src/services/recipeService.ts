import api from './api';
import type {
  Recipe,
  RecipeListResponse,
  RecipeCreate,
  RecipeUpdate,
} from '../types/recipe.types';

const RECIPES_BASE_URL = '/api/v1/recipes';

export const recipeService = {
  async getAllRecipes(skip: number = 0, limit: number = 10): Promise<RecipeListResponse> {
    const response = await api.get<RecipeListResponse>(RECIPES_BASE_URL, {
      params: { skip, limit },
    });
    return response.data;
  },

  async getRecipeById(id: number): Promise<Recipe> {
    const response = await api.get<Recipe>(`${RECIPES_BASE_URL}/${id}`);
    return response.data;
  },

  async createRecipe(recipe: RecipeCreate): Promise<Recipe> {
    const response = await api.post<Recipe>(RECIPES_BASE_URL, recipe);
    return response.data;
  },

  async updateRecipe(id: number, recipe: RecipeUpdate): Promise<Recipe> {
    const response = await api.put<Recipe>(`${RECIPES_BASE_URL}/${id}`, recipe);
    return response.data;
  },

  async deleteRecipe(id: number): Promise<void> {
    await api.delete(`${RECIPES_BASE_URL}/${id}`);
  },

  async searchRecipes(keyword: string, skip: number = 0, limit: number = 10): Promise<RecipeListResponse> {
    const response = await api.get<RecipeListResponse>(`${RECIPES_BASE_URL}/search`, {
      params: { keyword, skip, limit },
    });
    return response.data;
  },
};
