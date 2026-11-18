export interface RecipeStats {
  total_count: number;
}

export interface DraftStats {
  total_count: number;
  draft_count: number;
  validated_count: number;
  rejected_count: number;
}

export interface GroceryStats {
  total_count: number;
  active_count: number;
  completed_count: number;
}

export interface StatsResponse {
  recipes: RecipeStats;
  drafts: DraftStats;
  groceries: GroceryStats;
}
