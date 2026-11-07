import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../../../store';
import {
  loginStart,
  loginSuccess,
  loginFailure,
  logout,
  clearError,
} from '../authSlice';
import { authService } from '../services/authService';

interface LoginCredentials {
  email: string;
  password: string;
}

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const { user, token, isAuthenticated, loading, error } = useAppSelector(
    (state) => state.auth
  );

  const handleLogin = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        dispatch(loginStart());
        const response = await authService.login(credentials);
        dispatch(loginSuccess({ user: response.user, token: response.token }));
        localStorage.setItem('token', response.token);
        return response;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Login failed. Please try again.';
        dispatch(loginFailure(errorMessage));
        throw err;
      }
    },
    [dispatch]
  );

  const handleLogout = useCallback(() => {
    dispatch(logout());
    localStorage.removeItem('token');
    authService.logout();
  }, [dispatch]);

  const clearAuthError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  return {
    user,
    token,
    isAuthenticated,
    loading,
    error,
    login: handleLogin,
    logout: handleLogout,
    clearError: clearAuthError,
  };
};
