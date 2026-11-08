import { Link } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import styles from './NotFound.module.css';

export const NotFoundPage = () => {
  return (
    <div className={styles.notFoundContainer}>
      <div className={styles.content}>
        <h1 className={styles.title}>404 - Page Not Found</h1>
        <p className={styles.message}>The page you are looking for does not exist.</p>
        <Link to="/">
          <Button variant="primary" size="medium">
            <i className="bi bi-house me-2"></i>
            Go back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
};
