/**
 * OAuth Callback Page
 * Handles the redirect from Google OAuth and stores tokens
 */

import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    const refreshToken = searchParams.get('refresh_token');
    const error = searchParams.get('error');
    const errorMessage = searchParams.get('message');

    if (error) {
      // OAuth failed
      setStatus('error');
      setMessage(errorMessage || 'Authentication failed. Please try again.');
      setTimeout(() => {
        navigate('/login');
      }, 3000);
      return;
    }

    if (accessToken) {
      // Success! Store tokens using the same keys as authService
      localStorage.setItem('access_token', accessToken);
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }

      setStatus('success');
      setMessage('Successfully logged in with Google!');
      
      // Fetch user info and store it using protocol-relative API
      api.get('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      })
        .then(res => {
          localStorage.setItem('user', JSON.stringify(res.data));
          // Redirect to home page
          setTimeout(() => {
            window.location.href = '/';  // Use full page reload to reinitialize authService
          }, 1000);
        })
        .catch(err => {
          console.error('Failed to fetch user info:', err);
          // Still redirect even if user fetch fails
          setTimeout(() => {
            window.location.href = '/';
          }, 1000);
        });
    } else {
      // Missing tokens
      setStatus('error');
      setMessage('Missing authentication tokens.');
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        {status === 'loading' && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Completing Sign In</h2>
            <p className="text-gray-600">Please wait while we log you in...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="text-center">
            <div className="rounded-full h-16 w-16 bg-green-100 mx-auto mb-4 flex items-center justify-center">
              <svg className="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Success!</h2>
            <p className="text-gray-600">{message}</p>
            <p className="text-sm text-gray-500 mt-2">Redirecting to dashboard...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="text-center">
            <div className="rounded-full h-16 w-16 bg-red-100 mx-auto mb-4 flex items-center justify-center">
              <svg className="h-10 w-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Authentication Failed</h2>
            <p className="text-gray-600">{message}</p>
            <p className="text-sm text-gray-500 mt-2">Redirecting to login...</p>
          </div>
        )}
      </div>
    </div>
  );
}

