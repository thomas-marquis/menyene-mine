import type { Recipe } from '../../../types/recipe.types';
import styles from './RecipeCard.module.css';

interface RecipeCardProps {
  recipe: Recipe;
  onView: () => void;
}

export const RecipeCard = ({ recipe, onView }: RecipeCardProps) => {
  if (!recipe || !recipe.id) {
    return null;
  }
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className={styles.recipeCard} onClick={onView}>
      <div className={styles.cardContent}>
        <h3 className={styles.title}>{recipe.title}</h3>
        <p className={styles.summary}>
          {recipe.summary || 'No summary available'}
        </p>
        <div className={styles.meta}>
          <span className={styles.date}>
            <i className="bi bi-calendar me-1"></i>
            {formatDate(recipe.creation_date)}
          </span>
        </div>
      </div>
      <div className={styles.viewOverlay}>
        <button className={styles.viewButton}>
          <i className="bi bi-eye"></i>
          <span>View Recipe</span>
        </button>
      </div>
    </div>
  );
};
