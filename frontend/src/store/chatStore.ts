/**
 * Chat Store
 * ~~~~~~~~~~
 * 
 * Zustand store for managing chat state and messages.
 */

import { create } from 'zustand'
import { Message } from '../types'
import { ApiService } from '../services/api'
import { useAuthStore } from './authStore'

interface ChatStore {
  messages: Message[]
  isLoading: boolean
  error: string | null

  /**
   * Add a message to the chat
   */
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void

  /**
   * Send a message to the AI
   */
  sendMessage: (content: string) => Promise<void>

  /**
   * Clear all messages
   */
  clearMessages: () => void

  /**
   * Clear error
   */
  clearError: () => void
}

/**
 * Generate unique message ID
 */
const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Chat store
 */
export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isLoading: false,
  error: null,

  /**
   * Add message
   */
  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: generateMessageId(),
      timestamp: new Date(),
    }

    set((state) => ({
      messages: [...state.messages, newMessage],
    }))
  },

  /**
   * Send message to AI
   */
  sendMessage: async (content: string) => {
    const { sessionId } = useAuthStore.getState()

    if (!sessionId) {
      set({ error: 'No session available' })
      return
    }

    // Add user message
    get().addMessage({
      role: 'user',
      content,
    })

    // Set loading state
    set({ isLoading: true, error: null })

    try {
      // Call API
      const response = await ApiService.chat(sessionId, content)

      // Add AI response
      get().addMessage({
        role: 'assistant',
        content: response.response,
        intent: response.intent,
        contextData: response.context_data,
      })

      // Handle authentication requirement
      if (response.requires_auth) {
        get().addMessage({
          role: 'system',
          content: 'Please authenticate with your employee ID and name to continue.',
        })
      }
    } catch (error) {
      const errorMessage = (error as Error).message || 'Failed to send message'
      set({ error: errorMessage })

      // Add error message
      get().addMessage({
        role: 'system',
        content: `Error: ${errorMessage}`,
      })
    } finally {
      set({ isLoading: false })
    }
  },

  /**
   * Clear messages
   */
  clearMessages: () => {
    set({ messages: [], error: null })
  },

  /**
   * Clear error
   */
  clearError: () => {
    set({ error: null })
  },
}))

