import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../store';
import { type ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

export const ProtectedRoute = ({
  children,
  redirectTo = '/',
}: ProtectedRouteProps) => {
  const { isAuthenticated, loading } = useAppSelector((state) => state.auth);
  const location = useLocation();

  if (loading) {
    // You can replace this with a loading spinner component
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    // Redirect to login page, but save the attempted location
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
