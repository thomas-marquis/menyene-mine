import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { recipeDraftService } from '../../services/recipeDraftService';
import { recipeService } from '../../services/recipeService';
import type { RecipeDraft } from '../../types/recipe_draft.types';
import type { Recipe } from '../../types/recipe.types';
import styles from './DraftDetail.module.css';

export const DraftDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [draft, setDraft] = useState<RecipeDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);
  const [showConfirmValidate, setShowConfirmValidate] = useState(false);
  const [showConfirmReject, setShowConfirmReject] = useState(false);

  const fetchDraft = useCallback(async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const draftData = await recipeDraftService.getDraftById(parseInt(id, 10));
      setDraft(draftData);
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe draft not found.');
      } else if (err.response) {
        setError('Failed to fetch draft. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch draft. Please try again later.');
      }
      console.error('Error fetching draft:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDraft();
  }, [fetchDraft]);

  useEffect(() => {
    if (id && isNaN(parseInt(id, 10))) {
      navigate('/404');
    }
  }, [id, navigate]);

  const handleGoBack = () => {
    navigate('/recipes/drafts');
  };

  const handleValidate = async () => {
    if (!id || !draft) return;

    try {
      setIsValidating(true);
      setError(null);
      setShowConfirmValidate(false);

      const response = await recipeDraftService.validateDraft(parseInt(id, 10));
      
      if (response.success && response.recipe) {
        setSuccessMessage('Draft validated and recipe created successfully!');
        setDraft({ ...draft, status: 'validated', recipe_id: response.recipe.id });
        
        // Refresh draft to get updated status
        await fetchDraft();
        
        setTimeout(() => {
          setSuccessMessage(null);
          // Navigate to the new recipe after a delay
          if (response.recipe && response.recipe.id) {
            navigate(`/recipes/${response.recipe.id}`);
          }
        }, 2000);
      } else {
        setError('Failed to validate draft. Please try again.');
      }
    } catch (err: any) {
      setError('Failed to validate draft. Please try again.');
      console.error('Error validating draft:', err);
    } finally {
      setIsValidating(false);
    }
  };

  const handleReject = async () => {
    if (!id || !draft) return;

    try {
      setIsRejecting(true);
      setError(null);
      setShowConfirmReject(false);

      const response = await recipeDraftService.rejectDraft(parseInt(id, 10));
      
      if (response.success) {
        setSuccessMessage('Draft rejected successfully!');
        setDraft({ ...draft, status: 'rejected' });
        setTimeout(() => setSuccessMessage(null), 3000);
      } else {
        setError('Failed to reject draft. Please try again.');
      }
    } catch (err: any) {
      setError('Failed to reject draft. Please try again.');
      console.error('Error rejecting draft:', err);
    } finally {
      setIsRejecting(false);
    }
  };

  const handleDelete = async () => {
    if (!id || !draft) return;

    if (window.confirm('Are you sure you want to delete this draft? This action cannot be undone.')) {
      try {
        await recipeDraftService.deleteDraft(parseInt(id, 10));
        setSuccessMessage('Draft deleted successfully!');
        setTimeout(() => {
          navigate('/recipes/drafts');
        }, 1500);
      } catch (err: any) {
        setError('Failed to delete draft. Please try again.');
        console.error('Error deleting draft:', err);
      }
    }
  };

  const handleViewRecipe = async () => {
    if (!draft || !draft.recipe_id) return;

    try {
      const recipe = await recipeService.getRecipeById(draft.recipe_id);
      navigate(`/recipes/${recipe.id}`);
    } catch (err) {
      setError('Failed to load recipe. It may have been deleted.');
      console.error('Error loading recipe:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'validated':
        return <span className="badge bg-success">Validated</span>;
      case 'rejected':
        return <span className="badge bg-danger">Rejected</span>;
      default:
        return <span className="badge bg-warning text-dark">Draft</span>;
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderRecipeContent = () => {
    if (!draft) return null;

    const content = draft.generated_content;
    const title = content.title || 'Untitled Recipe';
    const summary = content.summary || 'No summary available';
    const recipeContent = content.content || 'No content available';

    return (
      <div className={styles.content}>
        <h2 className={styles.contentTitle}>{title}</h2>
        
        <div className={styles.summary}>
          <h3>Summary</h3>
          <p>{summary}</p>
        </div>

        <div className={styles.recipeDetails}>
          <h3>Recipe Details</h3>
          <div 
            className={styles.markdownContent}
            dangerouslySetInnerHTML={{ __html: renderMarkdown(recipeContent) }}
          />
        </div>

        {content.ingredients && content.ingredients.length > 0 && (
          <div className={styles.ingredients}>
            <h3>Ingredients</h3>
            <ul>
              {content.ingredients.map((ingredient: string, index: number) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>
          </div>
        )}

        {content.instructions && content.instructions.length > 0 && (
          <div className={styles.instructions}>
            <h3>Instructions</h3>
            <ol>
              {content.instructions.map((instruction: string, index: number) => (
                <li key={index}>{instruction}</li>
              ))}
            </ol>
          </div>
        )}

        {content.servings && (
          <div className={styles.meta}>
            <span><strong>Servings:</strong> {content.servings}</span>
            {content.prep_time && <span><strong>Prep Time:</strong> {content.prep_time}</span>}
            {content.cook_time && <span><strong>Cook Time:</strong> {content.cook_time}</span>}
            {content.difficulty && <span><strong>Difficulty:</strong> {content.difficulty}</span>}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading draft...</p>
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
          <Button onClick={() => fetchDraft()} variant="primary" disabled={loading}>
            {loading ? 'Loading...' : 'Retry'}
          </Button>
          <Button onClick={handleGoBack} variant="secondary" disabled={loading} className="ms-2">
            Back to Drafts
          </Button>
        </div>
      </div>
    );
  }

  if (!draft) {
    return (
      <div className={styles.errorContainer}>
        <div className="alert alert-warning" role="alert">
          Recipe draft not found
        </div>
        <Button onClick={handleGoBack} variant="secondary">
          Back to Drafts
        </Button>
      </div>
    );
  }

  return (
    <div className={styles.detailContainer}>
      <div className={styles.header}>
        <Button onClick={handleGoBack} variant="outline" size="medium" disabled={loading}>
          <i className="bi bi-arrow-left me-2"></i>
          Back to Drafts
        </Button>
        
        <div className={styles.actionButtons}>
          {draft.status === 'draft' && (
            <>
              <Button
                onClick={() => setShowConfirmReject(true)}
                variant="danger"
                size="medium"
                disabled={isValidating || isRejecting}
              >
                <i className="bi bi-x-circle me-2"></i>
                Reject
              </Button>
              <Button
                onClick={() => setShowConfirmValidate(true)}
                variant="success"
                size="medium"
                className="ms-2"
                disabled={isValidating || isRejecting}
              >
                <i className="bi bi-check-circle me-2"></i>
                Validate & Create Recipe
              </Button>
            </>
          )}
          
          {draft.status === 'validated' && draft.recipe_id && (
            <Button
              onClick={handleViewRecipe}
              variant="primary"
              size="medium"
            >
              <i className="bi bi-eye me-2"></i>
              View Recipe
            </Button>
          )}
          
          <Button
            onClick={handleDelete}
            variant="outline"
            size="medium"
            className="ms-2"
            disabled={isValidating || isRejecting}
          >
            <i className="bi bi-trash me-2"></i>
            Delete
          </Button>
        </div>
      </div>

      {successMessage && (
        <div className="alert alert-success" role="alert">
          {successMessage}
        </div>
      )}

      <div className={styles.meta}>
        <h1 className={styles.title}>
          Draft #{draft.id}
        </h1>
        <div className={styles.status}>
          {getStatusBadge(draft.status)}
        </div>
      </div>

      <div className={styles.info}>
        <div className={styles.infoItem}>
          <span className={styles.infoLabel}>Created:</span>
          <span className={styles.infoValue}>{formatDate(draft.created_at)}</span>
        </div>
        <div className={styles.infoItem}>
          <span className={styles.infoLabel}>Updated:</span>
          <span className={styles.infoValue}>{formatDate(draft.updated_at)}</span>
        </div>
        {draft.recipe_id && (
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Recipe ID:</span>
            <span className={styles.infoValue}>{draft.recipe_id}</span>
          </div>
        )}
      </div>

      <div className={styles.promptSection}>
        <h3>User Prompt</h3>
        <div className={styles.promptContent}>
          <p>{draft.user_prompt}</p>
        </div>
      </div>

      {renderRecipeContent()}

      {/* Confirmation Modals */}
      {showConfirmValidate && (
        <div className="modal show" style={{ display: 'block' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Confirm Validation</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowConfirmValidate(false)}
                ></button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to validate this draft and create a recipe from it?</p>
                <p className="text-muted">
                  This will create a new recipe in your catalog with the title: 
                  <strong>{draft.generated_content.title || 'Untitled Recipe'}</strong>
                </p>
              </div>
              <div className="modal-footer">
                <Button
                  onClick={() => setShowConfirmValidate(false)}
                  variant="secondary"
                  disabled={isValidating}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleValidate}
                  variant="success"
                  className="ms-2"
                  loading={isValidating}
                  disabled={isValidating}
                >
                  {isValidating ? 'Validating...' : 'Validate & Create Recipe'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showConfirmReject && (
        <div className="modal show" style={{ display: 'block' }}>
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Confirm Rejection</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowConfirmReject(false)}
                ></button>
              </div>
              <div className="modal-body">
                <p>Are you sure you want to reject this draft?</p>
                <p className="text-muted">
                  You can still view it later in the "Rejected" tab, but it won't be created as a recipe.
                </p>
              </div>
              <div className="modal-footer">
                <Button
                  onClick={() => setShowConfirmReject(false)}
                  variant="secondary"
                  disabled={isRejecting}
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleReject}
                  variant="danger"
                  className="ms-2"
                  loading={isRejecting}
                  disabled={isRejecting}
                >
                  {isRejecting ? 'Rejecting...' : 'Reject Draft'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Simple markdown to HTML renderer
function renderMarkdown(markdown: string): string {
  if (!markdown || markdown.trim() === '') {
    return '<p>No content available</p>';
  }

  const lines = markdown.split('\n');
  let html = '';
  let inList = false;
  let inOrderedList = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();

    if (trimmedLine === '') {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inOrderedList) {
        html += '</ol>';
        inOrderedList = false;
      }
      continue;
    }

    // Headers
    if (trimmedLine.startsWith('# ')) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inOrderedList) {
        html += '</ol>';
        inOrderedList = false;
      }
      html += `<h1>${trimmedLine.substring(2)}</h1>`;
      continue;
    }
    if (trimmedLine.startsWith('## ')) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inOrderedList) {
        html += '</ol>';
        inOrderedList = false;
      }
      html += `<h2>${trimmedLine.substring(3)}</h2>`;
      continue;
    }
    if (trimmedLine.startsWith('### ')) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inOrderedList) {
        html += '</ol>';
        inOrderedList = false;
      }
      html += `<h3>${trimmedLine.substring(4)}</h3>`;
      continue;
    }

    // Unordered lists
    if (trimmedLine.startsWith('- ')) {
      if (!inList && !inOrderedList) {
        html += '<ul>';
        inList = true;
      } else if (inOrderedList) {
        html += '</ol><ul>';
        inOrderedList = false;
        inList = true;
      }
      html += `<li>${trimmedLine.substring(2)}</li>`;
      continue;
    }

    // Ordered lists
    if (/^\d+\. /.test(trimmedLine)) {
      if (!inOrderedList && !inList) {
        html += '<ol>';
        inOrderedList = true;
      } else if (inList) {
        html += '</ul><ol>';
        inList = false;
        inOrderedList = true;
      }
      const content = trimmedLine.replace(/^\d+\. /, '');
      html += `<li>${content}</li>`;
      continue;
    }

    if (inList) {
      html += '</ul>';
      inList = false;
    }
    if (inOrderedList) {
      html += '</ol>';
      inOrderedList = false;
    }

    let processedLine = trimmedLine
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

    html += `<p>${processedLine}</p>`;
  }

  if (inList) {
    html += '</ul>';
  }
  if (inOrderedList) {
    html += '</ol>';
  }

  return html;
}
