/**
 * Authentication Store
 * ~~~~~~~~~~~~~~~~~~~~
 * 
 * Zustand store for managing authentication state.
 */

import { create } from 'zustand'
import { AuthState } from '../types'
import { ApiService } from '../services/api'

interface AuthStore extends AuthState {
  /**
   * Initialize session and load from localStorage
   */
  initialize: () => Promise<void>

  /**
   * Authenticate with employee credentials
   */
  authenticate: (employeeId?: number, employeeName?: string) => Promise<{
    success: boolean
    message: string
  }>

  /**
   * Logout and clear session
   */
  logout: () => void

  /**
   * Update session ID
   */
  setSessionId: (sessionId: string) => void
}

/**
 * Authentication store
 */
export const useAuthStore = create<AuthStore>((set, get) => ({
  // Initial state
  isAuthenticated: false,
  isCiso: false,
  sessionId: null,
  employeeId: null,
  employeeName: null,
  missingFields: [],

  /**
   * Initialize session
   */
  initialize: async () => {
    // Try to load session from localStorage
    const storedSessionId = localStorage.getItem('session_id')

    if (storedSessionId) {
      set({ sessionId: storedSessionId })
    } else {
      // Create new session
      try {
        const response = await ApiService.createSession()
        const sessionId = response.session_id
        localStorage.setItem('session_id', sessionId)
        set({ sessionId })
      } catch (error) {
        console.error('Failed to create session:', error)
      }
    }
  },

  /**
   * Authenticate user
   */
  authenticate: async (employeeId?: number, employeeName?: string) => {
    let { sessionId } = get()

    if (!sessionId) {
      return {
        success: false,
        message: 'No session available. Please refresh the page.',
      }
    }

    try {
      const response = await ApiService.authenticate(
        sessionId,
        employeeId,
        employeeName
      )

      // If session is invalid, create a new one and retry
      if (!response.success && response.message === 'Invalid session') {
        console.log('Session invalid, creating new session...')
        const newSession = await ApiService.createSession()
        sessionId = newSession.session_id
        localStorage.setItem('session_id', sessionId)
        set({ sessionId })
        
        // Retry authentication with new session
        const retryResponse = await ApiService.authenticate(
          sessionId,
          employeeId,
          employeeName
        )
        
        set({
          isAuthenticated: retryResponse.is_authenticated,
          isCiso: retryResponse.is_ciso,
          employeeId: employeeId || get().employeeId,
          employeeName: employeeName || get().employeeName,
          missingFields: retryResponse.missing_fields,
        })

        return {
          success: retryResponse.success,
          message: retryResponse.message,
        }
      }

      set({
        isAuthenticated: response.is_authenticated,
        isCiso: response.is_ciso,
        employeeId: employeeId || get().employeeId,
        employeeName: employeeName || get().employeeName,
        missingFields: response.missing_fields,
      })

      return {
        success: response.success,
        message: response.message,
      }
    } catch (error) {
      return {
        success: false,
        message: (error as Error).message,
      }
    }
  },

  /**
   * Logout
   */
  logout: () => {
    localStorage.removeItem('session_id')
    set({
      isAuthenticated: false,
      isCiso: false,
      sessionId: null,
      employeeId: null,
      employeeName: null,
      missingFields: [],
    })
  },

  /**
   * Set session ID
   */
  setSessionId: (sessionId: string) => {
    localStorage.setItem('session_id', sessionId)
    set({ sessionId })
  },
}))

