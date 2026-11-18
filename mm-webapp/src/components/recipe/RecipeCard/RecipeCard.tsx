import type { Recipe } from '../../../types/recipe.types';
import { Card, Button } from 'react-bootstrap';

interface RecipeCardProps {
  recipe: Recipe;
  onView: () => void;
}

export const RecipeCard = ({ recipe, onView }: RecipeCardProps) => {
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

  return (
    <Card
      className="h-100 border-0 shadow-sm cursor-pointer position-relative overflow-hidden"
      onClick={onView}
      style={{ borderRadius: '8px', border: '1px solid #e9ecef' }}
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
    </Card>
  );
};
