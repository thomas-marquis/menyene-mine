import type { RootState } from './index'

export const selectStats = (state: RootState) => state.stats
export const selectRecipesCount = (state: RootState) => state.stats.recipes
export const selectPendingDraftsCount = (state: RootState) => state.stats.pendingDrafts
export const selectUncheckedGroceriesCount = (state: RootState) => state.stats.uncheckedGroceries
