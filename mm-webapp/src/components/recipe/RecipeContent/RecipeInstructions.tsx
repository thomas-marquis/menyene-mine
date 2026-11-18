import { Card, ListGroup } from 'react-bootstrap';

interface RecipeInstructionsProps {
  instructions: string[];
}

export const RecipeInstructions = ({ instructions }: RecipeInstructionsProps) => {
  if (!instructions || instructions.length === 0) {
    return (
      <Card className="mb-4">
        <Card.Header className="bg-white border-0">
          <h3 className="mb-0" style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2c3e50' }}>
            Instructions
          </h3>
        </Card.Header>
        <Card.Body>
          <p className="text-muted mb-0">No instructions specified</p>
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className="mb-4">
      <Card.Header className="bg-white border-0">
        <h3 className="mb-0" style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2c3e50' }}>
          Instructions
        </h3>
      </Card.Header>
      <Card.Body>
        <ListGroup variant="flush" className="border-0" numbered>
          {instructions.map((instruction, index) => (
            <ListGroup.Item
              key={index}
              className="border-0 px-0 py-2"
              style={{ backgroundColor: 'transparent' }}
            >
              <span style={{ fontSize: '0.95rem' }}>
                {instruction}
              </span>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Card.Body>
    </Card>
  );
};
