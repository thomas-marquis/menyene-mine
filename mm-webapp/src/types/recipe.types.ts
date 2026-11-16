export interface Recipe {
  id: number;
  title: string;
  creation_date: string;
  last_updated: string;
  summary: string;
  ingredients: string[];
  instructions: string[];
  servings: number;
  prep_time: string;
  cook_time: string;
  difficulty: string;
}

export interface RecipeListResponse {
  recipes: Recipe[];
  total: number;
  skip: number;
  limit: number;
}

export interface RecipeCreate {
  title: string;
  summary: string;
  ingredients: string[];
  instructions: string[];
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
}

export interface RecipeUpdate {
  title: string;
  summary: string;
  ingredients: string[];
  instructions: string[];
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
}
