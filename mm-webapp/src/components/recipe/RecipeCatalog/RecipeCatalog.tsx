import { useState, useEffect, useCallback, useMemo } from 'react';
import { Spinner, Alert, Row, Col, Pagination } from 'react-bootstrap';
import { recipeService } from '../../../services/recipeService';
import type { Recipe, RecipeListResponse } from '../../../types/recipe.types';
import { RecipeCard } from '../RecipeCard/RecipeCard';
import { SearchBar } from '../../common/SearchBar';

/**
 * Props for the RecipeCatalog component
 */
interface RecipeCatalogProps {
  /** Callback when a recipe is selected */
  onRecipeSelect?: (recipe: Recipe | null) => void;
  /** Callback when a recipe is viewed */
  onRecipeView?: (recipe: Recipe) => void;
  /** ID of the currently selected recipe */
  selectedRecipeId?: number | null;
  /** Maximum number of recipes to display (overrides pagination) */
  maxRecipes?: number;
  /** Whether to show the search bar */
  showSearch?: boolean;
  /** Whether to show pagination controls */
  showPagination?: boolean;
  /** Number of items per page when pagination is enabled */
  itemsPerPage?: number;
  /** External search query (controlled mode) */
  searchQuery?: string;
  /** Callback when search query changes (controlled mode) */
  onSearchChange?: (query: string) => void;
  /** Placeholder text for the search input */
  searchPlaceholder?: string;
  /** Additional CSS class name for the container */
  className?: string;
  /** Additional inline styles for the container */
  style?: React.CSSProperties;
}

/**
 * RecipeCatalog - A reusable component for displaying a catalog of recipes with search and pagination.
 * 
 * Features:
 * - Server-side search and pagination
 * - Customizable recipe cards with action buttons
 * - Optional search bar
 * - Optional pagination controls
 * 
 * @example
 * // With pagination
 * <RecipeCatalog showPagination={true} itemsPerPage={20} />
 * 
 * @example
 * // With selection and custom buttons
 * <RecipeCatalog 
 *   onRecipeSelect={(recipe) => console.log(recipe)}
 *   selectedRecipeId={selectedId}
 *   maxRecipes={6}
 * />
 */
