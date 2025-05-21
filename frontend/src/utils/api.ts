import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API endpoints
export const endpoints = {
  // Auth endpoints
  register: '/auth/register',
  login: '/auth/login',
  
  // Product endpoints
  products: '/products',
  product: (id: string) => `/products/${id}`,
  
  // Review endpoints
  reviews: '/comments',
  productReviews: (productId: string) => `/comments/product/${productId}`,
};

// Auth API calls
export const auth = {
  register: async (pgpKey: string, isSeller: boolean = false) => {
    const response = await api.post(endpoints.register, { pgp_key: pgpKey, is_seller: isSeller });
    return response.data;
  },

  login: async (pgpKey: string) => {
    const response = await api.post(endpoints.login, { pgp_key: pgpKey });
    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
  },
};

// Product API calls
export const products = {
  create: async (formData: FormData) => {
    const response = await api.post(endpoints.products, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (page: number = 1, limit: number = 10) => {
    const response = await api.get(endpoints.products, {
      params: { skip: (page - 1) * limit, limit },
    });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get(endpoints.product(id));
    return response.data;
  },

  delete: async (id: string) => {
    const response = await api.delete(endpoints.product(id));
    return response.data;
  },
};

// Review API calls
export const reviews = {
  create: async (productId: string, rating: number, comment: string) => {
    const response = await api.post(endpoints.reviews, {
      product_id: productId,
      rating,
      comment,
    });
    return response.data;
  },

  listForProduct: async (productId: string, page: number = 1, limit: number = 10) => {
    const response = await api.get(endpoints.productReviews(productId), {
      params: { skip: (page - 1) * limit, limit },
    });
    return response.data;
  },
};

// Error handler
export const handleApiError = (error: any) => {
  if (error.response) {
    // Server responded with error
    const message = error.response.data.detail || 'An error occurred';
    throw new Error(message);
  } else if (error.request) {
    // Request made but no response
    throw new Error('No response from server');
  } else {
    // Error setting up request
    throw new Error('Error setting up request');
  }
};

export default api;
