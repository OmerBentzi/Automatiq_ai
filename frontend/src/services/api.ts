/**
 * API Service
 * ~~~~~~~~~~~
 * 
 * Centralized API communication with the backend.
 * Provides type-safe methods for all API endpoints.
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import { ChatResponse, AuthResponse, EmployeeStatus } from '../types'

/**
 * Base API configuration
 * Use /api for production (proxied by Nginx)
 * Use http://localhost:8000/api for development
 */
const API_BASE_URL = '/api'

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
})

/**
 * API error handler
 */
const handleApiError = (error: AxiosError): never => {
  if (error.response) {
    // Server responded with error
    const message = (error.response.data as any)?.message || error.message
    throw new Error(message)
  } else if (error.request) {
    // Request made but no response
    throw new Error('No response from server. Please check your connection.')
  } else {
    // Request setup error
    throw new Error(error.message)
  }
}

/**
 * API Service class
 */
export class ApiService {
  /**
   * Create a new session
   */
  static async createSession(): Promise<{ session_id: string; message: string }> {
    try {
      const response = await apiClient.post('/session/create')
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Authenticate user with employee credentials
   */
  static async authenticate(
    sessionId: string,
    employeeId?: number,
    employeeName?: string
  ): Promise<AuthResponse> {
    try {
      const response = await apiClient.post('/authenticate', {
        session_id: sessionId,
        employee_id: employeeId,
        employee_name: employeeName,
      })
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Send a chat message and get AI response
   */
  static async chat(sessionId: string, query: string): Promise<ChatResponse> {
    try {
      const response = await apiClient.post('/chat', {
        session_id: sessionId,
        query: query,
      })
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Get employee training status
   */
  static async getEmployeeStatus(
    sessionId: string,
    employeeId?: number
  ): Promise<{ success: boolean; data?: EmployeeStatus; error?: string }> {
    try {
      const response = await apiClient.post('/status/employee', {
        session_id: sessionId,
        employee_id: employeeId,
      })
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Get global training statistics (CISO only)
   */
  static async getGlobalStatus(
    sessionId: string,
    statusFilter?: string
  ): Promise<{ success: boolean; data?: any; error?: string }> {
    try {
      const response = await apiClient.post('/status/all', {
        session_id: sessionId,
        status_filter: statusFilter,
      })
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }

  /**
   * Check API health
   */
  static async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    try {
      const response = await apiClient.get('/health')
      return response.data
    } catch (error) {
      return handleApiError(error as AxiosError)
    }
  }
}

export default ApiService

