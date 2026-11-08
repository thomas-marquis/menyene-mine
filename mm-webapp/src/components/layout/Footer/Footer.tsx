import styles from './Footer.module.css';

export const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <p className={styles.text}>
          © {new Date().getFullYear()} Menyene Mine. All rights reserved.
        </p>
      </div>
    </footer>
  );
};
