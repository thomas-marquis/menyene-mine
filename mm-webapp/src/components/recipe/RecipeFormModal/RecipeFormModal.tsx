import { useState, useEffect, useCallback, useRef } from 'react';
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

// Difficulty options
const DIFFICULTY_OPTIONS = ['Easy', 'Medium', 'Hard'];

export const RecipeFormModal = ({
  isOpen,
  onClose,
  onSuccess,
  recipe,
}: RecipeFormModalProps) => {
  const isEditMode = Boolean(recipe && recipe.id);

  // Form state with structured fields
  const [formData, setFormData] = useState({
    title: '',
    summary: '',
    ingredients: [''] as string[],
    instructions: [''] as string[],
    servings: 4,
    prep_time: '0 minutes',
    cook_time: '0 minutes',
    difficulty: 'Medium',
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Drag and drop state for instructions (mouse-based approach)
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [mousePosition, setMousePosition] = useState<[number, number]>([0, 0]);
  const [dropZoneIndex, setDropZoneIndex] = useState<number>(0);
  
  // Track mouse position
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      setMousePosition([e.clientX, e.clientY]);
    };
    document.addEventListener('mousemove', handler);
    return () => document.removeEventListener('mousemove', handler);
  }, []);

  // Find closest drop zone
  // We use data attributes instead of class names because CSS Modules hash class names
  useEffect(() => {
    if (draggedIndex !== null) {
      const elements = Array.from(document.querySelectorAll('[data-drop-zone-index]'));
      if (elements.length > 0) {
        // Get vertical positions of all drop zones
        const positions = elements.map((e: HTMLElement) => e.getBoundingClientRect().top);
        // Find which drop zone is closest to the mouse
        const absDifferences = positions.map((v: number) => Math.abs(v - mousePosition[1]));
        let closestDropZoneDomIndex = absDifferences.indexOf(Math.min(...absDifferences));
        
        // Get the actual drop zone index from the data attribute
        // This maps directly to the insertion position in the instructions array
        const closestElement = elements[closestDropZoneDomIndex] as HTMLElement;
        const closestDropZoneIndex = parseInt(closestElement.dataset.dropZoneIndex || '0');
        
        // Ensure the index is within bounds (0 to instructions.length)
        const boundedIndex = Math.max(0, Math.min(closestDropZoneIndex, formData.instructions.length));
        
        setDropZoneIndex(boundedIndex);
      }
    }
  }, [draggedIndex, mousePosition, formData.instructions.length]);

  // Drop item on mouse up
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (draggedIndex !== null) {
        e.preventDefault();
        setDraggedIndex(null);
        
        // Reorder the list
        setFormData((prev) => {
          const newInstructions = [...prev.instructions];
          let fromIndex = draggedIndex;
          let toIndex = dropZoneIndex;
          
          // Ensure indices are within bounds
          fromIndex = Math.max(0, Math.min(fromIndex, newInstructions.length - 1));
          toIndex = Math.max(0, Math.min(toIndex, newInstructions.length));
          
          if (fromIndex === toIndex) return prev;
          
          const reordered = reorderList(newInstructions, fromIndex, toIndex);
          return { ...prev, instructions: reordered };
        });
      }
    };
    document.addEventListener('mouseup', handler);
    return () => document.removeEventListener('mouseup', handler);
  }, [draggedIndex, dropZoneIndex]);

  // Helper function to reorder list
  const reorderList = useCallback((list: string[], start: number, end: number): string[] => {
    if (start === end) return list;
    
    const newList = [...list];
    if (start < end) {
      // Moving forward
      const temp = newList[start];
      for (let i = start; i < end; i++) {
        newList[i] = newList[i + 1];
      }
      newList[end - 1] = temp;
    } else {
      // Moving backward
      const temp = newList[start];
      for (let i = start; i > end; i--) {
        newList[i] = newList[i - 1];
      }
      newList[end] = temp;
    }
    return newList;
  }, []);

  // Initialize form with recipe data if editing
  useEffect(() => {
    if (recipe) {
      // Always ensure there's at least one empty row at the end
      let ingredients = recipe.ingredients && recipe.ingredients.length > 0
        ? [...recipe.ingredients]
        : [''];
      let instructions = recipe.instructions && recipe.instructions.length > 0
        ? [...recipe.instructions]
        : [''];
      
      // Add empty row at the end if the last item is not empty
      if (ingredients.length === 0 || ingredients[ingredients.length - 1].trim() !== '') {
        ingredients = [...ingredients, ''];
      }
      if (instructions.length === 0 || instructions[instructions.length - 1].trim() !== '') {
        instructions = [...instructions, ''];
      }
      
      setFormData({
        title: recipe.title || '',
        summary: recipe.summary || '',
        ingredients,
        instructions,
        servings: recipe.servings || 4,
        prep_time: recipe.prep_time || '0 minutes',
        cook_time: recipe.cook_time || '0 minutes',
        difficulty: recipe.difficulty || 'Medium',
      });
    } else {
      // Reset to defaults for new recipe
      setFormData({
        title: '',
        summary: '',
        ingredients: [''],
        instructions: [''],
        servings: 4,
        prep_time: '0 minutes',
        cook_time: '0 minutes',
        difficulty: 'Medium',
      });
    }
    setError(null);
  }, [recipe, isOpen]);

  // Handle input changes for text fields
  const handleTextChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value } = e.target;
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    },
    []
  );

  // Handle ingredient changes
  const handleIngredientChange = useCallback(
    (index: number, value: string) => {
      setFormData((prev) => {
        const newIngredients = [...prev.ingredients];
        newIngredients[index] = value;
        return { ...prev, ingredients: newIngredients };
      });
    },
    []
  );

  // Handle instruction changes
  const handleInstructionChange = useCallback(
    (index: number, value: string) => {
      setFormData((prev) => {
        const newInstructions = [...prev.instructions];
        newInstructions[index] = value;
        return { ...prev, instructions: newInstructions };
      });
    },
    []
  );

  // Add new ingredient line when user starts typing in the last empty line
  const handleIngredientInput = useCallback(
    (index: number, value: string) => {
      handleIngredientChange(index, value);
      // If this is the last ingredient and it has content, add a new empty line
      if (index === formData.ingredients.length - 1 && value.trim() !== '') {
        setFormData((prev) => ({
          ...prev,
          ingredients: [...prev.ingredients, ''],
        }));
      }
    },
    [formData.ingredients.length, handleIngredientChange]
  );

  // Add new instruction line when user starts typing in the last empty line
  const handleInstructionInput = useCallback(
    (index: number, value: string) => {
      handleInstructionChange(index, value);
      // If this is the last instruction and it has content, add a new empty line
      if (index === formData.instructions.length - 1 && value.trim() !== '') {
        setFormData((prev) => ({
          ...prev,
          instructions: [...prev.instructions, ''],
        }));
      }
    },
    [formData.instructions.length, handleInstructionChange]
  );

  // Remove ingredient line
  const removeIngredient = useCallback((index: number) => {
    if (formData.ingredients.length > 1) {
      setFormData((prev) => {
        const newIngredients = [...prev.ingredients];
        newIngredients.splice(index, 1);
        return { ...prev, ingredients: newIngredients };
      });
    }
  }, [formData.ingredients.length]);

  // Remove instruction line
  const removeInstruction = useCallback((index: number) => {
    if (formData.instructions.length > 1) {
      setFormData((prev) => {
        const newInstructions = [...prev.instructions];
        newInstructions.splice(index, 1);
        return { ...prev, instructions: newInstructions };
      });
    }
  }, [formData.instructions.length]);

  // Mouse-based drag start handler
  const handleMouseDown = useCallback((index: number, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggedIndex(index);
  }, []);

  const handleSubmit = async (e: React.SubmitEvent) => {
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

    // Validate at least one ingredient
    if (formData.ingredients.filter((ing) => ing.trim()).length === 0) {
      setError('At least one ingredient is required');
      return;
    }

    // Validate at least one instruction
    if (formData.instructions.filter((inst) => inst.trim()).length === 0) {
      setError('At least one instruction is required');
      return;
    }

    setLoading(true);

    try {
      // Prepare data for API - filter out empty strings
      const submitData: RecipeCreate | RecipeUpdate = {
        title: formData.title.trim(),
        summary: formData.summary.trim(),
        ingredients: formData.ingredients
          .map((ing) => ing.trim())
          .filter((ing) => ing !== ''),
        instructions: formData.instructions
          .map((inst) => inst.trim())
          .filter((inst) => inst !== ''),
        servings: formData.servings,
        prep_time: formData.prep_time,
        cook_time: formData.cook_time,
        difficulty: formData.difficulty,
      };

      if (isEditMode && recipe && recipe.id) {
        await recipeService.updateRecipe(recipe.id, submitData as RecipeUpdate);
      } else {
        await recipeService.createRecipe(submitData as RecipeCreate);
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
        summary: '',
        ingredients: [''],
        instructions: [''],
        servings: 4,
        prep_time: '0 minutes',
        cook_time: '0 minutes',
        difficulty: 'Medium',
      });
      setError(null);
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
      <div className={styles.modalContent}>
        {error && (
          <div className="alert alert-danger" role="alert">
            <strong>Error:</strong> {error}
          </div>
        )}

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
                onChange={handleTextChange}
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
                onChange={handleTextChange}
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

            {/* Ingredients Section */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Ingredients *
              </label>
              {formData.ingredients.map((ingredient, index) => (
                <div key={index} className={styles.ingredientRow}>
                  <div className={styles.ingredientInputContainer}>
                    <input
                      type="text"
                      value={ingredient}
                      onChange={(e) => handleIngredientInput(index, e.target.value)}
                      className="form-control"
                      placeholder={index === 0 ? "Enter an ingredient (e.g., 2 cups flour)" : "Enter another ingredient"}
                      disabled={loading}
                    />
                  </div>
                  {formData.ingredients.length > 1 && (
                    <button
                      type="button"
                      className={styles.removeButton}
                      onClick={() => removeIngredient(index)}
                      disabled={loading}
                      title="Remove ingredient"
                    >
                      <i className="bi bi-trash"></i>
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Instructions Section */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Instructions * (Drag to reorder)
              </label>
              
              {/* Floating dragged item */}
              {draggedIndex !== null && (
                <div
                  className={`${styles.instructionRow} ${styles.floating}`}
                  style={{
                    left: `${mousePosition[0]}px`,
                    top: `${mousePosition[1]}px`,
                    position: 'fixed',
                    zIndex: 1000,
                    pointerEvents: 'none',
                    boxShadow: '5px 5px 10px rgba(0,0,0,0.5)',
                  }}
                >
                  <div className={styles.instructionInputContainer}>
                    <div className={styles.stepNumber}>{draggedIndex + 1}.</div>
                    <div className={styles.dragHandle}>
                      <i className="bi bi-grip-vertical"></i>
                    </div>
                    <input
                      type="text"
                      value={formData.instructions[draggedIndex]}
                      className="form-control"
                      readOnly
                      style={{ background: 'white' }}
                    />
                  </div>
                </div>
              )}
              
              {/* Drop zone before all items */}
              <div
                className={`${styles.instructionDropZone} ${draggedIndex === null || dropZoneIndex !== 0 ? styles.hidden : ''}`}
                data-drop-zone-index={0}
              />
              
              {/* Instruction items */}
              {formData.instructions.map((instruction, originalIndex) => (
                <div key={originalIndex}>
                  {draggedIndex !== originalIndex && (
                    <>
                      <div
                        className={styles.instructionRow}
                        onMouseDown={(e) => handleMouseDown(originalIndex, e)}
                      >
                        <div className={styles.instructionInputContainer}>
                          <div className={styles.stepNumber}>{originalIndex + 1}.</div>
                          <div className={styles.dragHandle} title="Drag to reorder">
                            <i className="bi bi-grip-vertical"></i>
                          </div>
                          <input
                            type="text"
                            value={instruction}
                            onChange={(e) => handleInstructionInput(originalIndex, e.target.value)}
                            className="form-control"
                            placeholder={originalIndex === 0 ? "Enter first step" : "Enter next step"}
                            disabled={loading}
                          />
                        </div>
                        {formData.instructions.length > 1 && (
                          <button
                            type="button"
                            className={styles.removeButton}
                            onClick={() => removeInstruction(originalIndex)}
                            disabled={loading}
                            title="Remove step"
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        )}
                      </div>
                      {/* Drop zone after each item - use originalIndex + 1 */}
                      <div
                        className={`${styles.instructionDropZone} ${draggedIndex === null || dropZoneIndex !== originalIndex + 1 ? styles.hidden : ''}`}
                        data-drop-zone-index={originalIndex + 1}
                      />
                    </>
                  )}
                </div>
              ))}
            </div>

            {/* Metadata Section */}
            <div className={styles.metadataSection}>
              <h4 className={styles.metadataTitle}>Recipe Details</h4>
              
              <div className={styles.metadataGrid}>
                <div className={styles.formGroup}>
                  <label htmlFor="servings" className={styles.label}>
                    Servings
                  </label>
                  <input
                    type="number"
                    id="servings"
                    name="servings"
                    value={formData.servings}
                    onChange={handleTextChange}
                    className="form-control"
                    min={1}
                    max={100}
                    disabled={loading}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor="difficulty" className={styles.label}>
                    Difficulty
                  </label>
                  <select
                    id="difficulty"
                    name="difficulty"
                    value={formData.difficulty}
                    onChange={handleTextChange}
                    className="form-control"
                    disabled={loading}
                  >
                    {DIFFICULTY_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor="prep_time" className={styles.label}>
                    Prep Time
                  </label>
                  <input
                    type="text"
                    id="prep_time"
                    name="prep_time"
                    value={formData.prep_time}
                    onChange={handleTextChange}
                    className="form-control"
                    placeholder="e.g., 20 minutes"
                    disabled={loading}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label htmlFor="cook_time" className={styles.label}>
                    Cook Time
                  </label>
                  <input
                    type="text"
                    id="cook_time"
                    name="cook_time"
                    value={formData.cook_time}
                    onChange={handleTextChange}
                    className="form-control"
                    placeholder="e.g., 30 minutes"
                    disabled={loading}
                  />
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
       </div>
    </Modal>
  );
};
