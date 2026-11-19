import api from './api';
import type {
  Meal,
  MealCreate,
  MealUpdate,
  MealListResponse,
} from '../types/meal.types';

const MEALS_BASE_URL = '/api/v1/meals';

export const mealService = {
  async getMealsForMonth(year: number, month: number): Promise<MealListResponse> {
    const response = await api.get<MealListResponse>(MEALS_BASE_URL, {
      params: { year, month },
    });
    return response.data;
  },

  async getMealById(id: number): Promise<Meal> {
    const response = await api.get<Meal>(`${MEALS_BASE_URL}/${id}`);
    return response.data;
  },

  async createMeal(meal: MealCreate): Promise<Meal> {
    const response = await api.post<Meal>(MEALS_BASE_URL, meal);
    return response.data;
  },

  async updateMeal(id: number, meal: MealUpdate): Promise<Meal> {
    const response = await api.put<Meal>(`${MEALS_BASE_URL}/${id}`, meal);
    return response.data;
  },

  async deleteMeal(id: number): Promise<void> {
    await api.delete(`${MEALS_BASE_URL}/${id}`);
  },
};
