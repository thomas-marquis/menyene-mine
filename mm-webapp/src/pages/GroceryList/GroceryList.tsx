import { useState, useEffect, useCallback } from 'react';
import { Button } from '../../components/common/Button/Button';
import { groceryService } from '../../services/groceryService';
import type { GroceryItem } from '../../types/grocery.types';
import styles from './GroceryList.module.css';

interface EditableItem extends GroceryItem {
  isEditing: boolean;
  editName: string;
  editQuantity: string;
}

export const GroceryListPage = () => {
  const [groceryItems, setGroceryItems] = useState<EditableItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newItemName, setNewItemName] = useState<string>('');
  const [newItemQuantity, setNewItemQuantity] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchGroceryItems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      const response = await groceryService.getAllGroceryItems(0, 1000);
      setGroceryItems(
        response.grocery_items.map((item) => ({
          ...item,
          isEditing: false,
          editName: item.name,
          editQuantity: item.quantity || '',
        }))
      );
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch grocery items. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch grocery items. Please try again later.');
      }
      console.error('Error fetching grocery items:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGroceryItems();
  }, [fetchGroceryItems]);

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newItemName.trim()) {
      setError('Item name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await groceryService.createGroceryItem({
        name: newItemName.trim(),
        quantity: newItemQuantity.trim() || null,
        is_completed: false,
      });
      setNewItemName('');
      setNewItemQuantity('');
      await fetchGroceryItems();
      setSuccessMessage('Grocery item added successfully!');
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to add grocery item. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to add grocery item. Please try again.');
      }
      console.error('Error adding grocery item:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = async (id: number) => {
    try {
      setLoading(true);
      setError(null);
      await groceryService.deleteGroceryItem(id);
      await fetchGroceryItems();
      setSuccessMessage('Grocery item deleted successfully!');
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to delete grocery item. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to delete grocery item. Please try again.');
      }
      console.error('Error deleting grocery item:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleCompletion = async (item: EditableItem) => {
    try {
      setLoading(true);
      setError(null);
      await groceryService.updateGroceryItem(item.id, {
        name: item.name,
        quantity: item.quantity || undefined,
        is_completed: !item.is_completed,
      });
      await fetchGroceryItems();
    } catch (err: any) {
      if (err.response) {
        setError('Failed to update grocery item. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to update grocery item. Please try again.');
      }
      console.error('Error toggling grocery item completion:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartEdit = (id: number) => {
    setGroceryItems(
      groceryItems.map((item) =>
        item.id === id
          ? { ...item, isEditing: true, editName: item.name, editQuantity: item.quantity || '' }
          : { ...item, isEditing: false }
      )
    );
  };

  const handleCancelEdit = (id: number) => {
    setGroceryItems(
      groceryItems.map((item) =>
        item.id === id
          ? { ...item, isEditing: false }
          : item
      )
    );
  };

  const handleSaveEdit = async (id: number) => {
    const item = groceryItems.find((i) => i.id === id);
    if (!item || !item.editName.trim()) {
      setError('Item name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await groceryService.updateGroceryItem(id, {
        name: item.editName.trim(),
        quantity: item.editQuantity.trim() || null,
        is_completed: item.is_completed,
      });
      await fetchGroceryItems();
      setSuccessMessage('Grocery item updated successfully!');
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to update grocery item. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to update grocery item. Please try again.');
      }
      console.error('Error updating grocery item:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditFieldChange = (id: number, field: 'editName' | 'editQuantity', value: string) => {
    setGroceryItems(
      groceryItems.map((item) =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  const handleClearCompleted = async () => {
    try {
      setLoading(true);
      setError(null);
      const completedItems = groceryItems.filter((item) => item.is_completed);
      for (const item of completedItems) {
        await groceryService.deleteGroceryItem(item.id);
      }
      await fetchGroceryItems();
      setSuccessMessage('Completed items cleared successfully!');
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to clear completed items. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to clear completed items. Please try again.');
      }
      console.error('Error clearing completed items:', err);
    } finally {
      setLoading(false);
    }
  };

  const completedCount = groceryItems.filter((item) => item.is_completed).length;
  const activeCount = groceryItems.length - completedCount;

  if (loading && groceryItems.length === 0) {
    return (
      <div className={styles.loadingContainer}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p>Loading grocery list...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
        <Button
          onClick={() => {
            setError(null);
            fetchGroceryItems();
          }}
          variant="primary"
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Retry'}
        </Button>
      </div>
    );
  }

  return (
    <div className={styles.groceryListContainer}>
      {successMessage && (
        <div className="alert alert-success" role="alert">
          {successMessage}
        </div>
      )}

      <div className={styles.header}>
        <h1 className={styles.title}>Grocery List</h1>
        {completedCount > 0 && (
          <Button
            onClick={handleClearCompleted}
            variant="danger"
            size="small"
            disabled={loading}
            className="btn-outline-danger"
          >
            <i className="bi bi-trash me-2"></i>
            Clear Completed ({completedCount})
          </Button>
        )}
      </div>

      <div className={styles.stats}>
        <span className={styles.stat}>
          <span className={styles.statNumber}>{activeCount}</span> active
        </span>
        <span className={styles.stat}>
          <span className={styles.statNumber}>{completedCount}</span> completed
        </span>
        <span className={styles.stat}>
          <span className={styles.statNumber}>{groceryItems.length}</span> total
        </span>
      </div>

      <form onSubmit={handleAddItem} className={styles.addForm}>
        <div className={styles.inputGroup}>
          <input
            type="text"
            className="form-control"
            placeholder="Item name (required)"
            value={newItemName}
            onChange={(e) => setNewItemName(e.target.value)}
            disabled={loading}
            required
          />
          <input
            type="text"
            className="form-control"
            placeholder="Quantity (optional)"
            value={newItemQuantity}
            onChange={(e) => setNewItemQuantity(e.target.value)}
            disabled={loading}
          />
          <Button
            type="submit"
            variant="primary"
            disabled={loading || !newItemName.trim()}
          >
            <i className="bi bi-plus-lg me-2"></i>
            Add Item
          </Button>
        </div>
      </form>

      {groceryItems.length > 0 ? (
        <div className={styles.groceryList}>
          {groceryItems.map((item) => (
            <div
              key={item.id}
              className={`${styles.groceryItem} ${item.is_completed ? styles.completed : ''}`}
            >
              {item.isEditing ? (
                <div className={styles.editForm}>
                  <input
                    type="text"
                    className="form-control"
                    value={item.editName}
                    onChange={(e) => handleEditFieldChange(item.id, 'editName', e.target.value)}
                    disabled={loading}
                    autoFocus
                  />
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Quantity (optional)"
                    value={item.editQuantity}
                    onChange={(e) => handleEditFieldChange(item.id, 'editQuantity', e.target.value)}
                    disabled={loading}
                  />
                  <div className={styles.editButtons}>
                    <Button
                      onClick={() => handleSaveEdit(item.id)}
                      variant="primary"
                      size="small"
                      disabled={loading || !item.editName.trim()}
                    >
                      <i className="bi bi-check-lg"></i>
                    </Button>
                    <Button
                      onClick={() => handleCancelEdit(item.id)}
                      variant="secondary"
                      size="small"
                      disabled={loading}
                    >
                      <i className="bi bi-x-lg"></i>
                    </Button>
                  </div>
                </div>
              ) : (
                <>
                  <div className={styles.itemContent}>
                    <input
                      type="checkbox"
                      checked={item.is_completed}
                      onChange={() => handleToggleCompletion(item)}
                      disabled={loading}
                      className={styles.checkbox}
                    />
                    <div className={styles.itemDetails}>
                      <span className={styles.itemName}>{item.name}</span>
                      {item.quantity && (
                        <span className={styles.itemQuantity}> - {item.quantity}</span>
                      )}
                    </div>
                  </div>
                  <div className={styles.actionButtons}>
                    <Button
                      onClick={() => handleStartEdit(item.id)}
                      variant="outline"
                      size="small"
                      disabled={loading}
                      className={styles.editButton}
                    >
                      <i className="bi bi-pencil"></i>
                    </Button>
                    <Button
                      onClick={() => handleDeleteItem(item.id)}
                      variant="danger"
                      size="small"
                      disabled={loading}
                      className={`${styles.deleteButton} btn-outline-danger`}
                    >
                      <i className="bi bi-trash"></i>
                    </Button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <i className="bi bi-cart text-muted" style={{ fontSize: '4rem' }}></i>
          </div>
          <h3>Your grocery list is empty</h3>
          <p>Start by adding items to your grocery list!</p>
        </div>
      )}
    </div>
  );
};
