import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeDraftCard } from '../../components/recipe/RecipeDraftCard/RecipeDraftCard';
import { recipeDraftService } from '../../services/recipeDraftService';
import type { RecipeDraft } from '../../types/recipe_draft.types';
import { Container, Row, Col, Form, Alert, Spinner, Card, ListGroup } from 'react-bootstrap';

export const RecipeGeneratorPage = () => {
  const navigate = useNavigate();
  const [instruction, setInstruction] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [drafts, setDrafts] = useState<RecipeDraft[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleInstructionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInstruction(e.target.value);
    setError(null);
  };

  const handleGenerate = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      const trimmedInstruction = instruction.trim();
      if (!trimmedInstruction) {
        setError('Please enter an instruction to generate a recipe');
        return;
      }

      try {
        setIsGenerating(true);
        setError(null);
        setSuccessMessage(null);
        setDrafts([]);

        const newDrafts = await recipeDraftService.generateDrafts({
          instruction: trimmedInstruction,
          max_drafts: 1,
        });

        setDrafts(newDrafts);
        setSuccessMessage('Recipe draft generated successfully!');
      } catch (err: any) {
        console.error('Error generating drafts:', err);
        console.error('Error response:', err.response);
        console.error('Error request:', err.request);
        
        // Extract error message from various error formats
        let errorMessage = 'Failed to generate recipe. Please try again.';
        
        if (err.response) {
          // Backend returned an error response
          const responseData = err.response.data;
          console.error('Response data:', responseData);
          
          if (typeof responseData === 'string') {
            errorMessage = responseData;
          } else if (responseData?.detail) {
            errorMessage = responseData.detail;
          } else if (responseData?.message) {
            errorMessage = responseData.message;
          } else if (responseData) {
            errorMessage = JSON.stringify(responseData);
          }
        } else if (err.request) {
          // Network error
          errorMessage = 'Network error. Please check your connection and that the backend is running.';
        } else if (err.message) {
          // Other errors with message
          errorMessage = err.message;
        }
        
        setError(errorMessage);
      } finally {
        setIsGenerating(false);
      }
    },
    [instruction]
  );

  const handleViewDraft = (draftId: number) => {
    navigate(`/recipes/drafts/${draftId}`);
  };

  const handleViewAllDrafts = () => {
    navigate('/recipes/drafts');
  };

  const handleGoBack = () => {
    navigate('/');
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
    setInstruction(example);
    setError(null);
  };

  // Show loading state if we're waiting for the first load
  if (isGenerating && drafts.length === 0 && !error && !successMessage) {
    return (
      <Container className="py-4">
        <div className="d-flex align-items-center mb-4">
          <Button onClick={handleGoBack} variant="outline" size="md" disabled={true} className="me-3">
            <i className="bi bi-arrow-left me-2"></i>
            Back to Recipes
          </Button>
          <div>
            <h1 className="mb-1 d-flex align-items-center gap-2" style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
              <i className="bi bi-robot"></i>
              AI Recipe Generator
            </h1>
            <p className="text-muted mb-0">
              Describe what you want to cook, and our AI will generate recipe ideas for you!
            </p>
          </div>
        </div>
        
        <div className="py-5 text-center">
          <Spinner animation="border" variant="primary" role="status" className="mb-3">
            <span className="visually-hidden">Generating...</span>
          </Spinner>
          <p>Generating your recipe...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <div className="d-flex align-items-center mb-4">
        <Button onClick={handleGoBack} variant="outline" size="md" disabled={isGenerating} className="me-3">
          <i className="bi bi-arrow-left me-2"></i>
          Back to Recipes
        </Button>
        
        <div>
          <h1 className="mb-1 d-flex align-items-center gap-2" style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
            <i className="bi bi-robot"></i>
            AI Recipe Generator
          </h1>
          <p className="text-muted mb-0">
            Describe what you want to cook, and our AI will generate recipe ideas for you!
          </p>
        </div>
      </div>

      {successMessage && (
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
      )}

      {error && (
        <Alert variant="danger" className="mb-4">
          <strong>Error:</strong> {error}
        </Alert>
      )}

      <Card className="mb-4">
        <Card.Body>
          <Form onSubmit={handleGenerate}>
            <Form.Group className="mb-3">
              <Form.Label htmlFor="instruction" className="fw-semibold">
                Describe your recipe idea:
              </Form.Label>
              <Form.Control
                as="textarea"
                id="instruction"
                rows={6}
                value={instruction}
                onChange={handleInstructionChange}
                placeholder="e.g., Create a quick vegetarian pasta dish with tomatoes and basil..."
                disabled={isGenerating}
              />
              <Form.Text className="text-muted">
                Be as specific as you like! The AI will generate recipes based on your description.
              </Form.Text>
            </Form.Group>

            <div className="d-flex flex-wrap gap-2">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={isGenerating || !instruction.trim()}
                loading={isGenerating}
              >
                <i className="bi bi-magic me-2"></i>
                {isGenerating ? 'Generating...' : 'Generate Recipe'}
              </Button>

              <Button
                type="button"
                variant="outline"
                size="lg"
                onClick={handleViewAllDrafts}
                disabled={isGenerating}
              >
                <i className="bi bi-folder me-2"></i>
                View All Drafts
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Body>
          <h3 className="mb-3 d-flex align-items-center gap-2" style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2c3e50' }}>
            <i className="bi bi-lightbulb"></i>
            Need inspiration? Try these examples:
          </h3>
          <ListGroup variant="flush">
            {examplePrompts.map((example, index) => (
              <ListGroup.Item
                key={index}
                className="border-0 px-0 py-2"
                style={{ backgroundColor: 'transparent', cursor: 'pointer' }}
                onClick={() => handleUseExample(example)}
                disabled={isGenerating}
                action
              >
                <div className="d-flex align-items-center gap-2 text-primary">
                  <i className="bi bi-arrow-right-circle"></i>
                  <span>{example}</span>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Card.Body>
      </Card>

      {drafts.length > 0 && (
        <div className="mt-4">
          <h2 className="mb-3 d-flex align-items-center gap-2" style={{ fontSize: '1.5rem', fontWeight: 600, color: '#2c3e50' }}>
            <i className="bi bi-file-earmark-text"></i>
            Generated Recipe Draft
          </h2>
          <p className="text-muted mb-4">
            Review the draft below. Click on it to view details and validate or reject it.
          </p>

          <Row xs={1} md={2} lg={3} className="g-4 mb-4">
            {drafts.map((draft) => (
              <Col key={draft.id}>
                <RecipeDraftCard
                  draft={draft}
                  onView={() => handleViewDraft(draft.id)}
                />
              </Col>
            ))}
          </Row>

          <div className="text-center">
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
    </Container>
  );
};
