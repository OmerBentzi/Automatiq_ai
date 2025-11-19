/**
 * Chat Input Component
 * ~~~~~~~~~~~~~~~~~~~~~
 * 
 * Input field for sending chat messages.
 */

import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  isLoading: boolean
  disabled?: boolean
}

/**
 * Chat input component
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSend, isLoading, disabled = false }) => {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  /**
   * Auto-resize textarea based on content
   */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!message.trim() || isLoading || disabled) {
      return
    }

    onSend(message.trim())
    setMessage('')
  }

  /**
   * Handle Enter key (submit on Enter, new line on Shift+Enter)
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2">
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about training status, videos, or progress..."
          className="input resize-none min-h-[48px] max-h-[200px] pr-12"
          rows={1}
          disabled={isLoading || disabled}
        />
        
        {/* Character count */}
        {message.length > 800 && (
          <span className={`absolute bottom-2 right-12 text-xs ${
            message.length > 1000 ? 'text-red-500' : 'text-gray-400'
          }`}>
            {message.length}/1000
          </span>
        )}
      </div>

      <button
        type="submit"
        disabled={!message.trim() || isLoading || disabled || message.length > 1000}
        className="btn btn-primary flex items-center gap-2 flex-shrink-0"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="hidden sm:inline">Sending...</span>
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">Send</span>
          </>
        )}
      </button>
    </form>
  )
}

