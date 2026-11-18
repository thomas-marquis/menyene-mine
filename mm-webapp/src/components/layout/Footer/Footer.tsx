import { Container } from 'react-bootstrap';

export const Footer = () => {
  return (
    <footer className="bg-white border-top py-4 mt-auto">
      <Container className="text-center">
        <p className="text-muted mb-0 small">
          &copy; {new Date().getFullYear()} Menyene Mine. All rights reserved.
        </p>
      </Container>
    </footer>
  );
};
