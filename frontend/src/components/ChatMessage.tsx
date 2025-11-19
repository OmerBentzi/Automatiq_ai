/**
 * Chat Message Component
 * ~~~~~~~~~~~~~~~~~~~~~~~
 * 
 * Displays a single chat message with appropriate styling.
 */

import React from 'react'
import { User, Bot, AlertCircle } from 'lucide-react'
import { Message } from '../types'
import ReactMarkdown from 'react-markdown'

interface ChatMessageProps {
  message: Message
}

/**
 * Chat message component
 */
export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  /**
   * Get icon based on message role
   */
  const getIcon = () => {
    switch (message.role) {
      case 'user':
        return <User className="w-5 h-5" />
      case 'assistant':
        return <Bot className="w-5 h-5" />
      case 'system':
        return <AlertCircle className="w-5 h-5" />
      default:
        return null
    }
  }

  /**
   * Get styling based on message role
   */
  const getMessageClass = () => {
    switch (message.role) {
      case 'user':
        return 'bg-primary-600 text-white ml-auto'
      case 'assistant':
        return 'bg-white border border-gray-200 text-gray-900'
      case 'system':
        return 'bg-yellow-50 border border-yellow-200 text-yellow-900'
      default:
        return 'bg-gray-100'
    }
  }

  const iconBgClass = () => {
    switch (message.role) {
      case 'user':
        return 'bg-primary-700'
      case 'assistant':
        return 'bg-primary-100 text-primary-600'
      case 'system':
        return 'bg-yellow-100 text-yellow-600'
      default:
        return 'bg-gray-200'
    }
  }

  return (
    <div className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
      {/* Icon */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${iconBgClass()}`}>
        {getIcon()}
      </div>

      {/* Message Content */}
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${getMessageClass()} animate-slide-up`}>
        {message.role === 'assistant' ? (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        )}

        {/* Timestamp */}
        <p className={`text-xs mt-2 ${
          message.role === 'user' ? 'text-primary-100' : 'text-gray-500'
        }`}>
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  )
}

