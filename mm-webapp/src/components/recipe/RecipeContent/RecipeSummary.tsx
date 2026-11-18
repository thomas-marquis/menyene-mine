interface RecipeSummaryProps {
  summary: string;
}

export const RecipeSummary = ({ summary }: RecipeSummaryProps) => {
  if (!summary || summary.trim() === '') {
    return null;
  }

  return (
    <div className="mb-4">
      <p className="lead" style={{ color: '#7f8c8d' }}>
        {summary}
      </p>
    </div>
  );
};
