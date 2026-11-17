import styles from './RecipeContent.module.css';

interface RecipeDetailsProps {
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
}

export const RecipeDetails = ({
  servings = 4,
  prep_time = '0 minutes',
  cook_time = '0 minutes',
  difficulty = 'Medium',
}: RecipeDetailsProps) => {
  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Details</h2>
      <dl className={styles.detailsList}>
        <div className={styles.detailItem}>
          <dt>Servings:</dt>
          <dd>{servings}</dd>
        </div>
        <div className={styles.detailItem}>
          <dt>Prep Time:</dt>
          <dd>{prep_time}</dd>
        </div>
        <div className={styles.detailItem}>
          <dt>Cook Time:</dt>
          <dd>{cook_time}</dd>
        </div>
        <div className={styles.detailItem}>
          <dt>Difficulty:</dt>
          <dd>{difficulty}</dd>
        </div>
      </dl>
    </section>
  );
};
