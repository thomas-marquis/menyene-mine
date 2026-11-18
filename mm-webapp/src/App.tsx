import { BrowserRouter } from 'react-router-dom';
import { Header } from './components/layout/Header/Header';
import { Footer } from './components/layout/Footer/Footer';
import { AppRoutes } from './routes/AppRoutes';
import { Container } from 'react-bootstrap';

function App() {
  return (
    <BrowserRouter>
      <div className="app d-flex flex-column min-vh-100">
        <Header />
        <main className="main-content flex-grow-1">
          <Container fluid="xl" className="px-0">
            <AppRoutes />
          </Container>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
