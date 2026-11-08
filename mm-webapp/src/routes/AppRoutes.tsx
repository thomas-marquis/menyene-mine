import { Routes, Route, Navigate } from 'react-router-dom';
import { RecipeListPage } from '../pages/RecipeList/RecipeList';
import { RecipeDetailPage } from '../pages/RecipeDetail/RecipeDetail';
import { GroceryListPage } from '../pages/GroceryList/GroceryList';
import { NotFoundPage } from '../pages/NotFound/NotFound';
import { RecipeBuilderPage } from '../pages/RecipeBuilder/RecipeBuilder';
import { DraftListPage } from '../pages/RecipeBuilder/DraftList';
import { DraftDetailPage } from '../pages/RecipeBuilder/DraftDetail';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<RecipeListPage />} />
      <Route path="/recipes/:id" element={<RecipeDetailPage />} />
      <Route path="/recipes/builder" element={<RecipeBuilderPage />} />
      <Route path="/recipes/drafts" element={<DraftListPage />} />
      <Route path="/recipes/drafts/:id" element={<DraftDetailPage />} />
      <Route path="/groceries" element={<GroceryListPage />} />

      {/* 404 route */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};
