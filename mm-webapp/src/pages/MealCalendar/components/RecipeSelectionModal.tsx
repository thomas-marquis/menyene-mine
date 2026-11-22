import { useState } from 'react';
import { Button, Modal } from 'react-bootstrap';
import type { Meal, Recipe } from '../../../types';
import { RecipeContent } from '../../../components/recipe/RecipeContent';
import { RecipeCatalog } from '../../../components/recipe/RecipeCatalog';

/**
 * Props for the RecipeSelectionModal component
 */
interface RecipeSelectionModalProps {
  /** Whether the modal is visible */
  show: boolean;
  /** Callback to close the modal */
  close: () => void;
  /** Callback when a recipe is selected */
  onRecipeSelected: (recipe: Recipe) => void;
  /** The currently selected meal (contains date, moment, and recipe info) */
  selectedMeal: Meal | null;
}

/**
 * RecipeSelectionModal - A modal for selecting recipes for meal planning.
 * 
 * Displays a catalog of recipes with search functionality and allows selection
 * of a recipe for a specific meal slot.
 */
export const RecipeSelectionModal = ({show, close, onRecipeSelected: onRecipeSelect, selectedMeal}: RecipeSelectionModalProps) => {
  const [showRecipeDetails, setShowRecipeDetails] = useState<boolean>(false);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);

  const handleViewRecipeDetails = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setShowRecipeDetails(true);
  };

  const handleBackToSelection = () => {
    setShowRecipeDetails(false);
    setSelectedRecipe(null);
  };

  const handleRecipeSelect = (recipe: Recipe | null) => {
    if (recipe) {
      onRecipeSelect(recipe);
    }
  };

  return (
    <Modal
      show={show}
      onHide={() => {
        close();
        setShowRecipeDetails(false);
        setSelectedRecipe(null);
      }}
      size="lg"
      centered
    >
      <Modal.Header closeButton>
        <Modal.Title>
          {showRecipeDetails && selectedRecipe ? selectedRecipe.title : selectedMeal ? 'Change Meal' : 'Select Recipe'}
          {selectedMeal?.date && selectedMeal?.moment && !showRecipeDetails && (
            <span className="text-muted ms-2">
              ({selectedMeal.date} - {selectedMeal.moment})
            </span>
          )}
        </Modal.Title>
        {showRecipeDetails && selectedRecipe && (
          <div className="ms-auto d-flex gap-2">
            <Button variant="secondary" size="sm" onClick={handleBackToSelection}>
              <i className="bi bi-arrow-left me-1"></i>
              Back
            </Button>
            <Button variant="primary" size="sm" onClick={() => handleRecipeSelect(selectedRecipe)}>
              <i className="bi bi-check me-1"></i>
              Select
            </Button>
          </div>
        )}
      </Modal.Header>
      <Modal.Body>
        {showRecipeDetails && selectedRecipe ? (
          <RecipeContent
            title={selectedRecipe.title}
            summary={selectedRecipe.summary}
            ingredients={selectedRecipe.ingredients}
            instructions={selectedRecipe.instructions}
            servings={selectedRecipe.servings}
            prep_time={selectedRecipe.prep_time}
            cook_time={selectedRecipe.cook_time}
            difficulty={selectedRecipe.difficulty}
            showTitle={true}
            showSummary={true}
          />
        ) : (
          <RecipeCatalog
            onRecipeSelect={handleRecipeSelect}
            onRecipeView={handleViewRecipeDetails}
            selectedRecipeId={selectedMeal?.recipe_id || null}
            showSearch={true}
            showPagination={true}
            itemsPerPage={6}
            style={{ maxHeight: '500px', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}
          />
        )}
      </Modal.Body>
      <Modal.Footer>
        {!showRecipeDetails && (
          <Button variant="secondary" onClick={close}>
            Cancel
          </Button>
        )}
      </Modal.Footer>
    </Modal>
  );
};
