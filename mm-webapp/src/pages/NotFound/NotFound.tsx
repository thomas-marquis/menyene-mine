import { Link } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { Container } from 'react-bootstrap';

export const NotFoundPage = () => {
  return (
    <Container className="py-5 text-center">
      <div className="mb-4">
        <h1 className="display-1 fw-bold text-muted">404</h1>
        <h2 className="mb-3" style={{ fontSize: '2rem', fontWeight: 600, color: '#2c3e50' }}>
          Page Not Found
        </h2>
        <p className="text-muted mb-4">
          The page you are looking for does not exist.
        </p>
      </div>
      <Link to="/">
        <Button variant="primary" size="md">
          <i className="bi bi-house me-2"></i>
          Go back to Home
        </Button>
      </Link>
    </Container>
  );
};
