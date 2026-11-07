import { env } from './env';

export const appConfig = {
  name: env.APP_NAME,
  version: env.APP_VERSION,
  api: {
    baseUrl: env.API_BASE_URL,
    timeout: 10000,
    maxRetries: 3,
  },
  pagination: {
    defaultPage: 1,
    defaultPageSize: 10,
    maxPageSize: 100,
  },
  theme: {
    default: 'light',
    storageKey: 'theme',
  },
  auth: {
    tokenStorageKey: 'token',
    userStorageKey: 'user',
    tokenExpiry: 24 * 60 * 60 * 1000, // 24 hours in milliseconds
  },
};
