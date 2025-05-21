import { AxiosRequestConfig } from 'axios';

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

// Auth Types
export interface UserCreate {
  pgp_key: string;
  is_seller: boolean;
}

export interface User {
  id: string;
  is_seller: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Product Types
export interface ProductCreate {
  name: string;
  description: string;
  price: number;
  category?: string;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category?: string;
  image_path?: string;
  commission: number;
  seller_id: string;
  created_at: string;
}

// Review Types
export interface ReviewCreate {
  product_id: string;
  rating: number;
  comment: string;
}

export interface Review {
  id: string;
  product_id: string;
  user_id: string;
  rating: number;
  comment: string;
  created_at: string;
}

// API Config Types
export interface ApiConfig extends AxiosRequestConfig {
  headers: {
    Authorization?: string;
    'Content-Type': string;
  };
}

// Pagination Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// Error Types
export interface ApiError {
  status: number;
  message: string;
  details?: any;
}
