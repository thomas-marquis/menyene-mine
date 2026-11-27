import { useState, useEffect, useCallback } from 'react'
import { Button } from '../../components/common/Button/Button'
import { groceryService } from '../../services/groceryService'
import type { GroceryItem } from '../../types/grocery.types'
import { Container, Row, Col, Form, Alert, Badge, ListGroup, Spinner } from 'react-bootstrap'
import { useAppDispatch } from '../../store'
import {
  incrementUncheckedGroceryCount,
  decrementUncheckedGroceryCount,
} from '../../store/stats/slice'

interface EditableItem extends GroceryItem {
  isEditing: boolean
  editName: string
  editQuantity: string
}

export const GroceryListPage = () => {
  const dispatch = useAppDispatch()
  const [groceryItems, setGroceryItems] = useState<EditableItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [newItemName, setNewItemName] = useState<string>('')
  const [newItemQuantity, setNewItemQuantity] = useState<string>('')
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const fetchGroceryItems = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      setSuccessMessage(null)
      const response = await groceryService.getAllGroceryItems(0, 1000)
      setGroceryItems(
        response.grocery_items.map((item) => ({
          ...item,
          isEditing: false,
          editName: item.name,
          editQuantity: item.quantity || '',
        })),
      )
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch grocery items. Please try again later.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to fetch grocery items. Please try again later.')
      }
      console.error('Error fetching grocery items:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchGroceryItems()
  }, [fetchGroceryItems])

  const handleAddItem = async (e: React.SubmitEvent) => {
    e.preventDefault()
    if (!newItemName.trim()) {
      setError('Item name is required')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await groceryService.createGroceryItem({
        name: newItemName.trim(),
        quantity: newItemQuantity.trim() || null,
        is_completed: false,
      })
      dispatch(incrementUncheckedGroceryCount())
      setNewItemName('')
      setNewItemQuantity('')
      await fetchGroceryItems()
      setSuccessMessage('Grocery item added successfully!')
      setTimeout(() => {
        setSuccessMessage(null)
      }, 3000)
    } catch (err: any) {
      if (err.response) {
        setError('Failed to add grocery item. Please try again.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to add grocery item. Please try again.')
      }
      console.error('Error adding grocery item:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteItem = async (id: number, isCompleted: boolean) => {
    try {
      setLoading(true)
      setError(null)
      await groceryService.deleteGroceryItem(id)
      if (!isCompleted) {
        dispatch(decrementUncheckedGroceryCount())
      }
      await fetchGroceryItems()
      setSuccessMessage('Grocery item deleted successfully!')
      setTimeout(() => {
        setSuccessMessage(null)
      }, 3000)
    } catch (err: any) {
      if (err.response) {
        setError('Failed to delete grocery item. Please try again.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to delete grocery item. Please try again.')
      }
      console.error('Error deleting grocery item:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleCompletion = async (item: EditableItem) => {
    try {
      setLoading(true)
      setError(null)
      const newCompletedStatus = !item.is_completed
      await groceryService.updateGroceryItem(item.id, {
        name: item.name,
        quantity: item.quantity || undefined,
        is_completed: newCompletedStatus,
      })
      if (newCompletedStatus) {
        dispatch(decrementUncheckedGroceryCount())
      } else {
        dispatch(incrementUncheckedGroceryCount())
      }
      await fetchGroceryItems()
    } catch (err: any) {
      if (err.response) {
        setError('Failed to update grocery item. Please try again.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to update grocery item. Please try again.')
      }
      console.error('Error toggling grocery item completion:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleStartEdit = (id: number) => {
    setGroceryItems(
      groceryItems.map((item) =>
        item.id === id
          ? { ...item, isEditing: true, editName: item.name, editQuantity: item.quantity || '' }
          : { ...item, isEditing: false },
      ),
    )
  }

  const handleCancelEdit = (id: number) => {
    setGroceryItems(
      groceryItems.map((item) => (item.id === id ? { ...item, isEditing: false } : item)),
    )
  }

  const handleSaveEdit = async (id: number) => {
    const item = groceryItems.find((i) => i.id === id)
    if (!item || !item.editName.trim()) {
      setError('Item name is required')
      return
    }

    try {
      setLoading(true)
      setError(null)
      await groceryService.updateGroceryItem(id, {
        name: item.editName.trim(),
        quantity: item.editQuantity.trim() || null,
        is_completed: item.is_completed,
      })
      await fetchGroceryItems()
      setSuccessMessage('Grocery item updated successfully!')
      setTimeout(() => {
        setSuccessMessage(null)
      }, 3000)
    } catch (err: any) {
      if (err.response) {
        setError('Failed to update grocery item. Please try again.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to update grocery item. Please try again.')
      }
      console.error('Error updating grocery item:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleEditFieldChange = (id: number, field: 'editName' | 'editQuantity', value: string) => {
    setGroceryItems(
      groceryItems.map((item) => (item.id === id ? { ...item, [field]: value } : item)),
    )
  }

  const handleClearCompleted = async () => {
    try {
      setLoading(true)
      setError(null)
      const completedItems = groceryItems.filter((item) => item.is_completed)
      for (const item of completedItems) {
        await groceryService.deleteGroceryItem(item.id)
      }
      await fetchGroceryItems()
      setSuccessMessage('Completed items cleared successfully!')
      setTimeout(() => {
        setSuccessMessage(null)
      }, 3000)
    } catch (err: any) {
      if (err.response) {
        setError('Failed to clear completed items. Please try again.')
      } else if (err.request) {
        setError('Network error. Please check your connection.')
      } else {
        setError('Failed to clear completed items. Please try again.')
      }
      console.error('Error clearing completed items:', err)
    } finally {
      setLoading(false)
    }
  }

  const completedCount = groceryItems.filter((item) => item.is_completed).length
  const activeCount = groceryItems.length - completedCount

  if (loading && groceryItems.length === 0) {
    return (
      <Container className='py-5 text-center'>
        <Spinner animation='border' variant='primary' role='status' className='mb-3'>
          <span className='visually-hidden'>Loading...</span>
        </Spinner>
        <p>Loading grocery list...</p>
      </Container>
    )
  }

  if (error) {
    return (
      <Container className='py-5 text-center'>
        <Alert variant='danger' className='mb-4'>
          {error}
        </Alert>
        <Button
          onClick={() => {
            setError(null)
            fetchGroceryItems()
          }}
          variant='primary'
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Retry'}
        </Button>
      </Container>
    )
  }

  return (
    <Container className='py-4'>
      {successMessage && (
        <Alert variant='success' className='mb-4'>
          {successMessage}
        </Alert>
      )}

      {/* Header */}
      <div className='d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3'>
        <h1 className='mb-0' style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
          Grocery List
        </h1>
        {completedCount > 0 && (
          <Button
            onClick={handleClearCompleted}
            variant='danger'
            size='sm'
            disabled={loading}
            className='btn-outline-danger text-white'
            style={{ borderColor: '#dc3545' }}
          >
            <i className='bi bi-trash me-2'></i>
            Clear Completed ({completedCount})
          </Button>
        )}
      </div>

      {/* Stats */}
      <div className='d-flex gap-4 mb-4 flex-wrap'>
        <Badge bg='primary' className='p-2'>
          <span className='fw-bold'>{activeCount}</span> active
        </Badge>
        <Badge bg='success' className='p-2'>
          <span className='fw-bold'>{completedCount}</span> completed
        </Badge>
        <Badge bg='secondary' className='p-2'>
          <span className='fw-bold'>{groceryItems.length}</span> total
        </Badge>
      </div>

      {/* Add Form */}
      <Form onSubmit={handleAddItem} className='mb-4'>
        <div className='d-flex flex-column align-items-center gap-2'>
          <Form.Control
            type='text'
            placeholder='Item name (required)'
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            disabled={loading}
            required
            className='w-100'
            style={{ maxWidth: '400px' }}
          />
          <Form.Control
            type='text'
            placeholder='Quantity (optional)'
            value={newItemQuantity}
            onChange={(e) => setNewItemQuantity(e.target.value)}
            disabled={loading}
            className='w-100'
            style={{ maxWidth: '400px' }}
          />
          <Button
            type='submit'
            variant='primary'
            disabled={loading || !newItemName.trim()}
            className='w-100'
            style={{ maxWidth: '400px' }}
          >
            <i className='bi bi-plus-lg me-2'></i>
            Add Item
          </Button>
        </div>
      </Form>

      {/* Grocery List */}
      <Container className='mx-auto' style={{ maxWidth: '800px' }}>
        {groceryItems.length > 0 ? (
          <ListGroup variant='flush'>
            {groceryItems.map((item) => (
              <ListGroup.Item
                key={item.id}
                className={`border-0 border-bottom px-0 py-3 ${item.is_completed ? 'text-muted' : ''}`}
                style={{ backgroundColor: 'transparent' }}
              >
                {item.isEditing ? (
                  <Row className='g-2 align-items-center'>
                    <Col md={4}>
                      <Form.Control
                        type='text'
                        value={item.editName}
                        onChange={(e) => handleEditFieldChange(item.id, 'editName', e.target.value)}
                        disabled={loading}
                        autoFocus
                        size='sm'
                      />
                    </Col>
                    <Col md={3}>
                      <Form.Control
                        type='text'
                        placeholder='Quantity (optional)'
                        value={item.editQuantity}
                        onChange={(e) =>
                          handleEditFieldChange(item.id, 'editQuantity', e.target.value)
                        }
                        disabled={loading}
                        size='sm'
                      />
                    </Col>
                    <Col md={5} className='d-flex gap-2 justify-content-end'>
                      <Button
                        onClick={() => handleSaveEdit(item.id)}
                        variant='primary'
                        size='sm'
                        disabled={loading || !item.editName.trim()}
                      >
                        <i className='bi bi-check-lg'></i>
                      </Button>
                      <Button
                        onClick={() => handleCancelEdit(item.id)}
                        variant='secondary'
                        size='sm'
                        disabled={loading}
                      >
                        <i className='bi bi-x-lg'></i>
                      </Button>
                    </Col>
                  </Row>
                ) : (
                  <Row className='g-2 align-items-center'>
                    <Col className='d-flex align-items-center gap-2'>
                      <Form.Check
                        type='checkbox'
                        checked={item.is_completed}
                        onChange={() => handleToggleCompletion(item)}
                        disabled={loading}
                        id={`item-${item.id}`}
                        className='mt-0'
                      />
                      <div>
                        <span
                          className={`fw-medium ${item.is_completed ? 'text-decoration-line-through' : ''}`}
                        >
                          {item.name}
                        </span>
                        {item.quantity && (
                          <span
                            className={`text-muted ms-2 ${item.is_completed ? 'text-decoration-line-through' : ''}`}
                          >
                            - {item.quantity}
                          </span>
                        )}
                      </div>
                    </Col>
                    <Col className='d-flex gap-2 justify-content-end'>
                      <Button
                        onClick={() => handleStartEdit(item.id)}
                        variant='outline'
                        size='sm'
                        disabled={loading}
                        className='px-2 py-1'
                      >
                        <i className='bi bi-pencil'></i>
                      </Button>
                      <Button
                        onClick={() => handleDeleteItem(item.id, item.is_completed)}
                        variant='danger'
                        size='sm'
                        disabled={loading}
                        className='px-2 py-1 btn-outline-danger text-white'
                        style={{ borderColor: '#dc3545' }}
                      >
                        <i className='bi bi-trash'></i>
                      </Button>
                    </Col>
                  </Row>
                )}
              </ListGroup.Item>
            ))}
          </ListGroup>
        ) : (
          <Container className='py-5 text-center'>
            <div className='mb-4'>
              <i className='bi bi-cart text-muted' style={{ fontSize: '4rem' }}></i>
            </div>
            <h3 className='mb-2'>Your grocery list is empty</h3>
            <p className='text-muted mb-4'>Start by adding items to your grocery list!</p>
          </Container>
        )}
      </Container>
    </Container>
  )
}
