import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '../../components/common/Button/Button'
import { RecipeDraftCard } from '../../components/recipe/RecipeDraftCard/RecipeDraftCard'
import { recipeDraftService } from '../../services/recipeDraftService'
import type { RecipeDraft, RecipeDraftStats } from '../../types/recipe_draft.types'
import { Container, Row, Col, Alert, Spinner, Nav, Badge, Pagination } from 'react-bootstrap'
import { useAppDispatch } from '../../store'
import { decrementPendingDraftCount } from '../../store/stats/slice'

export const DraftListPage = () => {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [drafts, setDrafts] = useState<RecipeDraft[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<RecipeDraftStats | null>(null)
  const [activeTab, setActiveTab] = useState<'all' | 'draft' | 'validated' | 'rejected'>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const ITEMS_PER_PAGE = 12

  const fetchDrafts = useCallback(async (status?: string) => {
    try {
      setLoading(true)
      setError(null)

      const response = await recipeDraftService.listDrafts(0, 1000, status)
      setDrafts(response.drafts)

      // Fetch stats
      const statsResponse = await recipeDraftService.getDraftStats()
      setStats(statsResponse)
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch drafts. Please try again later.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to fetch drafts. Please try again later.')
      }
      console.error('Error fetching drafts:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDrafts()
  }, [fetchDrafts])

  useEffect(() => {
    // Filter drafts based on active tab
    const filterStatus = activeTab === 'all' ? undefined : activeTab
    fetchDrafts(filterStatus)
    setCurrentPage(1)
  }, [activeTab, fetchDrafts])

  const handleViewDraft = (draftId: number) => {
    navigate(`/recipes/drafts/${draftId}`)
  }

  const handleCreateNew = () => {
    navigate('/recipes/builder')
  }

  const handleDeleteDraft = async (draftId: number, status: string, e: React.MouseEvent) => {
    e.stopPropagation()

    if (
      window.confirm('Are you sure you want to delete this draft? This action cannot be undone.')
    ) {
      try {
        await recipeDraftService.deleteDraft(draftId)
        if (status === 'draft') {
          dispatch(decrementPendingDraftCount())
        }
        setSuccessMessage('Draft deleted successfully!')
        fetchDrafts(activeTab === 'all' ? undefined : activeTab)
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err: any) {
        setError('Failed to delete draft. Please try again.')
        console.error('Error deleting draft:', err)
      }
    }
  }

  const getTabCount = (tab: 'all' | 'draft' | 'validated' | 'rejected') => {
    if (!stats) return 0
    switch (tab) {
      case 'all':
        return stats.total
      case 'draft':
        return stats.draft
      case 'validated':
        return stats.validated
      case 'rejected':
        return stats.rejected
      default:
        return 0
    }
  }

  // Filter drafts by status based on active tab
  const filteredDrafts = activeTab === 'all' ? drafts : drafts.filter((d) => d.status === activeTab)

  // Pagination
  const totalPages = Math.max(1, Math.ceil(filteredDrafts.length / ITEMS_PER_PAGE))
  const safeCurrentPage = Math.min(currentPage, totalPages)
  const paginatedDrafts = filteredDrafts.slice(
    (safeCurrentPage - 1) * ITEMS_PER_PAGE,
    safeCurrentPage * ITEMS_PER_PAGE,
  )

  // Render pagination items
  const renderPaginationItems = () => {
    const items = []
    const maxVisiblePages = 5

    // Always show first page
    if (totalPages > 1) {
      items.push(
        <Pagination.Item
          key={1}
          active={safeCurrentPage === 1}
          onClick={() => setCurrentPage(1)}
          disabled={safeCurrentPage === 1}
        >
          1
        </Pagination.Item>,
      )
    }

    // Show ellipsis if needed before current page
    if (safeCurrentPage > 3) {
      items.push(<Pagination.Ellipsis key='ellipsis-start' disabled />)
    }

    // Show pages around current page
    const startPage = Math.max(2, safeCurrentPage - Math.floor(maxVisiblePages / 2))
    const endPage = Math.min(totalPages - 1, safeCurrentPage + Math.floor(maxVisiblePages / 2))

    for (let page = startPage; page <= endPage; page++) {
      items.push(
        <Pagination.Item
          key={page}
          active={safeCurrentPage === page}
          onClick={() => setCurrentPage(page)}
        >
          {page}
        </Pagination.Item>,
      )
    }

    // Show ellipsis if needed after current page
    if (safeCurrentPage < totalPages - 2) {
      items.push(<Pagination.Ellipsis key='ellipsis-end' disabled />)
    }

    // Always show last page if different from first
    if (totalPages > 1) {
      items.push(
        <Pagination.Item
          key={totalPages}
          active={safeCurrentPage === totalPages}
          onClick={() => setCurrentPage(totalPages)}
          disabled={safeCurrentPage === totalPages}
        >
          {totalPages}
        </Pagination.Item>,
      )
    }

    return items
  }

  if (loading && drafts.length === 0) {
    return (
      <Container className='py-5 text-center'>
        <Spinner animation='border' variant='primary' role='status' className='mb-3'>
          <span className='visually-hidden'>Loading...</span>
        </Spinner>
        <p>Loading drafts...</p>
      </Container>
    )
  }

  if (error) {
    return (
      <Container className='py-5 text-center'>
        <Alert variant='danger' className='mb-4'>
          <strong>Error:</strong> {error}
        </Alert>
        <Button onClick={() => fetchDrafts()} variant='primary'>
          Retry
        </Button>
      </Container>
    )
  }

  return (
    <Container className='py-4'>
      <div className='d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3'>
        <h1
          className='mb-0 d-flex align-items-center gap-2'
          style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}
        >
          <i className='bi bi-file-earmark-text'></i>
          My Recipe Drafts
        </h1>
        <Button onClick={handleCreateNew} variant='primary' size='md'>
          <i className='bi bi-plus-lg me-2'></i>
          Create New Draft
        </Button>
      </div>

      {successMessage && (
        <Alert variant='success' className='mb-4'>
          {successMessage}
        </Alert>
      )}

      <Nav variant='tabs' className='mb-4'>
        <Nav.Item>
          <Nav.Link
            active={activeTab === 'all'}
            onClick={() => setActiveTab('all')}
            className='d-flex align-items-center gap-2'
          >
            All{' '}
            <Badge bg='secondary' className='ms-1'>
              {getTabCount('all')}
            </Badge>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link
            active={activeTab === 'draft'}
            onClick={() => setActiveTab('draft')}
            className='d-flex align-items-center gap-2'
          >
            Pending{' '}
            <Badge bg='warning' className='ms-1'>
              {getTabCount('draft')}
            </Badge>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link
            active={activeTab === 'validated'}
            onClick={() => setActiveTab('validated')}
            className='d-flex align-items-center gap-2'
          >
            Validated{' '}
            <Badge bg='success' className='ms-1'>
              {getTabCount('validated')}
            </Badge>
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link
            active={activeTab === 'rejected'}
            onClick={() => setActiveTab('rejected')}
            className='d-flex align-items-center gap-2'
          >
            Rejected{' '}
            <Badge bg='danger' className='ms-1'>
              {getTabCount('rejected')}
            </Badge>
          </Nav.Link>
        </Nav.Item>
      </Nav>

      {paginatedDrafts.length > 0 ? (
        <>
          <Row xs={1} md={2} lg={3} className='g-4 mb-4'>
            {paginatedDrafts.map((draft) => (
              <Col key={draft.id}>
                <div className='position-relative h-100'>
                  <RecipeDraftCard
                    draft={draft}
                    onView={() => handleViewDraft(draft.id)}
                    showStatusBadge
                  />
                  {draft.status === 'draft' && (
                    <div className='position-absolute top-0 end-0 p-2'>
                      <Button
                        variant='danger'
                        size='sm'
                        onClick={(e) => handleDeleteDraft(draft.id, draft.status, e)}
                        title='Delete draft'
                        className='px-2 py-1'
                      >
                        <i className='bi bi-trash'></i>
                      </Button>
                    </div>
                  )}
                </div>
              </Col>
            ))}
          </Row>

          {totalPages > 1 && (
            <div className='d-flex justify-content-center'>
              <Pagination>
                <Pagination.First
                  onClick={() => setCurrentPage(1)}
                  disabled={safeCurrentPage === 1}
                  aria-label='First'
                />
                <Pagination.Prev
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={safeCurrentPage === 1}
                  aria-label='Previous'
                />
                {renderPaginationItems()}
                <Pagination.Next
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={safeCurrentPage === totalPages}
                  aria-label='Next'
                />
                <Pagination.Last
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={safeCurrentPage === totalPages}
                  aria-label='Last'
                />
              </Pagination>
            </div>
          )}
        </>
      ) : (
        <Container className='py-5 text-center'>
          <div className='mb-4'>
            <i className='bi bi-file-earmark-x text-muted' style={{ fontSize: '4rem' }}></i>
          </div>
          <h3 className='mb-2'>
            {activeTab === 'all'
              ? 'No drafts yet'
              : activeTab === 'draft'
                ? 'No pending drafts'
                : activeTab === 'validated'
                  ? 'No validated drafts'
                  : 'No rejected drafts'}
          </h3>
          <p className='text-muted mb-4'>
            {activeTab === 'all'
              ? 'Start by creating a new draft using the AI Recipe Builder.'
              : activeTab === 'draft'
                ? 'Generate new drafts using the AI Recipe Builder.'
                : activeTab === 'validated'
                  ? 'Validated drafts will appear here after you approve them.'
                  : 'Rejected drafts will appear here after you reject them.'}
          </p>
          <Button onClick={handleCreateNew} variant='primary'>
            <i className='bi bi-plus-lg me-2'></i>
            Create New Draft
          </Button>
        </Container>
      )}
    </Container>
  )
}
