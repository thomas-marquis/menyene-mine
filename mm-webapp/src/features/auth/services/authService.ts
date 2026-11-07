import api from '../../../services/api';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
  name: string;
}

interface AuthResponse {
  user: {
    id: string;
    email: string;
    name: string;
  };
  token: string;
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },

  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    const response = await api.post('/api/auth/register', credentials);
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/api/auth/logout');
    localStorage.removeItem('token');
  },

  async getCurrentUser(): Promise<AuthResponse['user']> {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post('/api/auth/forgot-password', { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    await api.post('/api/auth/reset-password', { token, password });
  },
};
