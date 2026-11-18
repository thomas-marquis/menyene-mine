import api from "./api";
import type { StatsResponse } from "../types/stats.types";

const STATS_BASE_URL = "/api/v1/stats";

export const statsService = {
  async getAllStats(): Promise<StatsResponse> {
    const response = await api.get<StatsResponse>(STATS_BASE_URL);
    return response.data;
  },
};
