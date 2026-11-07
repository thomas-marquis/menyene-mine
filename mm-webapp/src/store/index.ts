import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, type TypedUseSelectorHook, useSelector } from 'react-redux';

// Import slices here
import authReducer from '../features/auth/authSlice';

// Configure the store
export const store = configureStore({
  reducer: {
    // Add slices here
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) => {
    return getDefaultMiddleware({
      serializableCheck: {
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'meta.baseQueryMeta'],
        // Ignore these paths in the state
        ignoredPaths: ['some.nested.path'],
      },
    });
  },
});

// Infer the RootState and AppDispatch types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Create a typed version of useDispatch
export const useAppDispatch = () => useDispatch<AppDispatch>();

// Create a typed version of useSelector
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
