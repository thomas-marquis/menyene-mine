import { useState } from 'react';
import type { RecipeDraft } from '../../../types/recipe_draft.types';
import styles from './RecipeDraftCard.module.css';

interface RecipeDraftCardProps {
  draft: RecipeDraft;
  onView: () => void;
  showStatusBadge?: boolean;
}

export const RecipeDraftCard = ({ 
  draft, 
  onView, 
  showStatusBadge = false 
}: RecipeDraftCardProps) => {
  const [isHovered, setIsHovered] = useState(false);

  const getStatusBadge = (status: string) => {
    if (!showStatusBadge) return null;
    
    switch (status) {
      case 'validated':
        return <span className="badge bg-success">Validated</span>;
      case 'rejected':
        return <span className="badge bg-danger">Rejected</span>;
      default:
        return <span className="badge bg-warning text-dark">Draft</span>;
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const content = draft.generated_content || {};
  const title = content.title || 'Untitled Recipe';
  const summary = content.summary || 'No summary available';

  // Truncate summary for card display
  const truncatedSummary = summary.length > 100 
    ? `${summary.substring(0, 100)}...` 
    : summary;

  return (
    <div
      className={styles.card}
      onClick={onView}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onView();
        }
      }}
    >
      <div className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>{title}</h3>
        {showStatusBadge && (
          <div className={styles.statusBadge}>
            {getStatusBadge(draft.status)}
          </div>
        )}
      </div>

      <div className={styles.cardBody}>
        <p className={styles.cardSummary}>{truncatedSummary}</p>
        
        <div className={styles.cardMeta}>
          <span className={styles.metaItem}>
            <i className="bi bi-calendar me-1"></i>
            {formatDate(draft.created_at)}
          </span>
          <span className={styles.metaItem}>
            <i className="bi bi-file-earmark-text me-1"></i>
            Draft #{draft.id}
          </span>
        </div>
      </div>

      <div className={styles.cardFooter}>
        <span className={styles.promptPreview}>
          <i className="bi bi-chat-left-quote me-1"></i>
          {draft.user_prompt.length > 50 
            ? `${draft.user_prompt.substring(0, 50)}...` 
            : draft.user_prompt}
        </span>
        
        <div className={styles.viewIndicator}>
          <i className="bi bi-eye me-1"></i>
          {isHovered ? 'Click to view' : 'View details'}
        </div>
      </div>

      {draft.recipe_id && (
        <div className={styles.recipeLink}>
          <i className="bi bi-link-45deg me-1"></i>
          Recipe #{draft.recipe_id}
        </div>
      )}
    </div>
  );
};
