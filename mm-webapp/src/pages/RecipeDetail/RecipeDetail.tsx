import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeContent } from '../../components/recipe/RecipeContent';
import { RecipeFormModal } from '../../components/recipe/RecipeFormModal/RecipeFormModal';
import { recipeService } from '../../services/recipeService';
import type { Recipe } from '../../types/recipe.types';
import styles from './RecipeDetail.module.css';

export const RecipeDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
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
      <div className={styles.loadingContainer}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading recipe...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
        <div className={styles.errorActions}>
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
          <Button onClick={handleGoBack} variant="secondary" disabled={loading} className="ms-2">
            Back to Recipes
          </Button>
        </div>
      </div>
    );
  }

  if (successMessage && !recipe) {
    return (
      <div className={styles.successContainer}>
        <div className="alert alert-success" role="alert">
          {successMessage}
        </div>
        <Button onClick={() => navigate('/')} variant="primary">
          Back to Recipes
        </Button>
      </div>
    );
  }

  if (!recipe) {
    return (
      <div className={styles.errorContainer}>
        <div className="alert alert-warning" role="alert">
          Recipe not found
        </div>
        <Button onClick={handleGoBack} variant="secondary" disabled={loading}>
          Back to Recipes
        </Button>
      </div>
    );
  }

  return (
    <div className={styles.recipeDetailContainer}>
      <div className={styles.header}>
        <Button
          onClick={handleGoBack}
          variant="outline"
          size="medium"
          disabled={loading}
        >
          <i className="bi bi-arrow-left me-2"></i>
          Back to Recipes
        </Button>
        <div className={styles.actionButtons}>
          <Button
            onClick={handleEdit}
            variant="secondary"
            size="medium"
            disabled={loading}
          >
            <i className="bi bi-pencil me-2"></i>
            Edit
          </Button>
          <Button
            onClick={handleDelete}
            variant="danger"
            size="medium"
            className="ms-2"
            disabled={loading}
          >
            <i className="bi bi-trash me-2"></i>
            Delete
          </Button>
        </div>
      </div>

      <div className={styles.recipeContent}>
        {successMessage && (
          <div className="alert alert-success" role="alert">
            {successMessage}
          </div>
        )}
        <h1 className={styles.title}>{recipe.title}</h1>

        <div className={styles.meta}>
          <span className={styles.date}>
            <i className="bi bi-calendar me-2"></i>
            Created: {formatDate(recipe.creation_date)}
          </span>
          <span className={styles.date}>
            <i className="bi bi-clock me-2"></i>
            Updated: {formatDate(recipe.last_updated)}
          </span>
        </div>

        <div className={styles.summary}>
          <p>{recipe.summary}</p>
        </div>

        <div className={styles.content}>
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

      {showEditModal && (
        <RecipeFormModal
          isOpen={showEditModal}
          onClose={handleCloseEditModal}
          onSuccess={handleRecipeUpdated}
          recipe={recipe}
        />
      )}

      {showDeleteConfirm && (
        <div className="modal show" style={{ display: 'block' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Confirm Deletion</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={handleCloseDeleteConfirm}
                ></button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to delete "{recipe.title}"? This action cannot be undone.</p>
              </div>
              <div className="modal-footer">
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
                  className="ms-2"
                  loading={deleting}
                  disabled={deleting}
                >
                  Delete
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
