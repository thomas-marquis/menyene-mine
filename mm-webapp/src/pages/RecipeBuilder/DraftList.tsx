import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { RecipeDraftCard } from '../../components/recipe/RecipeDraftCard/RecipeDraftCard';
import { recipeDraftService } from '../../services/recipeDraftService';
import type { RecipeDraft, RecipeDraftStats } from '../../types/recipe_draft.types';
import styles from './DraftList.module.css';

export const DraftListPage = () => {
  const navigate = useNavigate();
  const [drafts, setDrafts] = useState<RecipeDraft[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<RecipeDraftStats | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'draft' | 'validated' | 'rejected'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const ITEMS_PER_PAGE = 12;

  const fetchDrafts = useCallback(async (status?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await recipeDraftService.listDrafts(0, 1000, status);
      setDrafts(response.drafts);
      
      // Fetch stats
      const statsResponse = await recipeDraftService.getDraftStats();
      setStats(statsResponse);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch drafts. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch drafts. Please try again later.');
      }
      console.error('Error fetching drafts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDrafts();
  }, [fetchDrafts]);

  useEffect(() => {
    // Filter drafts based on active tab
    const filterStatus = activeTab === 'all' ? undefined : activeTab;
    fetchDrafts(filterStatus);
    setCurrentPage(1);
  }, [activeTab, fetchDrafts]);

  const handleViewDraft = (draftId: number) => {
    navigate(`/recipes/drafts/${draftId}`);
  };

  const handleCreateNew = () => {
    navigate('/recipes/builder');
  };

  const handleDeleteDraft = async (draftId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (window.confirm('Are you sure you want to delete this draft? This action cannot be undone.')) {
      try {
        await recipeDraftService.deleteDraft(draftId);
        setSuccessMessage('Draft deleted successfully!');
        fetchDrafts(activeTab === 'all' ? undefined : activeTab);
        setTimeout(() => setSuccessMessage(null), 3000);
      } catch (err: any) {
        setError('Failed to delete draft. Please try again.');
        console.error('Error deleting draft:', err);
      }
    }
  };

  const getTabCount = (tab: 'all' | 'draft' | 'validated' | 'rejected') => {
    if (!stats) return 0;
    switch (tab) {
      case 'all':
        return stats.total;
      case 'draft':
        return stats.draft;
      case 'validated':
        return stats.validated;
      case 'rejected':
        return stats.rejected;
      default:
        return 0;
    }
  };

  // Filter drafts by status based on active tab
  const filteredDrafts = activeTab === 'all' 
    ? drafts 
    : drafts.filter(d => d.status === activeTab);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(filteredDrafts.length / ITEMS_PER_PAGE));
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const paginatedDrafts = filteredDrafts.slice(
    (safeCurrentPage - 1) * ITEMS_PER_PAGE,
    safeCurrentPage * ITEMS_PER_PAGE
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'validated':
        return <span className="badge bg-success">Validated</span>;
      case 'rejected':
        return <span className="badge bg-danger">Rejected</span>;
      default:
        return <span className="badge bg-warning text-dark">Draft</span>;
    }
  };

  if (loading && drafts.length === 0) {
    return (
      <div className={styles.loadingContainer}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading drafts...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
        <Button onClick={() => fetchDrafts()} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className={styles.listContainer}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          <i className="bi bi-file-earmark-text me-3"></i>
          My Recipe Drafts
        </h1>
        <Button onClick={handleCreateNew} variant="primary" size="medium">
          <i className="bi bi-plus-lg me-2"></i>
          Create New Draft
        </Button>
      </div>

      {successMessage && (
        <div className="alert alert-success" role="alert">
          {successMessage}
        </div>
      )}

      <div className={styles.tabsContainer}>
        <ul className="nav nav-tabs">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              All <span className="badge bg-secondary ms-1">{getTabCount('all')}</span>
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'draft' ? 'active' : ''}`}
              onClick={() => setActiveTab('draft')}
            >
              Pending <span className="badge bg-warning text-dark ms-1">{getTabCount('draft')}</span>
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'validated' ? 'active' : ''}`}
              onClick={() => setActiveTab('validated')}
            >
              Validated <span className="badge bg-success ms-1">{getTabCount('validated')}</span>
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === 'rejected' ? 'active' : ''}`}
              onClick={() => setActiveTab('rejected')}
            >
              Rejected <span className="badge bg-danger ms-1">{getTabCount('rejected')}</span>
            </button>
          </li>
        </ul>
      </div>

      {paginatedDrafts.length > 0 ? (
        <>
          <div className={styles.draftsGrid}>
            {paginatedDrafts.map((draft) => (
              <div key={draft.id} className={styles.draftCardWrapper}>
                <RecipeDraftCard
                  draft={draft}
                  onView={() => handleViewDraft(draft.id)}
                  showStatusBadge
                />
                <div className={styles.cardActions}>
                  {draft.status === 'draft' && (
                    <button
                      className={styles.deleteButton}
                      onClick={(e) => handleDeleteDraft(draft.id, e)}
                      title="Delete draft"
                    >
                      <i className="bi bi-trash"></i>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <nav className={styles.pagination}>
              <ul className="pagination justify-content-center">
                <li className={`page-item ${safeCurrentPage === 1 ? 'disabled' : ''}`}>
                  <button
                    className="page-link"
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={safeCurrentPage === 1}
                    aria-label="Previous"
                  >
                    <i className="bi bi-chevron-left"></i>
                  </button>
                </li>
                
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const page = Math.max(1, safeCurrentPage - 2) + i;
                  if (page > totalPages) return null;
                  
                  return (
                    <li
                      key={page}
                      className={`page-item ${safeCurrentPage === page ? 'active' : ''}`}
                    >
                      <button
                        className="page-link"
                        onClick={() => setCurrentPage(page)}
                      >
                        {page}
                      </button>
                    </li>
                  );
                })}

                <li className={`page-item ${safeCurrentPage === totalPages ? 'disabled' : ''}`}>
                  <button
                    className="page-link"
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={safeCurrentPage === totalPages}
                    aria-label="Next"
                  >
                    <i className="bi bi-chevron-right"></i>
                  </button>
                </li>
              </ul>
            </nav>
          )}
        </>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <i className="bi bi-file-earmark-x text-muted" style={{ fontSize: '4rem' }}></i>
          </div>
          <h3>
            {activeTab === 'all' 
              ? 'No drafts yet' 
              : activeTab === 'draft' 
                ? 'No pending drafts' 
                : activeTab === 'validated' 
                  ? 'No validated drafts' 
                  : 'No rejected drafts'}
          </h3>
          <p>
            {activeTab === 'all' 
              ? 'Start by creating a new draft using the AI Recipe Builder.'
              : activeTab === 'draft' 
                ? 'Generate new drafts using the AI Recipe Builder.'
                : activeTab === 'validated' 
                  ? 'Validated drafts will appear here after you approve them.'
                  : 'Rejected drafts will appear here after you reject them.'}
          </p>
          <Button onClick={handleCreateNew} variant="primary">
            <i className="bi bi-plus-lg me-2"></i>
            Create New Draft
          </Button>
        </div>
      )}
    </div>
  );
};
