'use client';

import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation'; // Correct import for App Router

export default function ClientNav() {
  const { isAuthenticated, user, logout, isLoading } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    // router.push('/login'); // AuthContext's logout already handles redirection
  };

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-6 py-3 flex justify-between items-center">
        <Link href="/" className="text-xl font-semibold text-gray-700">
          Analytics Dashboard
        </Link>
        <div className="flex items-center space-x-4">
          <Link href="/" className="px-3 py-2 text-gray-700 hover:text-indigo-600">
            Home
          </Link>
          {isAuthenticated && (
            <Link href="/dashboard" className="px-3 py-2 text-gray-700 hover:text-indigo-600">
              Dashboard
            </Link>
          )}
          {isLoading ? (
            <span className="px-3 py-2 text-gray-500">Loading...</span>
          ) : isAuthenticated ? (
            <>
              <span className="text-gray-700">Welcome, {user?.username || 'User'}</span>
              <button
                onClick={handleLogout}
                className="px-3 py-2 text-gray-700 hover:text-indigo-600"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="px-3 py-2 text-gray-700 hover:text-indigo-600">
                Login
              </Link>
              <Link href="/register" className="px-3 py-2 text-gray-700 bg-indigo-600 hover:bg-indigo-700 text-white rounded">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
