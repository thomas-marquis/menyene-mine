import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    summary: '',
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'manual' | 'ai'>('manual');
  const [contentTab, setContentTab] = useState<'edit' | 'preview'>('edit');
  const [aiPrompt, setAiPrompt] = useState('');

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
    setActiveTab('manual');
    setContentTab('edit');
    setError(null);
    setAiPrompt('');
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

  const handleAiPromptChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setAiPrompt(e.target.value);
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
      setActiveTab('manual');
      setContentTab('edit');
      setAiPrompt('');
    }
  };

  const handleNavigateToAIGenerator = () => {
    // Close modal and navigate to AI generator
    onClose();
    navigate('/recipes/generate');
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title={isEditMode ? 'Edit Recipe' : 'Create New Recipe'}
      closeOnOverlayClick={!loading}
      closeOnEscape={!loading}
    >
      <div className={styles.modalContent}>
        {/* Creation Method Tabs */}
        {!isEditMode && (
          <div className={styles.creationTabs}>
            <div className={styles.tabs}>
              <button
                type="button"
                className={`${styles.tab} ${activeTab === 'manual' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('manual')}
                disabled={loading}
              >
                <i className="bi bi-pencil me-1"></i> Manual
              </button>
              <button
                type="button"
                className={`${styles.tab} ${activeTab === 'ai' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('ai')}
                disabled={loading}
              >
                <i className="bi bi-robot me-1"></i> AI-Assisted
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="alert alert-danger" role="alert">
            <strong>Error:</strong> {error}
          </div>
        )}

        {activeTab === 'manual' ? (
          <form onSubmit={handleSubmit} className={styles.form}>
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
                    className={`${styles.tab} ${contentTab === 'edit' ? styles.tabActive : ''}`}
                    onClick={() => setContentTab('edit')}
                    disabled={loading}
                  >
                    <i className="bi bi-pencil me-1"></i> Edit
                  </button>
                  <button
                    type="button"
                    className={`${styles.tab} ${contentTab === 'preview' ? styles.tabActive : ''}`}
                    onClick={() => setContentTab('preview')}
                    disabled={loading}
                  >
                    <i className="bi bi-eye me-1"></i> Preview
                  </button>
                </div>
                <div className={styles.tabContent}>
                  {contentTab === 'edit' ? (
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
        ) : (
          // AI-Assisted Tab
          <div className={styles.aiTabContent}>
            <div className={styles.aiDescription}>
              <p>
                <strong>AI-Assisted Recipe Creation</strong>
              </p>
              <p>
                Describe what you want to cook, and our AI will generate a complete recipe for you.
                You'll be able to review, edit, and validate the generated recipe before it's added to your catalog.
              </p>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="ai-prompt" className={styles.label}>
                Describe your recipe idea *
              </label>
              <textarea
                id="ai-prompt"
                value={aiPrompt}
                onChange={handleAiPromptChange}
                className="form-control"
                placeholder="e.g., Create a quick vegetarian pasta dish with tomatoes and basil..."
                rows={6}
                disabled={loading}
              />
              <div className={styles.aiHelp}>
                <small>
                  Be as specific as you like! The AI will generate a complete recipe based on your description.
                </small>
              </div>
            </div>

            <div className={styles.formActions}>
              <Button
                type="button"
                variant="secondary"
                onClick={() => setActiveTab('manual')}
                disabled={loading}
              >
                <i className="bi bi-arrow-left me-1"></i> Back to Manual
              </Button>
              <Button
                type="button"
                variant="primary"
                onClick={handleNavigateToAIGenerator}
                disabled={loading || !aiPrompt.trim()}
                className="ms-2"
              >
                <i className="bi bi-robot me-1"></i> Generate with AI
              </Button>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
};
