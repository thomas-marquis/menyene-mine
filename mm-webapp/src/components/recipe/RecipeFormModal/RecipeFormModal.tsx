import { useState, useEffect, useCallback } from 'react';
import { Button } from '../../common/Button/Button';
import { Modal } from '../../common/Modal/Modal';
import { recipeService } from '../../../services/recipeService';
import type { Recipe, RecipeCreate, RecipeUpdate } from '../../../types/recipe.types';
import styles from './RecipeFormModal.module.css';

interface RecipeFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  recipe?: Recipe | null;
}

// Simple markdown to HTML renderer for preview
function renderMarkdownPreview(markdown: string): string {
  if (!markdown || markdown.trim() === '') {
    return '<p>Preview will appear here...</p>';
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
      if (inList) html += '</ul>';
      if (inOrderedList) html += '</ol>';
      inList = false;
      inOrderedList = false;
      html += `<h1>${trimmedLine.substring(2)}</h1>`;
      continue;
    }
    if (trimmedLine.startsWith('## ')) {
      if (inList) html += '</ul>';
      if (inOrderedList) html += '</ol>';
      inList = false;
      inOrderedList = false;
      html += `<h2>${trimmedLine.substring(3)}</h2>`;
      continue;
    }
    if (trimmedLine.startsWith('### ')) {
      if (inList) html += '</ul>';
      if (inOrderedList) html += '</ol>';
      inList = false;
      inOrderedList = false;
      html += `<h3>${trimmedLine.substring(4)}</h3>`;
      continue;
    }

    // Lists
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

  if (inList) html += '</ul>';
  if (inOrderedList) html += '</ol>';

  return html;
}

export const RecipeFormModal = ({
  isOpen,
  onClose,
  onSuccess,
  recipe,
}: RecipeFormModalProps) => {
  const isEditMode = Boolean(recipe && recipe.id);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    summary: '',
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'edit' | 'preview'>('edit');

  useEffect(() => {
    if (recipe) {
      setFormData({
        title: recipe.title || '',
        content: recipe.content || '',
        summary: recipe.summary || '',
      });
    } else {
      setFormData({
        title: '',
        content: '',
        summary: '',
      });
    }
    setActiveTab('edit');
    setError(null);
  }, [recipe, isOpen]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const { name, value } = e.target;
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    },
    []
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate form
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }

    if (formData.title.length > 255) {
      setError('Title must be less than 255 characters');
      return;
    }

    if (!formData.summary.trim()) {
      setError('Summary is required');
      return;
    }

    if (formData.summary.length > 500) {
      setError('Summary must be less than 500 characters');
      return;
    }

    if (!formData.content.trim()) {
      setError('Content is required');
      return;
    }

    setLoading(true);

    try {
      if (isEditMode && recipe && recipe.id) {
        const updateData: RecipeUpdate = {
          title: formData.title.trim(),
          content: formData.content.trim(),
          summary: formData.summary.trim(),
        };
        await recipeService.updateRecipe(recipe.id, updateData);
      } else {
        const createData: RecipeCreate = {
          title: formData.title.trim(),
          content: formData.content.trim(),
          summary: formData.summary.trim(),
        };
        await recipeService.createRecipe(createData);
      }
      onSuccess();
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe not found.');
      } else if (err.response && err.response.data && err.response.data.detail) {
        // Handle validation errors from backend
        const errorMessages = err.response.data.detail;
        if (Array.isArray(errorMessages)) {
          setError(errorMessages.map((e: any) => e.msg || e.message || 'Validation error').join(', '));
        } else if (typeof errorMessages === 'string') {
          setError(errorMessages);
        } else {
          setError('Failed to save recipe. Please try again.');
        }
      } else if (err.response) {
        setError('Failed to save recipe. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to save recipe. Please try again.');
      }
      console.error('Error saving recipe:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
      setFormData({
        title: '',
        content: '',
        summary: '',
      });
      setError(null);
      setActiveTab('edit');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={isEditMode ? 'Edit Recipe' : 'Create New Recipe'}
      closeOnOverlayClick={!loading}
      closeOnEscape={!loading}
    >
      <form onSubmit={handleSubmit} className={styles.form}>
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        <div className={styles.formGroup}>
          <label htmlFor="title" className={styles.label}>
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="form-control"
            placeholder="Enter recipe title"
            maxLength={255}
            disabled={loading}
          />
          <div className={styles.charCount}>
            {formData.title.length}/255 characters
          </div>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="summary" className={styles.label}>
            Summary * (max 500 characters)
          </label>
          <textarea
            id="summary"
            name="summary"
            value={formData.summary}
            onChange={handleChange}
            className="form-control"
            placeholder="Enter a brief summary of the recipe"
            rows={3}
            maxLength={500}
            disabled={loading}
          />
          <div className={styles.charCount}>
            {formData.summary.length}/500 characters
          </div>
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="content" className={styles.label}>
            Content * (Markdown supported)
          </label>
          <div className={styles.tabContainer}>
            <div className={styles.tabs}>
              <button
                type="button"
                className={`${styles.tab} ${activeTab === 'edit' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('edit')}
                disabled={loading}
              >
                <i className="bi bi-pencil me-1"></i> Edit
              </button>
              <button
                type="button"
                className={`${styles.tab} ${activeTab === 'preview' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('preview')}
                disabled={loading}
              >
                <i className="bi bi-eye me-1"></i> Preview
              </button>
            </div>
            <div className={styles.tabContent}>
              {activeTab === 'edit' ? (
                <>
                  <textarea
                    id="content"
                    name="content"
                    value={formData.content}
                    onChange={handleChange}
                    className="form-control"
                    placeholder="Enter recipe content in markdown format..."
                    rows={10}
                    disabled={loading}
                  />
                  <div className={styles.markdownHelp}>
                    <small>
                      Supports: <code># Headers</code>, <code>**bold**</code>,{' '}
                      <code>*italic*</code>, <code>- Lists</code>,{' '}
                      <code>[links](url)</code>
                    </small>
                  </div>
                </>
              ) : (
                <div
                  className={styles.previewContent}
                  dangerouslySetInnerHTML={{
                    __html: renderMarkdownPreview(formData.content),
                  }}
                />
              )}
            </div>
          </div>
        </div>

        <div className={styles.formActions}>
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            disabled={loading}
            className="ms-2"
          >
            {isEditMode ? 'Update Recipe' : 'Create Recipe'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};
