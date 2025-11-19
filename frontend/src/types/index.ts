/**
 * TypeScript Type Definitions
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * 
 * Centralized type definitions for the application.
 */

/**
 * Message in the chat conversation
 */
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  intent?: string
  contextData?: Record<string, any>
}

/**
 * Authentication state
 */
export interface AuthState {
  isAuthenticated: boolean
  isCiso: boolean
  sessionId: string | null
  employeeId: number | null
  employeeName: string | null
  missingFields: string[]
}

/**
 * API Response types
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

/**
 * Chat API response
 */
export interface ChatResponse {
  success: boolean
  response: string
  intent?: string
  requires_auth: boolean
  context_data?: Record<string, any>
}

/**
 * Authentication API response
 */
export interface AuthResponse {
  success: boolean
  message: string
  session_id: string
  is_authenticated: boolean
  is_ciso: boolean
  missing_fields: string[]
}

/**
 * Employee status data
 */
export interface EmployeeStatus {
  employee_id: number
  employee_name: string
  email: string
  department: string
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'FINISHED'
  completion_percentage: number
  total_time_minutes: number
  completed_videos: number[]
  missing_videos: number[]
  video_details: VideoDetail[]
  started_at?: string
  completed_at?: string
}

/**
 * Video detail information
 */
export interface VideoDetail {
  video_number: number
  video_name: string
  completed: boolean
  duration_minutes: number
}

