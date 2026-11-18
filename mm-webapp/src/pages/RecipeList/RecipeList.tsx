import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeCard } from '../../components/recipe/RecipeCard/RecipeCard';
import { RecipeFormModal } from '../../components/recipe/RecipeFormModal/RecipeFormModal';
import { recipeService } from '../../services/recipeService';
import type { Recipe } from '../../types/recipe.types';
import { Container, Row, Col, Form, InputGroup, Alert, Pagination, Spinner } from 'react-bootstrap';

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

  const handleCreateWithAI = () => {
    setError(null);
    navigate('/recipes/generate');
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

  // Render pagination items
  const renderPaginationItems = () => {
    const items = [];
    const maxVisiblePages = 5; // Maximum number of page buttons to show
    
    // Always show first page
    if (totalPages > 1) {
      items.push(
        <Pagination.Item
          key={1}
          active={safeCurrentPage === 1}
          onClick={() => !loading && setCurrentPage(1)}
          disabled={loading}
        >
          1
        </Pagination.Item>
      );
    }

    // Show ellipsis if needed before current page
    if (safeCurrentPage > 3) {
      items.push(
        <Pagination.Ellipsis key="ellipsis-start" disabled />
      );
    }

    // Show pages around current page
    const startPage = Math.max(2, safeCurrentPage - Math.floor(maxVisiblePages / 2));
    const endPage = Math.min(totalPages - 1, safeCurrentPage + Math.floor(maxVisiblePages / 2));

    for (let page = startPage; page <= endPage; page++) {
      items.push(
        <Pagination.Item
          key={page}
          active={safeCurrentPage === page}
          onClick={() => !loading && setCurrentPage(page)}
          disabled={loading}
        >
          {page}
        </Pagination.Item>
      );
    }

    // Show ellipsis if needed after current page
    if (safeCurrentPage < totalPages - 2) {
      items.push(
        <Pagination.Ellipsis key="ellipsis-end" disabled />
      );
    }

    // Always show last page if different from first
    if (totalPages > 1) {
      items.push(
        <Pagination.Item
          key={totalPages}
          active={safeCurrentPage === totalPages}
          onClick={() => !loading && setCurrentPage(totalPages)}
          disabled={loading}
        >
          {totalPages}
        </Pagination.Item>
      );
    }

    return items;
  };

  if (loading && allRecipes.length === 0 && searchResults.length === 0) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" role="status" className="mb-3">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p>Loading recipes...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="danger" className="mb-4">
          <strong>Error:</strong> {error}
        </Alert>
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
      </Container>
    );
  }

  return (
    <Container className="py-4">
      {successMessage && (
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
      )}
      
      {/* Header */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3">
        <div>
          <h1 className="mb-0" style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
            My Recipes
          </h1>
        </div>
        <div className="d-flex gap-2">
          <Button
            onClick={handleCreateWithAI}
            variant="outline"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-robot me-1"></i> AI Create
          </Button>
          <Button
            onClick={handleCreateRecipe}
            variant="primary"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-plus-lg me-2"></i>
            Create
          </Button>
        </div>
      </div>

      {/* Search */}
      <Form onSubmit={handleSearchSubmit} className="mb-4">
        <InputGroup>
          <Form.Control
            type="text"
            placeholder="Search recipes by title, summary, ingredients..."
            value={searchQuery}
            onChange={handleSearchChange}
            disabled={loading}
          />
          <Button
            variant="primary"
            type="submit"
            disabled={loading || !searchQuery.trim()}
          >
            <i className="bi bi-search"></i>
          </Button>
        </InputGroup>
      </Form>

      {((isSearching || loading) && displayRecipes.length === 0 && searchQuery.trim()) ? (
        <Container className="py-5 text-center">
          <Spinner animation="border" variant="primary" role="status" className="mb-3">
            <span className="visually-hidden">Searching...</span>
          </Spinner>
          <p>Searching recipes...</p>
        </Container>
      ) : paginatedRecipes.length > 0 ? (
        <>
          {/* Recipes Grid */}
          <Row xs={1} md={2} lg={3} xxl={4} className="g-4 mb-4">
            {paginatedRecipes
              .filter((recipe) => recipe && recipe.id)
              .map((recipe) => (
                <Col key={recipe.id}>
                  <RecipeCard
                    recipe={recipe}
                    onView={() => handleViewRecipe(recipe.id!)}
                  />
                </Col>
              ))}
          </Row>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="d-flex justify-content-center">
              <Pagination>
                <Pagination.First
                  onClick={() => !loading && setCurrentPage(1)}
                  disabled={safeCurrentPage === 1 || loading}
                  aria-label="First"
                />
                <Pagination.Prev
                  onClick={() => !loading && setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={safeCurrentPage === 1 || loading}
                  aria-label="Previous"
                />
                {renderPaginationItems()}
                <Pagination.Next
                  onClick={() => !loading && setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={safeCurrentPage === totalPages || loading}
                  aria-label="Next"
                />
                <Pagination.Last
                  onClick={() => !loading && setCurrentPage(totalPages)}
                  disabled={safeCurrentPage === totalPages || loading}
                  aria-label="Last"
                />
              </Pagination>
            </div>
          )}
        </>
      ) : (
        /* Empty State */
        <Container className="py-5 text-center">
          <div className="mb-4">
            <i className="bi bi-book text-muted" style={{ fontSize: '4rem' }}></i>
          </div>
          <h3 className="mb-2">{searchQuery.trim() ? 'No recipes found' : 'No recipes yet'}</h3>
          <p className="text-muted mb-4">
            {searchQuery.trim() ? 'Try a different search term.' : 'Start by creating your first recipe!'}
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
            {searchQuery.trim() ? 'Create' : 'Create Your First Recipe'}
          </Button>
        </Container>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <RecipeFormModal
          isOpen={showCreateModal}
          onClose={handleCloseModal}
          onSuccess={handleRecipeCreated}
        />
      )}
    </Container>
  );
};
