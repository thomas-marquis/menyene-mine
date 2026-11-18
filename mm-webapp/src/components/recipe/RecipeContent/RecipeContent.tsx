import { RecipeIngredients } from './RecipeIngredients';
import { RecipeInstructions } from './RecipeInstructions';
import { RecipeDetails } from './RecipeDetails';
import { RecipeSummary } from './RecipeSummary';
import { Row, Col } from 'react-bootstrap';

interface RecipeContentProps {
  title?: string;
  summary?: string;
  ingredients?: string[];
  instructions?: string[];
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
  // Layout options
  showTitle?: boolean;
  showSummary?: boolean;
  className?: string;
}

export const RecipeContent = ({
  title = 'Untitled Recipe',
  summary = '',
  ingredients = [],
  instructions = [],
  servings = 4,
  prep_time = '0 minutes',
  cook_time = '0 minutes',
  difficulty = 'Medium',
  showTitle = true,
  showSummary = true,
  className = '',
}: RecipeContentProps) => {
  return (
    <div className={className}>
      {showTitle && (
        <h1 className="mb-4" style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
          {title}
        </h1>
      )}
      
      {showSummary && <RecipeSummary summary={summary} />}

      <Row className="g-4">
        <Col md={6}>
          <RecipeIngredients ingredients={ingredients || []} />
        </Col>
        <Col md={6}>
          <RecipeInstructions instructions={instructions || []} />
        </Col>
      </Row>
      
      <Row className="mt-4">
        <Col>
          <RecipeDetails
            servings={servings}
            prep_time={prep_time}
            cook_time={cook_time}
            difficulty={difficulty}
          />
        </Col>
      </Row>
    </div>
  );
};
