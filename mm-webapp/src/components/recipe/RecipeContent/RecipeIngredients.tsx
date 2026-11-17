import styles from './RecipeContent.module.css';

interface RecipeIngredientsProps {
  ingredients: string[];
}

export const RecipeIngredients = ({ ingredients }: RecipeIngredientsProps) => {
  if (!ingredients || ingredients.length === 0) {
    return (
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>Ingredients</h2>
        <p className={styles.emptyMessage}>No ingredients specified</p>
      </section>
    );
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.sectionTitle}>Ingredients</h2>
      <ul className={styles.ingredientsList}>
        {ingredients.map((ingredient, index) => (
          <li key={index} className={styles.ingredientItem}>
            {ingredient}
          </li>
        ))}
      </ul>
    </section>
  );
};
