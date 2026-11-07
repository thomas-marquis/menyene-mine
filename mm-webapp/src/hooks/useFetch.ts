import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface FetchOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

export const useFetch = <T = any>(
  url: string,
  options: FetchOptions = {}
): FetchState<T> & { refetch: () => Promise<void> } => {
  const { immediate = true, onSuccess, onError } = options;
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchData = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      const response = await api.get<T>(url);
      setState({ data: response.data, loading: false, error: null });
      onSuccess?.(response.data);
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'An error occurred while fetching data';
      setState({ data: null, loading: false, error: errorMessage });
      onError?.(errorMessage);
    }
  }, [url, onSuccess, onError]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [immediate, fetchData]);

  return {
    ...state,
    refetch: fetchData,
  };
};
