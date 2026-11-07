export const env = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  APP_NAME: import.meta.env.VITE_APP_NAME || 'Menyene Mine',
  APP_VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  NODE_ENV: import.meta.env.NODE_ENV || 'development',
  IS_DEV: import.meta.env.NODE_ENV === 'development',
  IS_PROD: import.meta.env.NODE_ENV === 'production',
};
