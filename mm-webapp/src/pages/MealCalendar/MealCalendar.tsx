import { useState, useEffect, useCallback, useMemo } from 'react';
import { Button, Container, Spinner, Alert, Modal, Tooltip, OverlayTrigger } from 'react-bootstrap';
import { mealService } from '../../services/mealService';

import type { Meal, MealMoment, CalendarMonth, CalendarDay } from '../../types/meal.types';
import type { Recipe } from '../../types/recipe.types';
import { RecipeSelectionModal } from './components';

const DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

function getCalendarMonth(year: number, month: number, meals: Meal[]): CalendarMonth {
  const date = new Date(year, month - 1, 1);
  const firstDay = date.getDay();
  const daysInMonth = new Date(year, month, 0).getDate();
  
  const mealsMap: Record<string, Record<MealMoment, Meal>> = {};
  meals.forEach(meal => {
    const dateStr = meal.date;
    if (!mealsMap[dateStr]) {
      mealsMap[dateStr] = {} as Record<MealMoment, Meal>;
    }
    mealsMap[dateStr][meal.moment] = meal;
  });
  
  const days: CalendarDay[] = [];
  
  const daysFromPrevMonth = firstDay === 0 ? 6 : firstDay - 1;
  
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
  
  const weeks: { days: CalendarDay[] }[] = [];
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

function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function truncateText(text: string, maxLength: number = 15): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
}

