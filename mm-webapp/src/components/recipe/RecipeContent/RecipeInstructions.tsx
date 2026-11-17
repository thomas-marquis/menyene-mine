import styles from './RecipeContent.module.css';

interface RecipeInstructionsProps {
  instructions: string[];
}

export const RecipeInstructions = ({ instructions }: RecipeInstructionsProps) => {
  if (!instructions || instructions.length === 0) {
    return (
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Instructions</h2>
        <p className={styles.emptyMessage}>No instructions specified</p>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Instructions</h2>
      <ol className={styles.instructionsList}>
        {instructions.map((instruction, index) => (
          <li key={index} className={styles.instructionItem}>
            {instruction}
          </li>
        ))}
      </ol>
    </section>
  );
};
