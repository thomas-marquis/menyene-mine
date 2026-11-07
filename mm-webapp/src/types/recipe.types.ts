export interface Recipe {
  id: number;
  title: string;
  creation_date: string;
  last_updated: string;
  content: string;
  summary: string;
}

export interface RecipeListResponse {
  recipes: Recipe[];
  total: number;
  skip: number;
  limit: number;
}

export interface RecipeCreate {
  title: string;
  content: string;
  summary: string;
}

export interface RecipeUpdate {
  title: string;
  content: string;
  summary: string;
}
