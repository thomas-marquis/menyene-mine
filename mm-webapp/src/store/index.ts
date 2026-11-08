import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, type TypedUseSelectorHook, useSelector } from 'react-redux';

// Configure the store
// For now, we don't need any slices since we're not implementing authentication
// We'll keep the store structure for future use

export const store = configureStore({
  reducer: {
    // Add slices here when needed
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
