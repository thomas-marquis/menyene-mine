import { Link } from 'react-router-dom';
import styles from './Header.module.css';

export const Header = () => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link to="/" className={styles.logo}>
          Menyene Mine
        </Link>
        <nav className={styles.nav}>
          <Link to="/" className={styles.navLink}>
            Recipes
          </Link>
          <Link to="/groceries" className={styles.navLink}>
            Grocery List
          </Link>
        </nav>
      </div>
    </header>
  );
};
