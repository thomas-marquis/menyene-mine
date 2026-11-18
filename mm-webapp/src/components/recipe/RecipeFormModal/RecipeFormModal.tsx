import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '../../common/Button/Button';
import { Modal } from '../../common/Modal/Modal';
import { recipeService } from '../../../services/recipeService';
import type { Recipe, RecipeCreate, RecipeUpdate } from '../../../types/recipe.types';
import { Form, InputGroup, Row, Col, Alert, Badge } from 'react-bootstrap';

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
  
  // Drag and drop state for instructions
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  const [mousePosition, setMousePosition] = useState<[number, number]>([0, 0]);
  const instructionItemRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Track mouse position
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      setMousePosition([e.clientX, e.clientY]);
      
      // If dragging, find where to insert
      if (draggedIndex !== null && instructionItemRefs.current.length > 0) {
        let newDragOverIndex: number | null = null;
        let minDistance = Infinity;
        
        instructionItemRefs.current.forEach((ref: HTMLDivElement | null, index: number) => {
          if (ref && index !== draggedIndex) {  // Skip the dragged item
            const rect = ref.getBoundingClientRect();
            const top = rect.top;
            const bottom = rect.bottom;
            
            // Check if mouse is within this item's bounds
            if (e.clientY >= top && e.clientY <= bottom) {
              const distance = Math.min(Math.abs(e.clientY - top), Math.abs(e.clientY - bottom));
              if (distance < minDistance) {
                minDistance = distance;
                // If mouse is in the top half, insert before; otherwise after
                newDragOverIndex = e.clientY < (top + rect.height / 2) ? index : index + 1;
              }
            }
          }
        });
        
        setDragOverIndex(newDragOverIndex);
      }
    };
    document.addEventListener('mousemove', handler);
    return () => document.removeEventListener('mousemove', handler);
  }, [draggedIndex]);

  // Handle mouse down on drag handle
  const handleMouseDown = (index: number, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggedIndex(index);
    document.body.style.cursor = 'grabbing';
  };

  // Handle mouse up (drop)
  useEffect(() => {
    const handleMouseUp = () => {
      if (draggedIndex !== null && dragOverIndex !== null && draggedIndex !== dragOverIndex) {
        // Calculate the actual insertion index
        // If dragging down (draggedIndex < dragOverIndex), insert before dragOverIndex
        // If dragging up (draggedIndex > dragOverIndex), insert after dragOverIndex
        let insertAt = dragOverIndex;
        if (draggedIndex > dragOverIndex) {
          // Dragging up: if mouse is below midpoint, insert after; otherwise before
          // But since we're using closest midpoint, we need to check the position
          // Actually, since all items are still in the DOM, we just use dragOverIndex directly
          insertAt = dragOverIndex;
        }
        
        setFormData((prev) => {
          const newInstructions = [...prev.instructions];
          const [removed] = newInstructions.splice(draggedIndex, 1);
          newInstructions.splice(insertAt, 0, removed);
          return { ...prev, instructions: newInstructions };
        });
      }
      setDraggedIndex(null);
      setDragOverIndex(null);
      document.body.style.cursor = '';
    };
    
    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, [draggedIndex, dragOverIndex]);

  // Initialize refs
  useEffect(() => {
    instructionItemRefs.current = instructionItemRefs.current.slice(0, formData.instructions.length);
  }, [formData.instructions.length]);

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
      size="lg"
    >
      <div className="p-1">
        {error && (
          <Alert variant="danger" className="mb-3">
            <strong>Error:</strong> {error}
          </Alert>
        )}

        <Form onSubmit={handleSubmit}>
          {/* Title */}
          <Form.Group className="mb-3">
            <Form.Label htmlFor="title" className="fw-medium">
              Title *
            </Form.Label>
            <Form.Control
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleTextChange}
              placeholder="Enter recipe title"
              maxLength={255}
              disabled={loading}
              isInvalid={formData.title.length > 255}
            />
            <Form.Text className="text-muted">
              {formData.title.length}/255 characters
            </Form.Text>
          </Form.Group>

          {/* Summary */}
          <Form.Group className="mb-3">
            <Form.Label htmlFor="summary" className="fw-medium">
              Summary * (max 500 characters)
            </Form.Label>
            <Form.Control
              as="textarea"
              id="summary"
              name="summary"
              value={formData.summary}
              onChange={handleTextChange}
              placeholder="Enter a brief summary of the recipe"
              rows={3}
              maxLength={500}
              disabled={loading}
              isInvalid={formData.summary.length > 500}
            />
            <Form.Text className="text-muted">
              {formData.summary.length}/500 characters
            </Form.Text>
          </Form.Group>

          {/* Ingredients Section */}
          <Form.Group className="mb-4">
            <Form.Label className="fw-medium">
              Ingredients *
            </Form.Label>
            {formData.ingredients.map((ingredient, index) => (
              <InputGroup key={index} className="mb-2">
                <Form.Control
                  type="text"
                  value={ingredient}
                  onChange={(e) => handleIngredientInput(index, e.target.value)}
                  placeholder={index === 0 ? "Enter an ingredient (e.g., 2 cups flour)" : "Enter another ingredient"}
                  disabled={loading}
                />
                {formData.ingredients.length > 1 && (
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => removeIngredient(index)}
                    disabled={loading}
                    title="Remove ingredient"
                    className="px-2"
                  >
                    <i className="bi bi-trash"></i>
                  </Button>
                )}
              </InputGroup>
            ))}
          </Form.Group>

          {/* Instructions Section */}
          <Form.Group className="mb-4">
            <Form.Label className="fw-medium">
              Instructions * (Drag to reorder)
            </Form.Label>
            
            {/* Floating dragged item */}
            {draggedIndex !== null && (
              <div
                className="mb-2 p-2 bg-light rounded position-fixed"
                style={{
                  left: `${mousePosition[0] - 100}px`,
                  top: `${mousePosition[1] - 20}px`,
                  zIndex: 1000,
                  pointerEvents: 'none',
                  boxShadow: '5px 5px 10px rgba(0,0,0,0.5)',
                  width: 'auto',
                  minWidth: '300px',
                }}
              >
                <div className="d-flex align-items-center gap-2">
                  <Badge bg="secondary">{draggedIndex + 1}.</Badge>
                  <div className="flex-grow-1">
                    <i className="bi bi-grip-vertical me-2"></i>
                    {formData.instructions[draggedIndex]}
                  </div>
                </div>
              </div>
            )}
            
            {/* Instruction items with drag-and-drop */}
            {formData.instructions.map((instruction, index) => {
              const isDragged = draggedIndex === index;
              const isDragOver = dragOverIndex === index;
              
              return (
                <div
                  key={index}
                  className="mb-2"
                >
                  {/* Insertion indicator line - shown between items when dragging over */}
                  {isDragOver && !isDragged && (
                    <div 
                      className="w-100"
                      style={{
                        height: '5px',
                        backgroundColor: '#0d6efd',
                        marginBottom: '5px',
                        marginTop: '5px'
                      }}
                    />
                  )}
                  
                  <div
                    ref={(el: HTMLDivElement | null) => { instructionItemRefs.current[index] = el; }}
                    className="instruction-item d-flex align-items-center gap-2 p-2 bg-white border rounded"
                    style={{
                      cursor: 'grab',
                      opacity: isDragged ? 0.3 : 1
                    }}
                    >
                    <Badge bg="secondary" className="p-2">{index + 1}.</Badge>
                    <div
                      onMouseDown={(e) => handleMouseDown(index, e)}
                      className="d-flex align-items-center p-1"
                      style={{ cursor: 'grab' }}
                    >
                      <i className="bi bi-grip-vertical text-muted"></i>
                    </div>
                    <Form.Control
                      type="text"
                      value={instruction}
                      onChange={(e) => handleInstructionInput(index, e.target.value)}
                      placeholder={index === 0 ? "Enter first step" : "Enter next step"}
                      disabled={loading || isDragged}
                      className="flex-grow-1 border-0 bg-transparent"
                      readOnly={false}
                    />
                    {formData.instructions.length > 1 && !isDragged && (
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeInstruction(index);
                        }}
                        disabled={loading}
                        title="Remove step"
                        className="px-2 py-1"
                      >
                        <i className="bi bi-trash"></i>
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}
            
            {/* Floating dragged item */}
            {draggedIndex !== null && (
              <div
                className="position-fixed"
                style={{
                  left: mousePosition[0] - 150,
                  top: mousePosition[1] - 25,
                  zIndex: 1000,
                  pointerEvents: 'none',
                  boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
                  width: '300px'
                }}
              >
                <div className="d-flex align-items-center gap-2 p-2 bg-white border rounded">
                  <Badge bg="secondary" className="p-2">{draggedIndex + 1}.</Badge>
                  <div className="d-flex align-items-center p-1">
                    <i className="bi bi-grip-vertical text-muted"></i>
                  </div>
                  <span className="flex-grow-1 text-truncate">
                    {formData.instructions[draggedIndex]}
                  </span>
                </div>
              </div>
            )}
            
            {/* Floating dragged item */}
            {draggedIndex !== null && (
              <div
                className="position-fixed"
                style={{
                  left: mousePosition[0] - 150,
                  top: mousePosition[1] - 25,
                  zIndex: 1000,
                  pointerEvents: 'none',
                  boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
                  width: '300px'
                }}
              >
                <div className="d-flex align-items-center gap-2 p-2 bg-white border rounded">
                  <Badge bg="secondary" className="p-2">{draggedIndex + 1}.</Badge>
                  <div className="d-flex align-items-center p-1">
                    <i className="bi bi-grip-vertical text-muted"></i>
                  </div>
                  <span className="flex-grow-1 text-truncate">
                    {formData.instructions[draggedIndex]}
                  </span>
                </div>
              </div>
            )}
          </Form.Group>

          {/* Metadata Section */}
          <div className="mb-4">
            <h4 className="mb-3 fw-semibold">Recipe Details</h4>
            
            <Row className="g-3">
              <Col md={6}>
                <Form.Group>
                  <Form.Label htmlFor="servings" className="fw-medium">
                    Servings
                  </Form.Label>
                  <Form.Control
                    type="number"
                    id="servings"
                    name="servings"
                    value={formData.servings}
                    onChange={handleTextChange}
                    min={1}
                    max={100}
                    disabled={loading}
                  />
                </Form.Group>
              </Col>

              <Col md={6}>
                <Form.Group>
                  <Form.Label htmlFor="difficulty" className="fw-medium">
                    Difficulty
                  </Form.Label>
                  <Form.Select
                    id="difficulty"
                    name="difficulty"
                    value={formData.difficulty}
                    onChange={handleTextChange}
                    disabled={loading}
                  >
                    {DIFFICULTY_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>

              <Col md={6}>
                <Form.Group>
                  <Form.Label htmlFor="prep_time" className="fw-medium">
                    Prep Time
                  </Form.Label>
                  <Form.Control
                    type="text"
                    id="prep_time"
                    name="prep_time"
                    value={formData.prep_time}
                    onChange={handleTextChange}
                    placeholder="e.g., 20 minutes"
                    disabled={loading}
                  />
                </Form.Group>
              </Col>

              <Col md={6}>
                <Form.Group>
                  <Form.Label htmlFor="cook_time" className="fw-medium">
                    Cook Time
                  </Form.Label>
                  <Form.Control
                    type="text"
                    id="cook_time"
                    name="cook_time"
                    value={formData.cook_time}
                    onChange={handleTextChange}
                    placeholder="e.g., 30 minutes"
                    disabled={loading}
                  />
                </Form.Group>
              </Col>
            </Row>
          </div>

          {/* Form Actions */}
          <div className="d-flex justify-content-end gap-2">
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
            >
              {isEditMode ? 'Update Recipe' : 'Create Recipe'}
            </Button>
          </div>
        </Form>
      </div>
    </Modal>
  );
};
