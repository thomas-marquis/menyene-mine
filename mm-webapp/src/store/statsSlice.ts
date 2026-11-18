import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "./index";
import type { StatsResponse } from "../types/stats.types";

// Define the initial state
interface StatsState {
  recipes: number;
  pendingDrafts: number;
  uncheckedGroceries: number;
  loaded: boolean;
}

const initialState: StatsState = {
  recipes: 0,
  pendingDrafts: 0,
  uncheckedGroceries: 0,
  loaded: false,
};

// Helper function to format count for display
const formatCount = (count: number): string => {
  return count > 99 ? "99+" : count.toString();
};

// Helper function to extract counts from stats response
export const extractCountsFromStats = (stats: StatsResponse) => ({
  recipes: stats.recipes.total_count,
  pendingDrafts: stats.drafts.draft_count,
  uncheckedGroceries: stats.groceries.active_count,
});

const statsSlice = createSlice({
  name: "stats",
  initialState,
  reducers: {
    // Set stats from API response
    setStats: (state, action: PayloadAction<StatsResponse>) => {
      const counts = extractCountsFromStats(action.payload);
      state.recipes = counts.recipes;
      state.pendingDrafts = counts.pendingDrafts;
      state.uncheckedGroceries = counts.uncheckedGroceries;
      state.loaded = true;
    },
    
    // Increment recipe count
    incrementRecipeCount: (state) => {
      state.recipes += 1;
    },
    
    // Decrement recipe count
    decrementRecipeCount: (state) => {
      state.recipes = Math.max(0, state.recipes - 1);
    },
    
    // Increment pending draft count
    incrementPendingDraftCount: (state) => {
      state.pendingDrafts += 1;
    },
    
    // Decrement pending draft count
    decrementPendingDraftCount: (state) => {
      state.pendingDrafts = Math.max(0, state.pendingDrafts - 1);
    },
    
    // Set pending draft count (for when drafts are validated/rejected)
    setPendingDraftCount: (state, action: PayloadAction<number>) => {
      state.pendingDrafts = Math.max(0, action.payload);
    },
    
    // Increment unchecked grocery count
    incrementUncheckedGroceryCount: (state) => {
      state.uncheckedGroceries += 1;
    },
    
    // Decrement unchecked grocery count
    decrementUncheckedGroceryCount: (state) => {
      state.uncheckedGroceries = Math.max(0, state.uncheckedGroceries - 1);
    },
    
    // Set unchecked grocery count
    setUncheckedGroceryCount: (state, action: PayloadAction<number>) => {
      state.uncheckedGroceries = Math.max(0, action.payload);
    },
    
    // Reset stats
    resetStats: () => initialState,
  },
});

// Export actions
export const {
  setStats,
  incrementRecipeCount,
  decrementRecipeCount,
  incrementPendingDraftCount,
  decrementPendingDraftCount,
  setPendingDraftCount,
  incrementUncheckedGroceryCount,
  decrementUncheckedGroceryCount,
  setUncheckedGroceryCount,
  resetStats,
} = statsSlice.actions;

// Export selectors
export const selectStats = (state: RootState) => state.stats;
export const selectRecipesCount = (state: RootState) => state.stats.recipes;
export const selectPendingDraftsCount = (state: RootState) => state.stats.pendingDrafts;
export const selectUncheckedGroceriesCount = (state: RootState) => state.stats.uncheckedGroceries;
export const selectStatsLoaded = (state: RootState) => state.stats.loaded;

// Export helper function for display
export const getFormattedCount = (state: RootState, statType: "recipes" | "pendingDrafts" | "uncheckedGroceries") => {
  const count = state.stats[statType];
  return count > 0 ? formatCount(count) : null;
};

// Export reducer
export default statsSlice.reducer;
