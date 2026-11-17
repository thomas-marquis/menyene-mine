import { RecipeIngredients } from './RecipeIngredients';
import { RecipeInstructions } from './RecipeInstructions';
import { RecipeDetails } from './RecipeDetails';
import { RecipeSummary } from './RecipeSummary';
import styles from './RecipeContent.module.css';

interface RecipeContentProps {
  title?: string;
  summary?: string;
  ingredients?: string[];
  instructions?: string[];
  servings?: number;
  prep_time?: string;
  cook_time?: string;
  difficulty?: string;
  // Layout options
  showTitle?: boolean;
  showSummary?: boolean;
  className?: string;
}

export const RecipeContent = ({
  title = 'Untitled Recipe',
  summary = '',
  ingredients = [],
  instructions = [],
  servings = 4,
  prep_time = '0 minutes',
  cook_time = '0 minutes',
  difficulty = 'Medium',
  showTitle = true,
  showSummary = true,
  className = '',
}: RecipeContentProps) => {
  return (
    <div className={`${styles.recipeContent} ${className}`}>
      {showTitle && <h1 className={styles.title}>{title}</h1>}
      
      {showSummary && <RecipeSummary summary={summary} />}

      <div className={styles.contentSections}>
        <RecipeIngredients ingredients={ingredients || []} />
        <RecipeInstructions instructions={instructions || []} />
        <RecipeDetails
          servings={servings}
          prep_time={prep_time}
          cook_time={cook_time}
          difficulty={difficulty}
        />
      </div>
    </div>
  );
};