export const MealCalendarPage = () => {
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [meals, setMeals] = useState<Meal[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  const [showRecipeModal, setShowRecipeModal] = useState<boolean>(false);
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);
  
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);
  const [confirmAction, setConfirmAction] = useState<() => void>(() => {});
  const [confirmMessage, setConfirmMessage] = useState<string>('');

  const fetchMeals = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;
      const response = await mealService.getMealsForMonth(year, month);
      setMeals(response.meals);
    } catch (err: any) {
      if (err.response) {
        setError('Failed to fetch meal plans. Please try again later.');
      } else if (err.request) {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to fetch meal plans. Please try again later.');
      }
      console.error('Error fetching meals:', err);
    } finally {
      setLoading(false);
    }
  }, [currentDate]);

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToCurrentMonth = () => {
    setCurrentDate(new Date());
  };

  const handleCellClick = (day: CalendarDay, moment: MealMoment) => {
    if (!day.isCurrentMonth) return;
    
    const dateStr = formatDate(day.date);
    const existingMeal = moment === 'lunch' ? day.lunchMeal : day.dinnerMeal;
    
    const mealToEdit = existingMeal || {
      id: 0,
      date: dateStr,
      moment,
      recipe_id: 0,
      recipe_title: '',
      created_at: '',
      updated_at: '',
    };
    
    setSelectedMeal(mealToEdit);
    setShowRecipeModal(true);
  };

  const handleRemoveMeal = (day: CalendarDay, moment: MealMoment, e: React.MouseEvent) => {
    e.stopPropagation();
    const meal = moment === 'lunch' ? day.lunchMeal : day.dinnerMeal;
    if (!meal) return;
    
    setConfirmMessage(`Are you sure you want to remove the ${moment} meal for ${formatDate(day.date)}?`);
    setConfirmAction(() => async () => {
      try {
        await mealService.deleteMeal(meal.id);
        fetchMeals();
      } catch (err) {
        setError('Failed to remove meal. Please try again.');
        console.error('Error removing meal:', err);
      }
    });
    setShowConfirmModal(true);
  };

  const handleSelectRecipe = async (recipe: Recipe) => {
    if (!selectedMeal) return;
    
    try {
      if (selectedMeal.id) {
        setConfirmMessage(`A meal already exists for ${selectedMeal.date} ${selectedMeal.moment}. Replace it with ${recipe.title}?`);
        setConfirmAction(() => async () => {
          try {
            await mealService.updateMeal(selectedMeal.id, { recipe_id: recipe.id });
            setShowRecipeModal(false);
            setSelectedMeal(null);
            fetchMeals();
          } catch (err) {
            setError('Failed to update meal. Please try again.');
            console.error('Error updating meal:', err);
          }
        });
        setShowConfirmModal(true);
      } else {
        await mealService.createMeal({
          date: selectedMeal.date,
          moment: selectedMeal.moment,
          recipe_id: recipe.id,
        });
        setShowRecipeModal(false);
        setSelectedMeal(null);
        fetchMeals();
      }
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError('A meal already exists for this date and time. Please select a different slot.');
      } else {
        setError('Failed to save meal. Please try again.');
      }
      console.error('Error saving meal:', err);
    }
  };

  const calendar = useMemo(() => {
    return getCalendarMonth(
      currentDate.getFullYear(),
      currentDate.getMonth() + 1,
      meals
    );
  }, [currentDate, meals]);

  useEffect(() => {
    fetchMeals();
  }, [fetchMeals]);

  if (loading && meals.length === 0) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" variant="primary" role="status" className="mb-3">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p>Loading meal calendar...</p>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      {error && (
        <Alert variant="danger" className="mb-4" dismissible onClose={() => setError(null)}>
          <strong>Error:</strong> {error}
        </Alert>
      )}

      <div className="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 gap-3">
        <div>
          <h1 className="mb-0" style={{ fontSize: '2rem', fontWeight: 700, color: '#2c3e50' }}>
            Meal Calendar
          </h1>
          <p className="text-muted mb-0">
            {calendar.monthName} {calendar.year}
          </p>
        </div>
        <div className="d-flex gap-2">
          <Button
            variant="outline-secondary"
            onClick={goToCurrentMonth}
            disabled={loading}
            className="d-flex align-items-center gap-1"
          >
            <i className="bi bi-calendar-today"></i>
            This Month
          </Button>
          <Button
            variant="outline-primary"
            onClick={goToPreviousMonth}
            disabled={loading}
            className="d-flex align-items-center gap-1"
          >
            <i className="bi bi-chevron-left"></i>
          </Button>
          <Button
            variant="outline-primary"
            onClick={goToNextMonth}
            disabled={loading}
            className="d-flex align-items-center gap-1"
          >
            <i className="bi bi-chevron-right"></i>
          </Button>
        </div>
      </div>

      <div className="calendar-container">
        <div className="calendar-header">
          {DAYS_OF_WEEK.map(day => (
            <div key={day} className="calendar-day-header">
              {day}
            </div>
          ))}
        </div>

        <div className="calendar-body">
          {calendar.weeks.map((week, weekIndex) => (
            <div key={weekIndex} className="calendar-week">
              {week.days.map(day => (
                <div
                  key={`${day.year}-${day.month}-${day.day}`}
                  className={`calendar-day ${day.isCurrentMonth ? 'current-month' : 'other-month'} ${day.isToday ? 'today' : ''}`}
                  onClick={() => {}}
                >
                  <div className="day-number">{day.day}</div>
                  
                  <div className="meal-slots">
                    <div
                      className={`meal-slot lunch-slot ${day.lunchMeal ? 'has-meal selected' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCellClick(day, 'lunch');
                      }}
                    >
                      {day.lunchMeal ? (
                        <>
                          <OverlayTrigger
                            placement="top"
                            overlay={
                              <Tooltip id={`lunch-tooltip-${day.year}-${day.month}-${day.day}`}>
                                <div>
                                  <strong>{day.lunchMeal.recipe_title}</strong>
                                </div>
                              </Tooltip>
                            }
                          >
                            <span className="meal-text">
                              {truncateText(day.lunchMeal.recipe_title)}
                            </span>
                          </OverlayTrigger>
                          <button
                            className="remove-btn"
                            onClick={(e) => handleRemoveMeal(day, 'lunch', e)}
                            title="Remove meal"
                          >
                            <i className="bi bi-x-circle-fill"></i>
                          </button>
                        </>
                      ) : (
                        <span className="empty-slot">+ Lunch</span>
                      )}
                    </div>
                    
                    <div
                      className={`meal-slot dinner-slot ${day.dinnerMeal ? 'has-meal selected' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCellClick(day, 'dinner');
                      }}
                    >
                      {day.dinnerMeal ? (
                        <>
                          <OverlayTrigger
                            placement="top"
                            overlay={
                              <Tooltip id={`dinner-tooltip-${day.year}-${day.month}-${day.day}`}>
                                <div>
                                  <strong>{day.dinnerMeal.recipe_title}</strong>
                                </div>
                              </Tooltip>
                            }
                          >
                            <span className="meal-text">
                              {truncateText(day.dinnerMeal.recipe_title)}
                            </span>
                          </OverlayTrigger>
                          <button
                            className="remove-btn"
                            onClick={(e) => handleRemoveMeal(day, 'dinner', e)}
                            title="Remove meal"
                          >
                            <i className="bi bi-x-circle-fill"></i>
                          </button>
                        </>
                      ) : (
                        <span className="empty-slot">+ Dinner</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {showRecipeModal && (
        <RecipeSelectionModal
          show={showRecipeModal}
          close={() => {
            setShowRecipeModal(false);
            setSelectedMeal(null);
          }}
          onRecipeSelected={handleSelectRecipe}
          selectedMeal={selectedMeal}
        />
      )}

      <Modal
        show={showConfirmModal}
        onHide={() => setShowConfirmModal(false)}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Confirm</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>{confirmMessage}</p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowConfirmModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={() => {
            confirmAction();
            setShowConfirmModal(false);
          }}>
            Confirm
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};
