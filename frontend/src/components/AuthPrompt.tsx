/**
 * Authentication Prompt Component
 * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 * 
 * Prompts user for employee ID and name for authentication.
 */

import React, { useState } from 'react'
import { Shield, Loader2 } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

/**
 * Authentication prompt component
 */
export const AuthPrompt: React.FC = () => {
  const { authenticate, missingFields } = useAuthStore()
  const [employeeId, setEmployeeId] = useState('')
  const [employeeName, setEmployeeName] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setMessage('')

    try {
      const result = await authenticate(
        employeeId ? parseInt(employeeId) : undefined,
        employeeName || undefined
      )

      setMessage(result.message)

      if (!result.success) {
        // Show error message briefly
        setTimeout(() => setMessage(''), 3000)
      }
    } catch (error) {
      setMessage((error as Error).message)
      setTimeout(() => setMessage(''), 3000)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="card max-w-md mx-auto animate-slide-up">
      <div className="flex items-center justify-center w-16 h-16 mx-auto bg-primary-100 rounded-full">
        <Shield className="w-8 h-8 text-primary-600" />
      </div>

      <h2 className="mt-4 text-2xl font-bold text-center text-gray-900">
        Authentication Required
      </h2>

      <p className="mt-2 text-center text-gray-600">
        Please provide your credentials to access the training assistant
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="employeeId" className="block text-sm font-medium text-gray-700 mb-1">
            Employee ID
          </label>
          <input
            type="number"
            id="employeeId"
            value={employeeId}
            onChange={(e) => setEmployeeId(e.target.value)}
            className="input"
            placeholder="Enter your employee ID"
            required={missingFields.includes('employee_id')}
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="employeeName" className="block text-sm font-medium text-gray-700 mb-1">
            Full Name
          </label>
          <input
            type="text"
            id="employeeName"
            value={employeeName}
            onChange={(e) => setEmployeeName(e.target.value)}
            className="input"
            placeholder="Enter your full name"
            required={missingFields.includes('employee_name')}
            disabled={isLoading}
          />
        </div>

        {message && (
          <div className={`p-3 rounded-lg text-sm ${
            message.includes('success') 
              ? 'bg-green-50 text-green-800' 
              : 'bg-red-50 text-red-800'
          }`}>
            {message}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || (!employeeId && !employeeName)}
          className="w-full btn btn-primary flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Authenticating...
            </>
          ) : (
            'Authenticate'
          )}
        </button>
      </form>

      <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
        <p className="font-medium mb-1">💡 Tip:</p>
        <p>Login with any employee from the database. Employee ID 123456789 has CISO privileges.</p>
      </div>
    </div>
  )
}

