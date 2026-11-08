export interface RecipeDraft {
  id: number;
  user_prompt: string;
  generated_content: RecipeDraftContent;
  status: RecipeDraftStatus;
  created_at: string;
  updated_at: string;
  recipe_id: number | null;
}

export interface RecipeDraftContent {
  title: string;
  content: string;
  summary: string;
  ingredients?: string[];
  instructions?: string[];
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
  [key: string]: any;
}

export type RecipeDraftStatus = 'draft' | 'validated' | 'rejected';

export interface RecipeDraftListResponse {
  drafts: RecipeDraft[];
  total: number;
  skip: number;
  limit: number;
}

export interface RecipeDraftStats {
  total: number;
  draft: number;
  validated: number;
  rejected: number;
}

export interface GenerateDraftRequest {
  prompt: string;
  max_drafts?: number;
}

export interface RecipeDraftActionResponse {
  success: boolean;
  message: string;
  draft?: RecipeDraft;
  recipe?: any; // Will use Recipe type from recipe.types
}
