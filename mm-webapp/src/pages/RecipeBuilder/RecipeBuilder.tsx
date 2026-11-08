import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeDraftCard } from '../../components/recipe/RecipeDraftCard/RecipeDraftCard';
import { recipeDraftService } from '../../services/recipeDraftService';
import type { RecipeDraft } from '../../types/recipe_draft.types';
import styles from './RecipeBuilder.module.css';

export const RecipeBuilderPage = () => {
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [drafts, setDrafts] = useState<RecipeDraft[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [maxDrafts, setMaxDrafts] = useState(3);

  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
    setError(null);
  };

  const handleMaxDraftsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value, 10);
    if (!isNaN(value) && value >= 1 && value <= 10) {
      setMaxDrafts(value);
    }
  };

  const handleGenerate = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      
      if (!prompt.trim()) {
        setError('Please enter a prompt to generate recipes');
        return;
      }

      try {
        setIsGenerating(true);
        setError(null);
        setSuccessMessage(null);
        setDrafts([]);

        const newDrafts = await recipeDraftService.generateDrafts({
          prompt: prompt.trim(),
          max_drafts: maxDrafts,
        });

        setDrafts(newDrafts);
        setSuccessMessage(`Generated ${newDrafts.length} recipe draft(s)!`);
        setPrompt('');
      } catch (err: any) {
        if (err.response) {
          setError(err.response.data?.detail || 'Failed to generate recipes. Please try again.');
        } else if (err.request) {
          setError('Network error. Please check your connection.');
        } else {
          setError('Failed to generate recipes. Please try again.');
        }
        console.error('Error generating drafts:', err);
      } finally {
        setIsGenerating(false);
      }
    },
    [prompt, maxDrafts]
  );

  const handleViewAllDrafts = () => {
    navigate('/recipes/drafts');
  };

  const handleViewDraft = (draftId: number) => {
    navigate(`/recipes/drafts/${draftId}`);
  };

  const examplePrompts = [
    'Create a quick and easy pasta recipe for weeknight dinner',
    'Generate a healthy vegetarian salad recipe',
    'Make a traditional Italian lasagna recipe',
    'Create a spicy Thai curry recipe',
    'Generate a dessert recipe using chocolate and berries',
    'Create a gluten-free breakfast recipe',
    'Make a low-carb dinner recipe',
    'Generate a recipe for a summer barbecue',
  ];

  const handleUseExample = (example: string) => {
    setPrompt(example);
    setError(null);
  };

  return (
    <div className={styles.builderContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          <i className="bi bi-robot me-3"></i>
          AI Recipe Builder
        </h1>
        <p className={styles.subtitle}>
          Describe what you want to cook, and our AI will generate recipe ideas for you!
        </p>
      </div>

      {successMessage && (
        <div className="alert alert-success" role="alert">
          {successMessage}
        </div>
      )}

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      <div className={styles.generatorForm}>
        <form onSubmit={handleGenerate}>
          <div className="mb-3">
            <label htmlFor="prompt" className="form-label">
              <strong>Describe your recipe idea:</strong>
            </label>
            <textarea
              id="prompt"
              className="form-control"
              rows={4}
              value={prompt}
              onChange={handlePromptChange}
              placeholder="e.g., Create a quick vegetarian pasta dish with tomatoes and basil..."
              disabled={isGenerating}
            />
            <div className="form-text">
              Be as specific as you like! The AI will generate recipes based on your description.
            </div>
          </div>

          <div className="mb-3">
            <label htmlFor="maxDrafts" className="form-label">
              Number of recipes to generate (1-10):
            </label>
            <input
              type="number"
              id="maxDrafts"
              className="form-control"
              min={1}
              max={10}
              value={maxDrafts}
              onChange={handleMaxDraftsChange}
              disabled={isGenerating}
            />
          </div>

          <div className={styles.buttonGroup}>
            <Button
              type="submit"
              variant="primary"
              size="large"
              disabled={isGenerating || !prompt.trim()}
              loading={isGenerating}
            >
              <i className="bi bi-magic me-2"></i>
              {isGenerating ? 'Generating...' : 'Generate Recipes'}
            </Button>

            <Button
              type="button"
              variant="outline"
              size="large"
              onClick={handleViewAllDrafts}
              disabled={isGenerating}
            >
              <i className="bi bi-folder me-2"></i>
              View All Drafts
            </Button>
          </div>
        </form>
      </div>

      <div className={styles.examplesSection}>
        <h3 className={styles.examplesTitle}>
          <i className="bi bi-lightbulb me-2"></i>
          Need inspiration? Try these examples:
        </h3>
        <div className={styles.examplesGrid}>
          {examplePrompts.map((example, index) => (
            <button
              key={index}
              type="button"
              className={styles.exampleButton}
              onClick={() => handleUseExample(example)}
              disabled={isGenerating}
            >
              <i className="bi bi-arrow-right-circle me-2"></i>
              {example}
            </button>
          ))}
        </div>
      </div>

      {drafts.length > 0 && (
        <div className={styles.resultsSection}>
          <h2 className={styles.resultsTitle}>
            <i className="bi bi-file-earmark-text me-2"></i>
            Generated Recipe Drafts
          </h2>
          <p className={styles.resultsSubtitle}>
            Review the drafts below. Click on any draft to view details and validate or reject it.
          </p>

          <div className={styles.draftsGrid}>
            {drafts.map((draft) => (
              <RecipeDraftCard
                key={draft.id}
                draft={draft}
                onView={() => handleViewDraft(draft.id)}
              />
            ))}
          </div>

          <div className={styles.viewAllButton}>
            <Button
              variant="secondary"
              onClick={handleViewAllDrafts}
            >
              <i className="bi bi-folder-open me-2"></i>
              View All Drafts
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
