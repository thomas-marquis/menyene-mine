import { configureStore } from '@reduxjs/toolkit'
import { useDispatch, type TypedUseSelectorHook, useSelector } from 'react-redux'
import statsReducer from './statsSlice'

// Configure the store
export const store = configureStore({
  reducer: {
    stats: statsReducer,
  },
  middleware: (getDefaultMiddleware) => {
    return getDefaultMiddleware({
      serializableCheck: {
        ignoredActionPaths: [],
        ignoredPaths: [],
      },
    })
  },
})

// Infer the RootState and AppDispatch types from the store itself
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// Create a typed version of useDispatch
export const useAppDispatch = () => useDispatch<AppDispatch>()

// Create a typed version of useSelector
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector
