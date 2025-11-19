/**
 * Chat Page Component
 * ~~~~~~~~~~~~~~~~~~~~
 * 
 * Main chat interface for interacting with the training assistant.
 */

import React, { useEffect, useRef } from 'react'
import { Shield, LogOut, Info } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import { useChatStore } from '../store/chatStore'
import { AuthPrompt } from '../components/AuthPrompt'
import { ChatMessage } from '../components/ChatMessage'
import { ChatInput } from '../components/ChatInput'
import { LoadingSpinner } from '../components/LoadingSpinner'

/**
 * Chat page component
 */
export const ChatPage: React.FC = () => {
  const { 
    isAuthenticated, 
    isCiso, 
    employeeName, 
    initialize, 
    logout 
  } = useAuthStore()
  
  const { 
    messages, 
    isLoading, 
    sendMessage, 
    clearMessages 
  } = useChatStore()

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [isInitializing, setIsInitializing] = React.useState(true)

  /**
   * Initialize session on mount
   */
  useEffect(() => {
    const init = async () => {
      await initialize()
      setIsInitializing(false)
    }
    init()
  }, [initialize])

  /**
   * Scroll to bottom when new messages arrive
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /**
   * Handle logout
   */
  const handleLogout = () => {
    clearMessages()
    logout()
  }

  /**
   * Show loading while initializing
   */
  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <LoadingSpinner message="Initializing session..." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">
                CyberSecurity Training Assistant
              </h1>
              {isAuthenticated && (
                <p className="text-sm text-gray-600">
                  Welcome, {employeeName} {isCiso && '(CISO)'}
                </p>
              )}
            </div>
          </div>

          {isAuthenticated && (
            <button
              onClick={handleLogout}
              className="btn btn-secondary flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden flex flex-col">
        {!isAuthenticated ? (
          /* Authentication Screen */
          <div className="flex-1 flex items-center justify-center p-4">
            <AuthPrompt />
          </div>
        ) : (
          /* Chat Interface */
          <>
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto px-4 py-6">
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Welcome Message */}
                {messages.length === 0 && (
                  <div className="card">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <Info className="w-5 h-5 text-primary-600" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-2">
                          Welcome to the CyberSecurity Training Assistant!
                        </h3>
                        <p className="text-sm text-gray-600 mb-3">
                          I can help you with questions about your cybersecurity training. Here are some examples:
                        </p>
                        <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                          <li>What is my training status?</li>
                          <li>Which videos have I completed?</li>
                          <li>What videos am I missing?</li>
                          <li>How long did video 3 take me?</li>
                          {isCiso && (
                            <>
                              <li>Show me all employees who finished training</li>
                              <li>Give me global training statistics</li>
                            </>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}

                {/* Messages */}
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}

                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                      <Shield className="w-5 h-5 text-primary-600" />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Area */}
            <div className="border-t border-gray-200 bg-white p-4">
              <div className="max-w-4xl mx-auto">
                <ChatInput
                  onSend={sendMessage}
                  isLoading={isLoading}
                />
              </div>
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-3">
        <div className="max-w-5xl mx-auto px-4 text-center text-xs text-gray-500">
          CyberSecurity Training Assistant v1.0.0 | Powered by AI
        </div>
      </footer>
    </div>
  )
}

