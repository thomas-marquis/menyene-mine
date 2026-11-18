import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button/Button';
import { Modal } from '../../components/common/Modal/Modal';
import { RecipeContent } from '../../components/recipe/RecipeContent';
import { RecipeFormModal } from '../../components/recipe/RecipeFormModal/RecipeFormModal';
import { recipeService } from '../../services/recipeService';
import { mealService } from '../../services/mealService';
import type { Recipe } from '../../types/recipe.types';
import type { Meal, MealMoment } from '../../types/meal.types';
import { Container, Alert, Spinner, Badge } from 'react-bootstrap';
import { useAppDispatch } from '../../store';
import { decrementRecipeCount } from '../../store/statsSlice';

const DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

// Helper to format date for API (YYYY-MM-DD)
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// Helper to get calendar data for a month
function getCalendarMonth(year: number, month: number, meals: Meal[]): {
  year: number;
  month: number;
  weeks: { days: { date: Date; day: number; month: number; year: number; isCurrentMonth: boolean; isToday: boolean; lunchMeal: Meal | null; dinnerMeal: Meal | null }[] }[];
  monthName: string;
} {
  const date = new Date(year, month - 1, 1);
  const firstDay = date.getDay(); // 0 (Sunday) to 6 (Saturday)
  const daysInMonth = new Date(year, month, 0).getDate();
  
  // Get meals indexed by date and moment for quick lookup
  const mealsMap: Record<string, Record<MealMoment, Meal>> = {};
  meals.forEach(meal => {
    const dateStr = meal.date;
    if (!mealsMap[dateStr]) {
      mealsMap[dateStr] = {} as Record<MealMoment, Meal>;
    }
    mealsMap[dateStr][meal.moment] = meal;
  });

  // Build calendar days
  const days: { date: Date; day: number; month: number; year: number; isCurrentMonth: boolean; isToday: boolean; lunchMeal: Meal | null; dinnerMeal: Meal | null }[] = [];
  
  // Calculate how many days from previous month to show (to start from Monday)
  const daysFromPrevMonth = firstDay === 0 ? 6 : firstDay - 1;
  
  // Add days from previous month to fill the first week (to start from Monday)
  const prevMonthDays = new Date(year, month - 1, 0).getDate();
  for (let i = daysFromPrevMonth - 1; i >= 0; i--) {
    const day = prevMonthDays - i;
    const dateObj = new Date(year, month - 2, day);
    days.push({
      date: dateObj,
      day,
      month: month - 1,
      year: month === 1 ? year - 1 : year,
      isCurrentMonth: false,
      isToday: false,
      lunchMeal: null,
      dinnerMeal: null,
    });
  }

  // Add days from current month
  const today = new Date();
  for (let day = 1; day <= daysInMonth; day++) {
    const dateObj = new Date(year, month - 1, day);
    const dateStr = formatDate(dateObj);
    const isToday = dateObj.toDateString() === today.toDateString();
    
    days.push({
      date: dateObj,
      day,
      month,
      year,
      isCurrentMonth: true,
      isToday,
      lunchMeal: mealsMap[dateStr]?.lunch || null,
      dinnerMeal: mealsMap[dateStr]?.dinner || null,
    });
  }

  // Add days from next month to fill the last week
  const totalDays = days.length;
  const remainingDays = 7 - (totalDays % 7);
  if (remainingDays < 7) {
    for (let day = 1; day <= remainingDays; day++) {
      const dateObj = new Date(year, month, day);
      days.push({
        date: dateObj,
        day,
        month: month + 1,
        year: month === 12 ? year + 1 : year,
        isCurrentMonth: false,
        isToday: false,
        lunchMeal: null,
        dinnerMeal: null,
      });
    }
  }

  // Split into weeks
  const weeks: { days: { date: Date; day: number; month: number; year: number; isCurrentMonth: boolean; isToday: boolean; lunchMeal: Meal | null; dinnerMeal: Meal | null }[] }[] = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push({ days: days.slice(i, i + 7) });
  }

  return {
    year,
    month,
    weeks,
    monthName: MONTH_NAMES[month - 1],
  };
}

