import { Routes, Route, Navigate } from 'react-router-dom';
import { GroceryListPage } from '../pages/GroceryList/GroceryList';
import { MealCalendarPage } from '../pages/MealCalendar/MealCalendar';
import { NotFoundPage } from '../pages/NotFound/NotFound';
import { DraftDetailPage } from '../pages/RecipeBuilder/DraftDetail';
import { DraftListPage } from '../pages/RecipeBuilder/DraftList';
import { RecipeBuilderPage } from '../pages/RecipeBuilder/RecipeBuilder';
import { RecipeDetailPage } from '../pages/RecipeDetail/RecipeDetail';
import { RecipeGeneratorPage } from '../pages/RecipeGenerator/RecipeGenerator';
import { RecipeListPage } from '../pages/RecipeList/RecipeList';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<RecipeListPage />} />
      <Route path="/calendar" element={<MealCalendarPage />} />
      <Route path="/groceries" element={<GroceryListPage />} />
      <Route path="/recipes/:id" element={<RecipeDetailPage />} />
      <Route path="/recipes/generate" element={<RecipeGeneratorPage />} />
      <Route path="/recipes/builder" element={<RecipeBuilderPage />} />
      <Route path="/recipes/drafts" element={<DraftListPage />} />
      <Route path="/recipes/drafts/:id" element={<DraftDetailPage />} />

      {/* 404 route */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};
