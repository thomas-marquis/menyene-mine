import { Link } from 'react-router-dom';
import { useAppSelector } from '../../../store';
import styles from './Header.module.css';

export const Header = () => {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          Menyene Mine
        </Link>
        <nav className={styles.nav}>
          <Link to="/" className={styles.navLink}>
            Home
          </Link>
          <Link to="/about" className={styles.navLink}>
            About
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className={styles.navLink}>
                Dashboard
              </Link>
              <Link to="/profile" className={styles.navLink}>
                Profile
              </Link>
            </>
          ) : (
            <Link to="/login" className={styles.navLink}>
              Login
            </Link>
          )}
        </nav>
        {isAuthenticated && user?.name && (
          <div className={styles.userInfo}>
            <span>Hello, {user.name}</span>
          </div>
        )}
      </div>
    </header>
  );
};