// Helper to format date for display
function formatDateForDisplay(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

// Helper to truncate text
function truncateText(text: string, maxLength: number = 15): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export const RecipeDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  // Check if ID is valid
  useEffect(() => {
    if (id && isNaN(parseInt(id, 10))) {
      navigate('/404');
    }
  }, [id, navigate]);
  
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<boolean>(false);
  
  // Plan meal modal state
  const [showPlanMealModal, setShowPlanMealModal] = useState<boolean>(false);
  const [planMealDate, setPlanMealDate] = useState<string | null>(null);
  const [planMealMoment, setPlanMealMoment] = useState<MealMoment | null>(null);
  const [planMealError, setPlanMealError] = useState<string | null>(null);
  const [meals, setMeals] = useState<Meal[]>([]);
  const [mealsLoading, setMealsLoading] = useState<boolean>(false);
  const [calendarDate, setCalendarDate] = useState<Date>(new Date());
  
  const fetchRecipe = useCallback(async () => {
    if (!id) return;
  
    try {
      setLoading(true);
      setError(null);
      setSuccessMessage(null);
      const recipeData = await recipeService.getRecipeById(parseInt(id, 10));
      setRecipe(recipeData);
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe not found.');
      } else if (err.response) {
        setError('Failed to fetch recipe. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch recipe. Please try again later.');
      }
      console.error('Error fetching recipe:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  // Fetch meals for calendar modal
  const fetchMealsForMonth = useCallback(async (year: number, month: number) => {
    try {
      setMealsLoading(true);
      setPlanMealError(null);
      const response = await mealService.getMealsForMonth(year, month);
      setMeals(response.meals);
    } catch (err: any) {
      setPlanMealError('Failed to fetch meal plans. Please try again.');
      console.error('Error fetching meals:', err);
    } finally {
      setMealsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRecipe();
  }, [fetchRecipe]);

  useEffect(() => {
    setSuccessMessage(null);
  }, [id]);

  // Handle plan meal button click
  const handlePlanMeal = () => {
    if (recipe) {
      setPlanMealDate(null);
      setPlanMealMoment(null);
      setPlanMealError(null);
      setCalendarDate(new Date());
      fetchMealsForMonth(new Date().getFullYear(), new Date().getMonth() + 1);
      setShowPlanMealModal(true);
    }
  };

  // Handle calendar cell click
  const handleCalendarCellClick = (day: { date: Date; day: number; month: number; year: number; isCurrentMonth: boolean; isToday: boolean; lunchMeal: Meal | null; dinnerMeal: Meal | null }, moment: MealMoment) => {
    if (!day.isCurrentMonth) return;
    
    const dateStr = formatDate(day.date);
    const existingMeal = moment === 'lunch' ? day.lunchMeal : day.dinnerMeal;
    
    // If there's an existing meal, ask for confirmation to replace
    if (existingMeal) {
      if (window.confirm(`A meal already exists for ${formatDateForDisplay(dateStr)} ${moment}. Replace it with ${recipe?.title}?`)) {
        setPlanMealDate(dateStr);
        setPlanMealMoment(moment);
        // Don't close modal, just select the cell
      }
    } else {
      setPlanMealDate(dateStr);
      setPlanMealMoment(moment);
    }
  };

  // Handle save meal plan
  const handleSaveMealPlan = async () => {
    if (!planMealDate || !planMealMoment || !recipe) return;
    
    try {
      // Check if there's an existing meal for this date and moment
      const existingMeal = meals.find(m => m.date === planMealDate && m.moment === planMealMoment);
      
      if (existingMeal) {
        // Update existing meal
        await mealService.updateMeal(existingMeal.id, { recipe_id: recipe.id });
      } else {
        // Create new meal
        await mealService.createMeal({
          date: planMealDate,
          moment: planMealMoment,
          recipe_id: recipe.id,
        });
      }
      
      setShowPlanMealModal(false);
      setSuccessMessage(`Meal planned for ${formatDateForDisplay(planMealDate)} ${planMealMoment}!`);
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      if (err.response?.status === 409) {
        setPlanMealError('A meal already exists for this date and time.');
      } else {
        setPlanMealError('Failed to save meal plan. Please try again.');
      }
      console.error('Error saving meal plan:', err);
    }
  };

  // Calendar navigation
  const goToPreviousMonth = () => {
    const newDate = new Date(calendarDate.getFullYear(), calendarDate.getMonth() - 1, 1);
    setCalendarDate(newDate);
    fetchMealsForMonth(newDate.getFullYear(), newDate.getMonth() + 1);
  };

  const goToNextMonth = () => {
    const newDate = new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1, 1);
    setCalendarDate(newDate);
    fetchMealsForMonth(newDate.getFullYear(), newDate.getMonth() + 1);
  };

  const goToCurrentMonth = () => {
    const newDate = new Date();
    setCalendarDate(newDate);
    fetchMealsForMonth(newDate.getFullYear(), newDate.getMonth() + 1);
  };

  const handleGoBack = () => {
    setError(null);
    setSuccessMessage(null);
    navigate('/');
  };

  const handleEdit = () => {
    if (recipe) {
      setError(null);
      setShowEditModal(true);
    }
  };

  const handleDelete = () => {
    if (recipe) {
      setError(null);
      setShowDeleteConfirm(true);
    }
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setError(null);
  };

  const handleRecipeUpdated = () => {
    setShowEditModal(false);
    setError(null);
    fetchRecipe();
    setSuccessMessage('Recipe updated successfully!');
    setTimeout(() => {
      setSuccessMessage(null);
    }, 3000);
  };

  const handleCloseDeleteConfirm = () => {
    setShowDeleteConfirm(false);
    setError(null);
  };

  const handleConfirmDelete = async () => {
    if (!id) return;

    setDeleting(true);
    setError(null);
    try {
      await recipeService.deleteRecipe(parseInt(id, 10));
      dispatch(decrementRecipeCount());
      setSuccessMessage('Recipe deleted successfully!');
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        setError('Recipe not found.');
      } else if (err.response) {
        setError('Failed to delete recipe. Please try again.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to delete recipe. Please try again.');
      }
      console.error('Error deleting recipe:', err);
    } finally {
      setDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  // Get calendar data
  const calendar = getCalendarMonth(
    calendarDate.getFullYear(),
    calendarDate.getMonth() + 1,
    meals
  );

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" role="status" className="mb-3">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p>Loading recipe...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
        <div className="d-flex justify-content-center gap-2">
          <Button
            onClick={() => {
              setError(null);
              fetchRecipe();
            }}
            variant="primary"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Retry'}
          </Button>
          <Button onClick={handleGoBack} variant="secondary" disabled={loading}>
            Back to Recipes
          </Button>
        </div>
      </Container>
    );
  }

  if (successMessage && !recipe) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="success" className="mb-4">
          {successMessage}
        </Alert>
        <Button onClick={() => navigate('/')} variant="primary">
          Back to Recipes
        </Button>
      </Container>
    );
  }

  if (!recipe) {
    return (
      <Container className="py-5 text-center">
        <Alert variant="warning" className="mb-4">
          Recipe not found
        </Alert>
        <Button onClick={handleGoBack} variant="secondary" disabled={loading}>
          Back to Recipes
        </Button>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      {/* Header with actions */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3">
        <Button
          onClick={handleGoBack}
          variant="outline"
          size="md"
          disabled={loading}
        >
          <i className="bi bi-arrow-left me-2"></i>
          Back to Recipes
        </Button>
        <div className="d-flex gap-2">
          <Button
            onClick={handlePlanMeal}
            variant="primary"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-calendar-plus me-2"></i>
            Plan Meal
          </Button>
          <Button
            onClick={handleEdit}
            variant="secondary"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-pencil me-2"></i>
            Edit
          </Button>
          <Button
            onClick={handleDelete}
            variant="danger"
            size="md"
            disabled={loading}
          >
            <i className="bi bi-trash me-2"></i>
            Delete
          </Button>
        </div>
      </div>

      {/* Recipe Content */}
      <div className="mb-4">
        {successMessage && (
          <Alert variant="success" className="mb-4">
            {successMessage}
          </Alert>
        )}
        
        <h1 className="mb-3" style={{ fontSize: '2.5rem', fontWeight: 700, color: '#2c3e50' }}>
          {recipe.title}
        </h1>

        <div className="d-flex flex-wrap gap-3 mb-4 text-muted small">
          <Badge bg="light" text="secondary" className="p-2">
            <i className="bi bi-calendar me-2"></i>
            Created: {formatDate(new Date(recipe.creation_date))}
          </Badge>
          <Badge bg="light" text="secondary" className="p-2">
            <i className="bi bi-clock me-2"></i>
            Updated: {formatDate(new Date(recipe.last_updated))}
          </Badge>
        </div>

        <div className="mb-4">
          <p className="lead" style={{ color: '#7f8c8d' }}>
            {recipe.summary}
          </p>
        </div>

        <div className="border-top pt-4">
          <RecipeContent
            title={recipe.title}
            summary={recipe.summary}
            ingredients={recipe.ingredients}
            instructions={recipe.instructions}
            servings={recipe.servings}
            prep_time={recipe.prep_time}
            cook_time={recipe.cook_time}
            difficulty={recipe.difficulty}
            showTitle={false}
            showSummary={false}
          />
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <RecipeFormModal
          isOpen={showEditModal}
          onClose={handleCloseEditModal}
          onSuccess={handleRecipeUpdated}
          recipe={recipe}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <Modal
          isOpen={showDeleteConfirm}
          onClose={handleCloseDeleteConfirm}
          title="Confirm Deletion"
          closeOnOverlayClick={!deleting}
          closeOnEscape={!deleting}
        >
          <p>Are you sure you want to delete "{recipe.title}"? This action cannot be undone.</p>
          <div className="d-flex justify-content-end gap-2 mt-4">
            <Button
              onClick={handleCloseDeleteConfirm}
              variant="secondary"
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmDelete}
              variant="danger"
              loading={deleting}
              disabled={deleting}
            >
              Delete
            </Button>
          </div>
        </Modal>
      )}

      {/* Plan Meal Modal */}
      {showPlanMealModal && (
        <Modal
          isOpen={showPlanMealModal}
          onClose={() => setShowPlanMealModal(false)}
          title="Plan Meal"
          size="lg"
        >
          <div className="plan-meal-modal">
            <p className="mb-4">
              Select a date and meal time to plan "{recipe.title}"
            </p>
            
            {planMealError && (
              <Alert variant="danger" className="mb-3" dismissible onClose={() => setPlanMealError(null)}>
                {planMealError}
              </Alert>
            )}
            
            {/* Calendar Navigation */}
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="mb-0">
                {calendar.monthName} {calendar.year}
              </h5>
              <div className="d-flex gap-2">
                <Button
                  variant="outline-primary"
                  onClick={goToCurrentMonth}
                  disabled={mealsLoading}
                  size="sm"
                >
                  This Month
                </Button>
                <Button
                  variant="outline-primary"
                  onClick={goToPreviousMonth}
                  disabled={mealsLoading}
                  size="sm"
                >
                  <i className="bi bi-chevron-left"></i>
                </Button>
                <Button
                  variant="outline-primary"
                  onClick={goToNextMonth}
                  disabled={mealsLoading}
                  size="sm"
                >
                  <i className="bi bi-chevron-right"></i>
                </Button>
              </div>
            </div>
            
            {/* Calendar */}
            <div className="calendar-container">
              {/* Day headers */}
              <div className="calendar-header">
                {DAYS_OF_WEEK.map(day => (
                  <div key={day} className="calendar-day-header">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar days */}
              <div className="calendar-body">
                {calendar.weeks.map((week, weekIndex) => (
                  <div key={weekIndex} className="calendar-week">
                    {week.days.map(day => (
                      <div
                        key={`${day.year}-${day.month}-${day.day}`}
                        className={`calendar-day ${day.isCurrentMonth ? 'current-month' : 'other-month'} ${day.isToday ? 'today' : ''} ${planMealDate === formatDate(day.date) && planMealMoment ? 'selected' : ''}`}
                        onClick={() => {}}
                      >
                        {/* Day number */}
                        <div className="day-number">{day.day}</div>
                        
                        {/* Meal slots */}
                        <div className="meal-slots">
                          {/* Lunch slot */}
                          <div
                            className={`meal-slot lunch-slot ${planMealDate === formatDate(day.date) && planMealMoment === 'lunch' ? 'selected' : ''}`}
                            onClick={() => handleCalendarCellClick(day, 'lunch')}
                          >
                            {day.lunchMeal ? (
                              <span className="meal-text">
                                {truncateText(day.lunchMeal.recipe_title)}
                              </span>
                            ) : (
                              <span className="empty-slot">Lunch</span>
                            )}
                          </div>
                          
                          {/* Dinner slot */}
                          <div
                            className={`meal-slot dinner-slot ${planMealDate === formatDate(day.date) && planMealMoment === 'dinner' ? 'selected' : ''}`}
                            onClick={() => handleCalendarCellClick(day, 'dinner')}
                          >
                            {day.dinnerMeal ? (
                              <span className="meal-text">
                                {truncateText(day.dinnerMeal.recipe_title)}
                              </span>
                            ) : (
                              <span className="empty-slot">Dinner</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </div>
            
            {/* Selected meal info */}
            {planMealDate && planMealMoment && (
              <div className="mt-4 p-3 bg-light rounded">
                <p className="mb-0">
                  <strong>Selected:</strong> {formatDateForDisplay(planMealDate)} - {planMealMoment}
                </p>
              </div>
            )}
            
            {/* Actions */}
            <div className="d-flex justify-content-end gap-2 mt-4">
              <Button
                variant="secondary"
                onClick={() => setShowPlanMealModal(false)}
                disabled={mealsLoading}
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleSaveMealPlan}
                disabled={!planMealDate || !planMealMoment || mealsLoading}
              >
                <i className="bi bi-calendar-check me-2"></i>
                Save Meal Plan
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </Container>
  );
};
