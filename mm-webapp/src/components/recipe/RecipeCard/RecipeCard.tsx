import type { Recipe } from '../../../types/recipe.types';
import { Card, Button } from 'react-bootstrap';
import { type ReactNode } from 'react';

/**
 * Configuration for a custom button in RecipeCard
 */
interface RecipeCardButton {
  /** Button label text */
  label: string;
  /** Optional icon to display before the label */
  icon?: ReactNode;
  /** Bootstrap button variant (e.g., 'primary', 'outline-primary', 'danger') */
  variant?: string;
  /** Click handler for the button */
  onClick: () => void;
}

/**
 * Props for the RecipeCard component
 */
interface RecipeCardProps {
  /** The recipe to display */
  recipe: Recipe;
  /** Callback when the card is viewed/clicked (used when no custom buttons are provided) */
  onView?: () => void;
  /** Left action button configuration */
  leftButton?: RecipeCardButton;
  /** Right action button configuration */
  rightButton?: RecipeCardButton;
  /** Whether this card represents a selected recipe */
  isSelected?: boolean;
  /** Additional CSS class name for the card */
  className?: string;
}

/**
 * RecipeCard - A reusable component for displaying recipe information in a card format.
 * 
 * This component can be used in two modes:
 * 1. Simple mode: With just `onView` prop - displays a card with hover effect and view button
 * 2. Custom buttons mode: With `leftButton` and/or `rightButton` props - displays custom action buttons
 * 
 * @example
 * // Simple mode - click to view
 * <RecipeCard recipe={recipe} onView={() => navigate(`/recipes/${recipe.id}`)} />
 * 
 * @example
 * // With custom buttons
 * <RecipeCard 
 *   recipe={recipe}
 *   leftButton={{ label: 'View', icon: <i className="bi bi-eye"></i>, onClick: () => onView(recipe) }}
 *   rightButton={{ label: 'Select', icon: <i className="bi bi-check"></i>, variant: 'primary', onClick: () => onSelect(recipe) }}
 * />
 */
export const RecipeCard = ({
  recipe,
  onView,
  leftButton,
  rightButton,
  isSelected = false,
  className = '',
}: RecipeCardProps) => {
  if (!recipe || !recipe.id) {
    return null;
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleCardClick = () => {
    if (onView && !leftButton && !rightButton) {
      onView();
    }
  };

  return (
    <Card
      className={`h-100 ${isSelected ? 'border-primary' : ''} ${className}`}
      onClick={handleCardClick}
      style={{ borderRadius: '8px', border: '1px solid #e9ecef', cursor: onView ? 'pointer' : 'default' }}
    >
      <Card.Body className="p-3">
        <Card.Title className="mb-2 text-truncate" style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2c3e50' }}>
          {recipe.title}
        </Card.Title>
        <Card.Text className="mb-2 text-muted" style={{ fontSize: '0.9rem', lineHeight: 1.5, color: '#7f8c8d' }}>
          {recipe.summary || 'No summary available'}
        </Card.Text>
        <div className="d-flex align-items-center gap-2 text-muted small">
          <i className="bi bi-calendar me-1"></i>
          {formatDate(recipe.creation_date)}
        </div>
      </Card.Body>
      
      {(leftButton || rightButton) ? (
        <Card.Footer className="bg-transparent border-0 p-2">
          <div className="d-flex gap-2 justify-content-between">
            {leftButton && (
              <Button
                variant={leftButton.variant || 'outline-primary'}
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  leftButton.onClick();
                }}
                className="flex-grow-1"
              >
                {leftButton.icon && <span className="me-1">{leftButton.icon}</span>}
                {leftButton.label}
              </Button>
            )}
            {rightButton && (
              <Button
                variant={rightButton.variant || 'primary'}
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  rightButton.onClick();
                }}
                className="flex-grow-1"
              >
                {rightButton.icon && <span className="me-1">{rightButton.icon}</span>}
                {rightButton.label}
              </Button>
            )}
          </div>
        </Card.Footer>
      ) : onView ? (
        <div
          className="position-absolute bottom-0 start-0 end-0 p-3"
          style={{
            background: 'linear-gradient(transparent, rgba(0, 0, 0, 0.1))',
            opacity: 0,
            transition: 'opacity 0.3s ease',
          }}
          onMouseEnter={(e) => {
            const target = e.target as HTMLElement;
            target.style.opacity = '1';
          }}
          onMouseLeave={(e) => {
            const target = e.target as HTMLElement;
            target.style.opacity = '0';
          }}
        >
          <div className="d-flex justify-content-end">
            <Button
              variant="primary"
              size="sm"
              className="d-flex align-items-center gap-2"
              onClick={(e) => {
                e.stopPropagation();
                onView();
              }}
              style={{ fontSize: '0.85rem', fontWeight: 500 }}
            >
              <i className="bi bi-eye"></i>
              <span>View Recipe</span>
            </Button>
          </div>
        </div>
      ) : null}
    </Card>
  );
};
