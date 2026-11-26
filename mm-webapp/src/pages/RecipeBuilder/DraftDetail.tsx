import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '../../components/common/Button/Button'
import { Modal } from '../../components/common/Modal/Modal'
import { RecipeContent } from '../../components/recipe/RecipeContent'
import { recipeDraftService } from '../../services/recipeDraftService'
import { recipeService } from '../../services/recipeService'
import type { RecipeDraft } from '../../types/recipe_draft.types'
import { Container, Row, Col, Alert, Spinner, Card, Badge } from 'react-bootstrap'
import { useAppDispatch } from '../../store'
import { decrementPendingDraftCount, incrementRecipeCount } from '../../store/stats/slice'

export const DraftDetailPage = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const dispatch = useAppDispatch()

  const [draft, setDraft] = useState<RecipeDraft | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [isValidating, setIsValidating] = useState(false)
  const [isRejecting, setIsRejecting] = useState(false)
  const [showConfirmValidate, setShowConfirmValidate] = useState(false)
  const [showConfirmReject, setShowConfirmReject] = useState(false)

  const fetchDraft = useCallback(async () => {
    if (!id) return

    try {
      setLoading(true)
      setError(null)
      const draftData = await recipeDraftService.getDraftById(parseInt(id, 10))
      setDraft(draftData)
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe draft not found.')
      } else if (err.response) {
        setError('Failed to fetch draft. Please try again later.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to fetch draft. Please try again later.')
      }
      console.error('Error fetching draft:', err)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchDraft()
  }, [fetchDraft])

  useEffect(() => {
    if (id && isNaN(parseInt(id, 10))) {
      navigate('/404')
    }
  }, [id, navigate])

  const handleGoBack = () => {
    navigate('/recipes/drafts')
  }

  const handleValidate = async () => {
    if (!id || !draft) return

    try {
      setIsValidating(true)
      setError(null)
      setShowConfirmValidate(false)

      const response = await recipeDraftService.validateDraft(parseInt(id, 10))

      if (response.success && response.recipe) {
        setSuccessMessage('Draft validated and recipe created successfully!')
        setDraft({ ...draft, status: 'validated', recipe_id: response.recipe.id })

        dispatch(decrementPendingDraftCount())
        dispatch(incrementRecipeCount())

        // Refresh draft to get updated status
        await fetchDraft()

        setTimeout(() => {
          setSuccessMessage(null)
          // Navigate to the new recipe after a delay
          if (response.recipe && response.recipe.id) {
            navigate(`/recipes/${response.recipe.id}`)
          }
        }, 2000)
      } else {
        setError('Failed to validate draft. Please try again.')
      }
    } catch (err: any) {
      setError('Failed to validate draft. Please try again.')
      console.error('Error validating draft:', err)
    } finally {
      setIsValidating(false)
    }
  }

  const handleReject = async () => {
    if (!id || !draft) return

    try {
      setIsRejecting(true)
      setError(null)
      setShowConfirmReject(false)

      const response = await recipeDraftService.rejectDraft(parseInt(id, 10))

      if (response.success) {
        setSuccessMessage('Draft rejected successfully!')
        setDraft({ ...draft, status: 'rejected' })
        dispatch(decrementPendingDraftCount())
        setTimeout(() => setSuccessMessage(null), 3000)
      } else {
        setError('Failed to reject draft. Please try again.')
      }
    } catch (err: any) {
      setError('Failed to reject draft. Please try again.')
      console.error('Error rejecting draft:', err)
    } finally {
      setIsRejecting(false)
    }
  }

  const handleDelete = async () => {
    if (!id || !draft) return

    if (
      window.confirm('Are you sure you want to delete this draft? This action cannot be undone.')
    ) {
      try {
        await recipeDraftService.deleteDraft(parseInt(id, 10))
        if (draft.status === 'draft') {
          dispatch(decrementPendingDraftCount())
        }
        setSuccessMessage('Draft deleted successfully!')
        setTimeout(() => {
          navigate('/recipes/drafts')
        }, 1500)
      } catch (err: any) {
        setError('Failed to delete draft. Please try again.')
        console.error('Error deleting draft:', err)
      }
    }
  }

  const handleViewRecipe = async () => {
    if (!draft || !draft.recipe_id) return

    try {
      const recipe = await recipeService.getRecipeById(draft.recipe_id)
      navigate(`/recipes/${recipe.id}`)
    } catch (err) {
      setError('Failed to load recipe. It may have been deleted.')
      console.error('Error loading recipe:', err)
    }
  }

  // Map status to Bootstrap badge variant
  const getStatusVariant = (status: string): string => {
    switch (status) {
      case 'validated':
        return 'success'
      case 'rejected':
        return 'danger'
      default:
        return 'warning'
    }
  }

  // Map status to display text
  const getStatusText = (status: string): string => {
    switch (status) {
      case 'validated':
        return 'Validated'
      case 'rejected':
        return 'Rejected'
      default:
        return 'Draft'
    }
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const renderRecipeContent = () => {
    if (!draft) return null

    const content = draft.generated_content
    const title = content.title || 'Untitled Recipe'
    const summary = content.summary || 'No summary available'
    const ingredients = content.ingredients || []
    const instructions = content.instructions || []
    const servings = content.servings || 4
    const prepTime = content.prep_time || '0 minutes'
    const cookTime = content.cook_time || '0 minutes'
    const difficulty = content.difficulty || 'Medium'

    return (
      <Card className='mb-4'>
        <Card.Body>
          <h2 className='mb-3' style={{ fontSize: '1.5rem', fontWeight: 600, color: '#2c3e50' }}>
            {title}
          </h2>

          <div className='mb-4'>
            <h4 className='mb-2'>Summary</h4>
            <p className='text-muted'>{summary}</p>
          </div>

          <RecipeContent
            ingredients={ingredients}
            instructions={instructions}
            servings={servings}
            prep_time={prepTime}
            cook_time={cookTime}
            difficulty={difficulty}
            showTitle={false}
            showSummary={false}
          />
        </Card.Body>
      </Card>
    )
  }

  if (loading) {
    return (
      <Container className='py-5 text-center'>
        <Spinner animation='border' variant='primary' role='status' className='mb-3'>
          <span className='visually-hidden'>Loading...</span>
        </Spinner>
        <p>Loading draft...</p>
      </Container>
    )
  }

  if (error) {
    return (
      <Container className='py-5 text-center'>
        <Alert variant='danger' className='mb-4'>
          <strong>Error:</strong> {error}
        </Alert>
        <div className='d-flex justify-content-center gap-2'>
          <Button onClick={() => fetchDraft()} variant='primary' disabled={loading}>
            {loading ? 'Loading...' : 'Retry'}
          </Button>
          <Button onClick={handleGoBack} variant='secondary' disabled={loading}>
            Back to Drafts
          </Button>
        </div>
      </Container>
    )
  }

  if (!draft) {
    return (
      <Container className='py-5 text-center'>
        <Alert variant='warning' className='mb-4'>
          Recipe draft not found
        </Alert>
        <Button onClick={handleGoBack} variant='secondary'>
          Back to Drafts
        </Button>
      </Container>
    )
  }

  return (
    <Container className='py-4'>
      {/* Header with actions */}
      <div className='d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3'>
        <Button onClick={handleGoBack} variant='outline' size='md' disabled={loading}>
          <i className='bi bi-arrow-left me-2'></i>
          Back to Drafts
        </Button>

        <div className='d-flex flex-wrap gap-2'>
          {draft.status === 'draft' && (
            <>
              <Button
                onClick={() => setShowConfirmReject(true)}
                variant='danger'
                size='md'
                disabled={isValidating || isRejecting}
              >
                <i className='bi bi-x-circle me-2'></i>
                Reject
              </Button>
              <Button
                onClick={() => setShowConfirmValidate(true)}
                variant='primary'
                size='md'
                disabled={isValidating || isRejecting}
              >
                <i className='bi bi-check-circle me-2'></i>
                Validate & Create Recipe
              </Button>
            </>
          )}

          {draft.status === 'validated' && draft.recipe_id && (
            <Button onClick={handleViewRecipe} variant='primary' size='md'>
              <i className='bi bi-eye me-2'></i>
              View Recipe
            </Button>
          )}

          <Button
            onClick={handleDelete}
            variant='outline'
            size='md'
            disabled={isValidating || isRejecting}
          >
            <i className='bi bi-trash me-2'></i>
            Delete
          </Button>
        </div>
      </div>

      {successMessage && (
        <Alert variant='success' className='mb-4'>
          {successMessage}
        </Alert>
      )}

      {/* Draft Meta */}
      <div className='d-flex flex-wrap justify-content-between align-items-center mb-4 gap-3'>
        <h1 className='mb-0' style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
          Draft #{draft.id}
        </h1>
        <Badge bg={getStatusVariant(draft.status)} className='p-2'>
          {getStatusText(draft.status)}
        </Badge>
      </div>

      {/* Draft Info */}
      <Card className='mb-4'>
        <Card.Body>
          <Row className='g-3'>
            <Col md={6}>
              <div className='d-flex gap-2'>
                <span className='text-muted small'>Created:</span>
                <span>{formatDate(draft.created_at)}</span>
              </div>
            </Col>
            <Col md={6}>
              <div className='d-flex gap-2'>
                <span className='text-muted small'>Updated:</span>
                <span>{formatDate(draft.updated_at)}</span>
              </div>
            </Col>
            {draft.recipe_id && (
              <Col md={12}>
                <div className='d-flex gap-2'>
                  <span className='text-muted small'>Recipe ID:</span>
                  <Badge bg='light' text='primary' className='p-1'>
                    {draft.recipe_id}
                  </Badge>
                </div>
              </Col>
            )}
          </Row>
        </Card.Body>
      </Card>

      {/* User Prompt */}
      <Card className='mb-4'>
        <Card.Header className='bg-white border-0'>
          <h3 className='mb-0' style={{ fontSize: '1.25rem', fontWeight: 600, color: '#2c3e50' }}>
            User Prompt
          </h3>
        </Card.Header>
        <Card.Body>
          <p className='mb-0'>{draft.user_instruction}</p>
        </Card.Body>
      </Card>

      {renderRecipeContent()}

      {/* Confirmation Modals */}
      {showConfirmValidate && (
        <Modal
          isOpen={showConfirmValidate}
          onClose={() => setShowConfirmValidate(false)}
          title='Confirm Validation'
          closeOnOverlayClick={!isValidating}
          closeOnEscape={!isValidating}
        >
          <p>Are you sure you want to validate this draft and create a recipe from it?</p>
          <p className='text-muted'>
            This will create a new recipe in your catalog with the title:
            <strong>{draft.generated_content.title || 'Untitled Recipe'}</strong>
          </p>
          <div className='d-flex justify-content-end gap-2 mt-4'>
            <Button
              onClick={() => setShowConfirmValidate(false)}
              variant='secondary'
              disabled={isValidating}
            >
              Cancel
            </Button>
            <Button
              onClick={handleValidate}
              variant='primary'
              loading={isValidating}
              disabled={isValidating}
            >
              {isValidating ? 'Validating...' : 'Validate & Create Recipe'}
            </Button>
          </div>
        </Modal>
      )}

      {showConfirmReject && (
        <Modal
          isOpen={showConfirmReject}
          onClose={() => setShowConfirmReject(false)}
          title='Confirm Rejection'
          closeOnOverlayClick={!isRejecting}
          closeOnEscape={!isRejecting}
        >
          <p>Are you sure you want to reject this draft?</p>
          <p className='text-muted'>
            You can still view it later in the "Rejected" tab, but it won't be created as a recipe.
          </p>
          <div className='d-flex justify-content-end gap-2 mt-4'>
            <Button
              onClick={() => setShowConfirmReject(false)}
              variant='secondary'
              disabled={isRejecting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleReject}
              variant='danger'
              loading={isRejecting}
              disabled={isRejecting}
            >
              {isRejecting ? 'Rejecting...' : 'Reject Draft'}
            </Button>
          </div>
        </Modal>
      )}
    </Container>
  )
}