export const RecipeCatalog = ({
  onRecipeSelect,
  onRecipeView,
  selectedRecipeId = null,
  maxRecipes,
  showSearch = true,
  showPagination = false,
  itemsPerPage = 20,
  searchQuery: externalSearchQuery = '',
  onSearchChange,
  searchPlaceholder = 'Search recipes by title, summary, ingredients...',
  className = '',
  style = {},
}: RecipeCatalogProps) => {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [internalSearchQuery, setInternalSearchQuery] = useState<string>('');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [shouldSearch, setShouldSearch] = useState<boolean>(true);

  const activeSearchQuery = externalSearchQuery || internalSearchQuery;

  const fetchRecipes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const limit = maxRecipes || itemsPerPage;
      const skip = showPagination ? (currentPage - 1) * itemsPerPage : 0;
      
      const response: RecipeListResponse = activeSearchQuery.trim() 
        ? await recipeService.searchRecipes(activeSearchQuery, skip, limit)
        : await recipeService.getAllRecipes(skip, limit);
      
      setRecipes(response.recipes);
      setTotal(response.total);
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
      setShouldSearch(false);
    }
  }, [activeSearchQuery, currentPage, itemsPerPage, maxRecipes, showPagination]);

  const handleSearchChange = (query: string) => {
    if (onSearchChange) {
      onSearchChange(query);
    } else {
      setInternalSearchQuery(query);
    }
  };

  const handleSearchSubmit = (query: string) => {
    if (onSearchChange) {
      onSearchChange(query);
    } else {
      setInternalSearchQuery(query);
    }
    setCurrentPage(1);
    setShouldSearch(true);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    setShouldSearch(true);
  };

  const sortedRecipes = useMemo(() => {
    if (!selectedRecipeId) return recipes;
    
    const sorted = [...recipes];
    const selectedIndex = sorted.findIndex(r => r.id === selectedRecipeId);
    if (selectedIndex > -1) {
      const [selected] = sorted.splice(selectedIndex, 1);
      sorted.unshift(selected);
    }
    return sorted;
  }, [recipes, selectedRecipeId]);

  const totalPages = showPagination ? Math.ceil(total / itemsPerPage) : 1;
  const safeCurrentPage = Math.min(currentPage, totalPages);

  // Fetch on mount
  useEffect(() => {
    fetchRecipes();
  }, []);

  // Fetch when shouldSearch flag is set
  useEffect(() => {
    if (shouldSearch) {
      fetchRecipes();
    }
  }, [shouldSearch, fetchRecipes]);

  const renderPaginationItems = () => {
    const items = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= 1) return items;

    items.push(
      <Pagination.Item
        key={1}
        active={safeCurrentPage === 1}
        onClick={() => !loading && handlePageChange(1)}
        disabled={loading}
      >
        1
      </Pagination.Item>
    );

    if (safeCurrentPage > 3) {
      items.push(<Pagination.Ellipsis key="ellipsis-start" disabled />);
    }

    const startPage = Math.max(2, safeCurrentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(totalPages - 1, safeCurrentPage + Math.floor(maxVisiblePages / 2));

    for (let page = startPage; page <= endPage; page++) {
      items.push(
        <Pagination.Item
          key={page}
          active={safeCurrentPage === page}
          onClick={() => !loading && handlePageChange(page)}
          disabled={loading}
        >
          {page}
        </Pagination.Item>
      );
    }

    if (safeCurrentPage < totalPages - 2) {
      items.push(<Pagination.Ellipsis key="ellipsis-end" disabled />);
    }

    if (totalPages > 1) {
      items.push(
        <Pagination.Item
          key={totalPages}
          active={safeCurrentPage === totalPages}
          onClick={() => !loading && handlePageChange(totalPages)}
          disabled={loading}
        >
          {totalPages}
        </Pagination.Item>
      );
    }

    return items;
  };

  return (
    <div className={className} style={style}>
      {showSearch && (
        <div className="mb-3">
          <SearchBar
            value={activeSearchQuery}
            onChange={handleSearchChange}
            onSubmit={handleSearchSubmit}
            placeholder={searchPlaceholder}
            disabled={loading}
          />
        </div>
      )}

      {sortedRecipes.length > 0 ? (
        <>
          <Row xs={1} md={2} lg={3} className="g-3">
            {sortedRecipes.map(recipe => {
              const isSelected = selectedRecipeId === recipe.id;
              
              const leftButton = onRecipeView ? {
                label: 'View',
                icon: <i className="bi bi-eye"></i>,
                variant: 'outline-primary',
                onClick: () => onRecipeView(recipe),
              } : undefined;

              const rightButton = onRecipeSelect ? {
                label: isSelected ? 'Cancel' : 'Select',
                icon: isSelected ? <i className="bi bi-x"></i> : <i className="bi bi-check"></i>,
                variant: isSelected ? 'outline-danger' : 'primary',
                onClick: () => onRecipeSelect(isSelected ? null : recipe),
              } : undefined;

              return (
                <Col key={recipe.id}>
                  <RecipeCard
                    recipe={recipe}
                    isSelected={isSelected}
                    leftButton={leftButton}
                    rightButton={rightButton}
                  />
                </Col>
              );
            })}
          </Row>

          {showPagination && totalPages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              <Pagination>
                <Pagination.First
                  onClick={() => !loading && handlePageChange(1)}
                  disabled={safeCurrentPage === 1 || loading}
                  aria-label="First"
                />
                <Pagination.Prev
                  onClick={() => !loading && handlePageChange(safeCurrentPage - 1)}
                  disabled={safeCurrentPage === 1 || loading}
                  aria-label="Previous"
                />
                {renderPaginationItems()}
                <Pagination.Next
                  onClick={() => !loading && handlePageChange(safeCurrentPage + 1)}
                  disabled={safeCurrentPage === totalPages || loading}
                  aria-label="Next"
                />
                <Pagination.Last
                  onClick={() => !loading && handlePageChange(totalPages)}
                  disabled={safeCurrentPage === totalPages || loading}
                  aria-label="Last"
                />
              </Pagination>
            </div>
          )}
        </>
      ) : (
        <div className="col-12 text-center py-4 text-muted">
          <p>No recipes found</p>
        </div>
      )}

      {maxRecipes && !showPagination && recipes.length >= maxRecipes && (
        <div className="text-center mt-3 text-muted small">
          Showing first {maxRecipes} results
        </div>
      )}
    </div>
  );
};
