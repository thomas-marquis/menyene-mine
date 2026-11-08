import { Routes, Route, Navigate } from 'react-router-dom';
import { RecipeListPage } from '../pages/RecipeList/RecipeList';
import { RecipeDetailPage } from '../pages/RecipeDetail/RecipeDetail';
import { GroceryListPage } from '../pages/GroceryList/GroceryList';
import { NotFoundPage } from '../pages/NotFound/NotFound';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<RecipeListPage />} />
      <Route path="/recipes/:id" element={<RecipeDetailPage />} />
      <Route path="/groceries" element={<GroceryListPage />} />

      {/* 404 route */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};
