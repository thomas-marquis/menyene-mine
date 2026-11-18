import { Card, Row, Col } from 'react-bootstrap';
import { Badge } from 'react-bootstrap';

interface RecipeDetailsProps {
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
}

// Map difficulty to Bootstrap badge variant
const getDifficultyVariant = (difficulty: string): string => {
  switch (difficulty?.toLowerCase()) {
    case 'easy':
      return 'success';
    case 'medium':
      return 'warning';
    case 'hard':
      return 'danger';
    default:
      return 'secondary';
  }
};

export const RecipeDetails = ({
  servings = 4,
  prep_time = '0 minutes',
  cook_time = '0 minutes',
  difficulty = 'Medium',
}: RecipeDetailsProps) => {
  return (
    <Card className="mb-4">
      <Card.Header className="bg-white border-0">
        <h3 className="mb-0" style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2c3e50' }}>
          Details
        </h3>
      </Card.Header>
      <Card.Body>
        <Row className="g-3">
          <Col xs={6} md={3}>
            <div className="d-flex align-items-center gap-2">
              <i className="bi bi-people text-muted"></i>
              <span className="text-muted small">Servings:</span>
            </div>
            <div className="fw-medium">{servings}</div>
          </Col>
          <Col xs={6} md={3}>
            <div className="d-flex align-items-center gap-2">
              <i className="bi bi-clock text-muted"></i>
              <span className="text-muted small">Prep Time:</span>
            </div>
            <div className="fw-medium">{prep_time}</div>
          </Col>
          <Col xs={6} md={3}>
            <div className="d-flex align-items-center gap-2">
              <i className="bi bi-hourglass-split text-muted"></i>
              <span className="text-muted small">Cook Time:</span>
            </div>
            <div className="fw-medium">{cook_time}</div>
          </Col>
          <Col xs={6} md={3}>
            <div className="d-flex align-items-center gap-2">
              <i className="bi bi-graph-up text-muted"></i>
              <span className="text-muted small">Difficulty:</span>
            </div>
            <Badge bg={getDifficultyVariant(difficulty)} className="fw-medium">
              {difficulty}
            </Badge>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};
