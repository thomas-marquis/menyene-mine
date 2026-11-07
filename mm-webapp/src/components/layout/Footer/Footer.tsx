import styles from './Footer.module.css';

export const Footer = () => {
  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <p>&copy; {new Date().getFullYear()} Menyene Mine. All rights reserved.</p>
        <div className={styles.links}>
          <a href="/privacy" className={styles.link}>
            Privacy Policy
          </a>
          <a href="/terms" className={styles.link}>
            Terms of Service
          </a>
          <a href="/contact" className={styles.link}>
            Contact Us
          </a>
        </div>
      </div>
    </footer>
  );
};
