import { Routes, Route, Navigate } from 'react-router-dom';
import { RecipeListPage } from '../pages/RecipeList/RecipeList';
import { RecipeDetailPage } from '../pages/RecipeDetail/RecipeDetail';
import { NotFoundPage } from '../pages/NotFound/NotFound';

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<RecipeListPage />} />
      <Route path="/recipes/:id" element={<RecipeDetailPage />} />

      {/* 404 route */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};
