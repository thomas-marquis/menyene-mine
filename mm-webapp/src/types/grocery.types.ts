export interface GroceryItem {
  id: number;
  name: string;
  quantity: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface GroceryItemListResponse {
  grocery_items: GroceryItem[];
  total: number;
  skip: number;
  limit: number;
}

export interface GroceryItemCreate {
  name: string;
  quantity?: string | null;
  is_completed?: boolean;
}

export interface GroceryItemUpdate {
  name: string;
  quantity?: string | null;
  is_completed?: boolean;
}
