export type MealMoment = 'lunch' | 'dinner';

export interface Meal {
  id: number;
  date: string; // ISO date string (YYYY-MM-DD)
  moment: MealMoment;
  recipe_id: number;
  recipe_title: string;
  created_at: string;
  updated_at: string;
}

export interface MealCreate {
  date: string; // ISO date string (YYYY-MM-DD)
  moment: MealMoment;
  recipe_id: number;
}

export interface MealUpdate {
  recipe_id: number;
}

export interface MealListResponse {
  meals: Meal[];
  total: number;
  year: number;
  month: number;
}

// Calendar view types
export interface CalendarDay {
  date: Date;
  day: number;
  month: number;
  year: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  lunchMeal: Meal | null;
  dinnerMeal: Meal | null;
}

export interface CalendarWeek {
  days: CalendarDay[];
}

export interface CalendarMonth {
  year: number;
  month: number;
  weeks: CalendarWeek[];
  monthName: string;
}
