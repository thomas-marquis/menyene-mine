import { Link } from 'react-router-dom';
import { Navbar, Container, Nav } from 'react-bootstrap';

export const Header = () => {
  return (
    <Navbar expand="lg" className="bg-white shadow-sm" style={{ padding: '1rem 0' }}>
      <Container>
        <Navbar.Brand as={Link} to="/" className="fw-semibold" style={{ color: '#2c3e50', fontSize: '1.5rem' }}>
          Menyene Mine
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="justify-content-end">
          <Nav className="gap-3">
            <Nav.Link as={Link} to="/" className="text-secondary fw-medium" style={{ color: '#7f8c8d' }}>
              Recipes
            </Nav.Link>
            <Nav.Link as={Link} to="/groceries" className="text-secondary fw-medium" style={{ color: '#7f8c8d' }}>
              Grocery List
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};
