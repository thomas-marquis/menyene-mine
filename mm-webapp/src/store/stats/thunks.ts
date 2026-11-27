import { createAsyncThunk } from '@reduxjs/toolkit'

import { statsService } from '../../services/statsService'

export const getAllStats = createAsyncThunk('stats/getAll', async () => {
  const response = await statsService.getAllStats()
  return response
})
