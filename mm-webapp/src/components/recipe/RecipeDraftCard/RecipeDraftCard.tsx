import { useState } from 'react';
import type { RecipeDraft } from '../../../types/recipe_draft.types';
import { Card, Badge } from 'react-bootstrap';

interface RecipeDraftCardProps {
  draft: RecipeDraft;
  onView: () => void;
  showStatusBadge?: boolean;
}

// Map status to Bootstrap badge variant
const getStatusVariant = (status: string): string => {
  switch (status) {
    case 'validated':
      return 'success';
    case 'rejected':
      return 'danger';
    default:
      return 'warning';
  }
};

// Map status to display text
const getStatusText = (status: string): string => {
  switch (status) {
    case 'validated':
      return 'Validated';
    case 'rejected':
      return 'Rejected';
    default:
      return 'Draft';
  }
};

export const RecipeDraftCard = ({ 
  draft, 
  onView, 
  showStatusBadge = false 
}: RecipeDraftCardProps) => {
  const [isHovered, setIsHovered] = useState(false);

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
    <Card
      className="h-100 shadow-sm cursor-pointer border-0"
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
      style={{ borderRadius: '8px', border: '1px solid #e9ecef' }}
    >
      <Card.Body className="p-3">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <Card.Title className="mb-0 text-truncate" style={{ fontSize: '1.1rem', fontWeight: 600, color: '#2c3e50' }}>
            {title}
          </Card.Title>
          {showStatusBadge && (
            <Badge bg={getStatusVariant(draft.status)} className="text-dark">
              {getStatusText(draft.status)}
            </Badge>
          )}
        </div>

        <Card.Text className="text-muted mb-3" style={{ fontSize: '0.85rem', lineHeight: 1.5 }}>
          {truncatedSummary}
        </Card.Text>
        
        <div className="d-flex flex-wrap gap-3 mb-2 text-muted small">
          <span className="d-flex align-items-center gap-1">
            <i className="bi bi-calendar"></i>
            {formatDate(draft.created_at)}
          </span>
          <span className="d-flex align-items-center gap-1">
            <i className="bi bi-file-earmark-text"></i>
            Draft #{draft.id}
          </span>
        </div>

        <div className="border-top pt-2 mt-2">
          <div className="d-flex justify-content-between align-items-center">
            <span className="text-muted small d-flex align-items-center gap-1">
              <i className="bi bi-chat-left-quote"></i>
              {draft.user_instruction.length > 50 
                ? `${draft.user_instruction.substring(0, 50)}...` 
                : draft.user_instruction}
            </span>
            <span className="text-primary small d-flex align-items-center gap-1">
              <i className="bi bi-eye"></i>
              {isHovered ? 'Click to view' : 'View details'}
            </span>
          </div>
        </div>

        {draft.recipe_id && (
          <div className="border-top pt-2 mt-2 text-center">
            <Badge bg="light" text="primary" className="p-2">
              <i className="bi bi-link-45deg me-1"></i>
              Recipe #{draft.recipe_id}
            </Badge>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};
