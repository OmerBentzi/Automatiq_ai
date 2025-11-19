/**
 * Root Application Component
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * 
 * Main application component with error boundary and routing logic.
 */

import React from 'react'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ChatPage } from './pages/ChatPage'

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ChatPage />
    </ErrorBoundary>
  )
}

export default App

