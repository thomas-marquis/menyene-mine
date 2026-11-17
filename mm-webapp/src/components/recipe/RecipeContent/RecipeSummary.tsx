import styles from './RecipeContent.module.css';

interface RecipeSummaryProps {
  summary: string;
}

export const RecipeSummary = ({ summary }: RecipeSummaryProps) => {
  if (!summary || summary.trim() === '') {
    return null;
  }

  return (
    <div className={styles.summary}>
      <p>{summary}</p>
    </div>
  );
};
