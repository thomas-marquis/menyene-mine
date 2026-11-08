import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeCard } from '../../components/recipe/RecipeCard/RecipeCard';
import { RecipeFormModal } from '../../components/recipe/RecipeFormModal/RecipeFormModal';
import { recipeService } from '../../services/recipeService';
import type { Recipe } from '../../types/recipe.types';
import styles from './RecipeList.module.css';

const ITEMS_PER_PAGE = 20;

export const RecipeListPage = () => {
  const [allRecipes, setAllRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);

  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<Recipe[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch all recipes (for non-search mode)
  const fetchAllRecipes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      const response = await recipeService.getAllRecipes(0, 1000); // Get all recipes
      setAllRecipes(response.recipes);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch recipes. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch recipes. Please try again later.');
      }
      console.error('Error fetching recipes:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Search recipes
  const handleSearch = useCallback(
    async (query: string) => {
      if (!query.trim()) {
        setIsSearching(false);
        setSearchResults([]);
        setCurrentPage(1);
        await fetchAllRecipes();
        return;
      }

      try {
        setIsSearching(true);
        setError(null);
        const response = await recipeService.searchRecipes(query, 0, 1000); // Get all matching recipes
        setSearchResults(response.recipes);
        setCurrentPage(1);
      } catch (err: any) {
        if (err.response) {
          setError('Failed to search recipes. Please try again.');
        } else if (err.request) {
          setError('Network error. Please check your connection.');
        } else {
          setError('Failed to search recipes. Please try again.');
        }
        console.error('Error searching recipes:', err);
      } finally {
        setIsSearching(false);
      }
    },
    [fetchAllRecipes]
  );

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      handleSearch(searchQuery);
    } else {
      setError(null);
      setIsSearching(false);
      setSearchResults([]);
      fetchAllRecipes();
    }
  };

  useEffect(() => {
    fetchAllRecipes();
  }, [fetchAllRecipes]);

  useEffect(() => {
    if (searchQuery.trim() === '') {
      setCurrentPage(1);
      fetchAllRecipes();
    }
  }, [searchQuery, fetchAllRecipes]);

  useEffect(() => {
    setSuccessMessage(null);
  }, [currentPage, searchQuery]);

  const handleViewRecipe = (id: number) => {
    setError(null);
    setSuccessMessage(null);
    if (id && !isNaN(id)) {
      navigate(`/recipes/${id}`);
    }
  };

  const handleCreateRecipe = () => {
    setError(null);
    setShowCreateModal(true);
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
    setError(null);
  };

  const handleRecipeCreated = () => {
    setShowCreateModal(false);
    setError(null);
    setSearchQuery('');
    setIsSearching(false);
    setSearchResults([]);
    setCurrentPage(1);
    fetchAllRecipes();
    setSuccessMessage('Recipe created successfully!');
    setTimeout(() => {
      setSuccessMessage(null);
    }, 3000);
  };

  // Get recipes for current page
  const displayRecipes = searchQuery.trim() ? searchResults : allRecipes;
  const totalPages = Math.max(1, Math.ceil(displayRecipes.length / ITEMS_PER_PAGE)) || 1;
  
  // Ensure current page is within valid range
  const safeCurrentPage = Math.min(currentPage, totalPages);

  const paginatedRecipes = displayRecipes.slice(
    (safeCurrentPage - 1) * ITEMS_PER_PAGE,
    safeCurrentPage * ITEMS_PER_PAGE
  );

  // Render pagination buttons with ellipsis for many pages
  const renderPaginationButtons = () => {
    const buttons = [];
    const maxVisiblePages = 5; // Maximum number of page buttons to show
    
    // Always show first page
    if (totalPages > 1) {
      buttons.push(
        <li
          key={1}
          className={`page-item ${safeCurrentPage === 1 ? 'active' : ''}`}
        >
          <button
            className="page-link"
            onClick={() => {
              if (!loading) {
                setCurrentPage(1);
              }
            }}
            disabled={loading}
          >
            1
          </button>
        </li>
      );
    }

    // Show ellipsis if needed before current page
    if (safeCurrentPage > 3) {
      buttons.push(
        <li key="ellipsis-start" className="page-item disabled">
          <span className="page-link">...</span>
        </li>
      );
    }

    // Show pages around current page
    const startPage = Math.max(2, safeCurrentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(totalPages - 1, safeCurrentPage + Math.floor(maxVisiblePages / 2));

    for (let page = startPage; page <= endPage; page++) {
      buttons.push(
        <li
          key={page}
          className={`page-item ${safeCurrentPage === page ? 'active' : ''}`}
        >
          <button
            className="page-link"
            onClick={() => {
              if (!loading) {
                setCurrentPage(page);
              }
            }}
            disabled={loading}
          >
            {page}
          </button>
        </li>
      );
    }

    // Show ellipsis if needed after current page
    if (safeCurrentPage < totalPages - 2) {
      buttons.push(
        <li key="ellipsis-end" className="page-item disabled">
          <span className="page-link">...</span>
        </li>
      );
    }

    // Always show last page if different from first
    if (totalPages > 1) {
      buttons.push(
        <li
          key={totalPages}
          className={`page-item ${safeCurrentPage === totalPages ? 'active' : ''}`}
        >
          <button
            className="page-link"
            onClick={() => {
              if (!loading) {
                setCurrentPage(totalPages);
              }
            }}
            disabled={loading}
          >
            {totalPages}
          </button>
        </li>
      );
    }

    return buttons;
  };

  if (loading && allRecipes.length === 0 && searchResults.length === 0) {
    return (
      <div className={styles.loadingContainer}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading recipes...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
        <Button
          onClick={() => {
            setError(null);
            fetchAllRecipes();
          }}
          variant="primary"
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Retry'}
        </Button>
      </div>
    );
  }

  return (
    <div className={styles.recipeListContainer}>
      {successMessage && (
        <div className="alert alert-success" role="alert">
          {successMessage}
        </div>
      )}
      <div className={styles.header}>
        <h1 className={styles.title}>My Recipes</h1>
        <Button
          onClick={handleCreateRecipe}
          variant="primary"
          size="medium"
          disabled={loading}
        >
          <i className="bi bi-plus-lg me-2"></i>
          Create Recipe
        </Button>
      </div>

      <div className={styles.searchContainer}>
        <form onSubmit={handleSearchSubmit} className={styles.searchForm}>
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Search recipes by title or content..."
              value={searchQuery}
              onChange={handleSearchChange}
              disabled={loading}
            />
            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading || !searchQuery.trim()}
            >
              <i className="bi bi-search"></i>
            </button>
          </div>
        </form>
      </div>

      {(isSearching || loading) && displayRecipes.length === 0 && searchQuery.trim() ? (
        <div className={styles.loadingContainer}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Searching...</span>
          </div>
          <p>Searching recipes...</p>
        </div>
      ) : paginatedRecipes.length > 0 ? (
        <>
          <div className={styles.recipesGrid}>
            {paginatedRecipes
              .filter((recipe) => recipe && recipe.id)
              .map((recipe) => (
                <RecipeCard
                  key={recipe.id}
                  recipe={recipe}
                  onView={() => handleViewRecipe(recipe.id!)}
                />
              ))}
          </div>

          {totalPages > 1 && (
            <nav className={styles.pagination}>
              <ul className="pagination justify-content-center">
                <li className={`page-item ${safeCurrentPage === 1 ? 'disabled' : ''}`}>
                  <button
                    className="page-link"
                    onClick={() => {
                      if (!loading) {
                        setCurrentPage((p) => Math.max(1, p - 1));
                      }
                    }}
                    disabled={safeCurrentPage === 1 || loading}
                    aria-label="Previous"
                  >
                    <i className="bi bi-chevron-left"></i>
                  </button>
                </li>
                {renderPaginationButtons()}
                <li className={`page-item ${safeCurrentPage === totalPages ? 'disabled' : ''}`}>
                  <button
                    className="page-link"
                    onClick={() => {
                      if (!loading) {
                        setCurrentPage((p) => Math.min(totalPages, p + 1));
                      }
                    }}
                    disabled={safeCurrentPage === totalPages || loading}
                    aria-label="Next"
                  >
                    <i className="bi bi-chevron-right"></i>
                  </button>
                </li>
              </ul>
            </nav>
          )}
        </>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <i className="bi bi-book text-muted" style={{ fontSize: '4rem' }}></i>
          </div>
          <h3>{searchQuery.trim() ? 'No recipes found' : 'No recipes yet'}</h3>
          <p>
            {searchQuery.trim()
              ? 'Try a different search term.'
              : 'Start by creating your first recipe!'}
          </p>
          {searchQuery.trim() && paginatedRecipes.length === 0 && (
            <Button
              onClick={() => {
                if (!loading) {
                  setError(null);
                  setSearchQuery('');
                  setIsSearching(false);
                  setSearchResults([]);
                  setCurrentPage(1);
                  fetchAllRecipes();
                }
              }}
              variant="secondary"
              className="mb-3"
              disabled={loading}
            >
              Clear Search
            </Button>
          )}
          <Button onClick={handleCreateRecipe} variant="primary">
            {searchQuery.trim() ? 'Create New Recipe' : 'Create Your First Recipe'}
          </Button>
        </div>
      )}

      {showCreateModal && (
        <RecipeFormModal
          isOpen={showCreateModal}
          onClose={handleCloseModal}
          onSuccess={handleRecipeCreated}
        />
      )}
    </div>
  );
};
