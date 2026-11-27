import { useCallback, useEffect, useState } from 'react'
import type { Recipe, RecipeListResponse } from '../types'
import { recipeService } from '../services'

export function useRecipes(itemsPerPage: number = 20, initialSearchQuery: string = '') {
  const [loading, setLoading] = useState<boolean>(true)
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [searchQuery, setSearchQuery] = useState(initialSearchQuery)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState<number>(0)

  const fetchRecipes = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const limit = itemsPerPage
      const skip = (currentPage - 1) * itemsPerPage

      const response: RecipeListResponse = searchQuery.trim()
        ? await recipeService.searchRecipes(searchQuery, skip, limit)
        : await recipeService.getAllRecipes(skip, limit)

      setRecipes(response.recipes)
      setTotal(response.total)
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch recipes. Please try again later.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to fetch recipes. Please try again later.')
      }
      console.error('Error fetching recipes:', err)
    } finally {
      setLoading(false)
    }
  }, [searchQuery, currentPage, itemsPerPage])

  useEffect(() => {
    fetchRecipes()
  }, [fetchRecipes])

  const changePage = (page: number) => {
    setCurrentPage(page)
  }

  const search = (query: string) => {
    setCurrentPage(1)
    setSearchQuery(query)
    fetchRecipes()
  }

  return { loading, recipes, error, total, currentPage, changePage, search }
}
