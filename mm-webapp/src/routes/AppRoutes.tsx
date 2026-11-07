import { Routes, Route, Navigate } from 'react-router-dom';
import { HomePage } from '../pages/Home/Home';
import { AboutPage } from '../pages/About/About';
import { NotFoundPage } from '../pages/NotFound/NotFound';
import { ProtectedRoute } from './ProtectedRoute';

// Lazy load pages for better performance
// const HomePage = lazy(() => import('../pages/Home/Home'));
// const AboutPage = lazy(() => import('../pages/About/About'));
// const NotFoundPage = lazy(() => import('../pages/NotFound/NotFound'));

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<HomePage />} />
      <Route path="/about" element={<AboutPage />} />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            {/* <DashboardPage /> */}
            <div>Dashboard Page (Coming Soon)</div>
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            {/* <ProfilePage /> */}
            <div>Profile Page (Coming Soon)</div>
          </ProtectedRoute>
        }
      />

      {/* 404 route */}
      <Route path="/404" element={<NotFoundPage />} />
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};
