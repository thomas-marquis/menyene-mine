import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { Modal } from '../../components/common/Modal/Modal';
import { RecipeContent } from '../../components/recipe/RecipeContent';
import { RecipeFormModal } from '../../components/recipe/RecipeFormModal/RecipeFormModal';
import { recipeService } from '../../services/recipeService';
import type { Recipe } from '../../types/recipe.types';
import { Container, Alert, Spinner, Badge } from 'react-bootstrap';
import { useAppDispatch } from '../../store';
import { decrementRecipeCount } from '../../store/statsSlice';

export const RecipeDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  // Check if ID is valid
  useEffect(() => {
    if (id && isNaN(parseInt(id, 10))) {
      navigate('/404');
    }
  }, [id, navigate]);
  
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<boolean>(false);

  const fetchRecipe = useCallback(async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      const recipeData = await recipeService.getRecipeById(parseInt(id, 10));
      setRecipe(recipeData);
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe not found.');
      } else if (err.response) {
        setError('Failed to fetch recipe. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch recipe. Please try again later.');
      }
      console.error('Error fetching recipe:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchRecipe();
  }, [fetchRecipe]);

  useEffect(() => {
    setSuccessMessage(null);
  }, [id]);

  const handleGoBack = () => {
    setError(null);
    setSuccessMessage(null);
    navigate('/');
  };

  const handleEdit = () => {
    if (recipe) {
      setError(null);
      setShowEditModal(true);
    }
  };

  const handleDelete = () => {
    if (recipe) {
      setError(null);
      setShowDeleteConfirm(true);
    }
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setError(null);
  };

  const handleRecipeUpdated = () => {
    setShowEditModal(false);
    setError(null);
    fetchRecipe();
    setSuccessMessage('Recipe updated successfully!');
    setTimeout(() => {
      setSuccessMessage(null);
    }, 3000);
  };

  const handleCloseDeleteConfirm = () => {
    setShowDeleteConfirm(false);
    setError(null);
  };

  const handleConfirmDelete = async () => {
    if (!id) return;

    setDeleting(true);
    setError(null);
    try {
      await recipeService.deleteRecipe(parseInt(id, 10));
      dispatch(decrementRecipeCount());
      setSuccessMessage('Recipe deleted successfully!');
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe not found.');
      } else if (err.response) {
        setError('Failed to delete recipe. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to delete recipe. Please try again.');
      }
      console.error('Error deleting recipe:', err);
    } finally {
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" role="status" className="mb-3">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p>Loading recipe...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
        <div className="d-flex justify-content-center gap-2">
          <Button
            onClick={() => {
              setError(null);
              fetchRecipe();
            }}
            variant="primary"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Retry'}
          </Button>
          <Button onClick={handleGoBack} variant="secondary" disabled={loading}>
            Back to Recipes
          </Button>
        </div>
      </Container>
    );
  }

  if (successMessage && !recipe) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
        <Button onClick={() => navigate('/')} variant="primary">
          Back to Recipes
        </Button>
      </Container>
    );
  }

  if (!recipe) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="warning" className="mb-4">
          Recipe not found
        </Alert>
        <Button onClick={handleGoBack} variant="secondary" disabled={loading}>
          Back to Recipes
        </Button>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      {/* Header with actions */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3">
        <Button
          onClick={handleGoBack}
          variant="outline"
          size="md"
          disabled={loading}
        >
          <i className="bi bi-arrow-left me-2"></i>
          Back to Recipes
        </Button>
        <div className="d-flex gap-2">
          <Button
            onClick={handleEdit}
            variant="secondary"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-pencil me-2"></i>
            Edit
          </Button>
          <Button
            onClick={handleDelete}
            variant="danger"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-trash me-2"></i>
            Delete
          </Button>
        </div>
      </div>

      {/* Recipe Content */}
      <div className="mb-4">
        {successMessage && (
          <Alert variant="success" className="mb-4">
            {successMessage}
          </Alert>
        )}
        
        <h1 className="mb-3" style={{ fontSize: '2.5rem', fontWeight: 700, color: '#2c3e50' }}>
          {recipe.title}
        </h1>

        <div className="d-flex flex-wrap gap-3 mb-4 text-muted small">
          <Badge bg="light" text="secondary" className="p-2">
            <i className="bi bi-calendar me-2"></i>
            Created: {formatDate(recipe.creation_date)}
          </Badge>
          <Badge bg="light" text="secondary" className="p-2">
            <i className="bi bi-clock me-2"></i>
            Updated: {formatDate(recipe.last_updated)}
          </Badge>
        </div>

        <div className="mb-4">
          <p className="lead" style={{ color: '#7f8c8d' }}>
            {recipe.summary}
          </p>
        </div>

        <div className="border-top pt-4">
          <RecipeContent
            title={recipe.title}
            summary={recipe.summary}
            ingredients={recipe.ingredients}
            instructions={recipe.instructions}
            servings={recipe.servings}
            prep_time={recipe.prep_time}
            cook_time={recipe.cook_time}
            difficulty={recipe.difficulty}
            showTitle={false}
            showSummary={false}
          />
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <RecipeFormModal
          isOpen={showEditModal}
          onClose={handleCloseEditModal}
          onSuccess={handleRecipeUpdated}
          recipe={recipe}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <Modal
          isOpen={showDeleteConfirm}
          onClose={handleCloseDeleteConfirm}
          title="Confirm Deletion"
          closeOnOverlayClick={!deleting}
          closeOnEscape={!deleting}
        >
          <p>Are you sure you want to delete "{recipe.title}"? This action cannot be undone.</p>
          <div className="d-flex justify-content-end gap-2 mt-4">
            <Button
              onClick={handleCloseDeleteConfirm}
              variant="secondary"
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmDelete}
              variant="danger"
              loading={deleting}
              disabled={deleting}
            >
              Delete
            </Button>
          </div>
        </Modal>
      )}
    </Container>
  );
};
