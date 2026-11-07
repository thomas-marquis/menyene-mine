import { Link } from 'react-router-dom';
import './NotFound.module.css';

export const NotFoundPage = () => {
  return (
    <div className="not-found-container">
      <h1>404 - Page Not Found</h1>
      <p>The page you are looking for does not exist.</p>
      <Link to="/" className="back-home-link">
        Go back to Home
      </Link>
    </div>
  );
};
