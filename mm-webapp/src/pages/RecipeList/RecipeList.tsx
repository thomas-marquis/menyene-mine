import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeCatalog } from '../../components/recipe/RecipeCatalog';
import { RecipeFormModal } from '../../components/recipe/RecipeFormModal/RecipeFormModal';
import type { Recipe } from '../../types/recipe.types';
import { Container, Alert } from 'react-bootstrap';

const ITEMS_PER_PAGE = 20;

export const RecipeListPage = () => {
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleViewRecipe = (recipe: Recipe) => {
    setError(null);
    setSuccessMessage(null);
    if (recipe.id && !isNaN(recipe.id)) {
      navigate(`/recipes/${recipe.id}`);
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
    setSuccessMessage('Recipe created successfully!');
    setTimeout(() => {
      setSuccessMessage(null);
    }, 3000);
  };

  return (
    <Container className="py-4">
      {successMessage && (
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
      )}
      
      {error && (
        <Alert variant="danger" className="mb-4">
          <strong>Error:</strong> {error}
        </Alert>
      )}
      
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
          >
            <i className="bi bi-robot me-1"></i> AI Create
          </Button>
          <Button
            onClick={handleCreateRecipe}
            variant="primary"
            size="md"
          >
            <i className="bi bi-plus-lg me-2"></i>
            Create
          </Button>
        </div>
      </div>

      <RecipeCatalog
        onRecipeView={handleViewRecipe}
        showSearch={true}
        showPagination={true}
        itemsPerPage={ITEMS_PER_PAGE}
        className="mb-4"
      />

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
