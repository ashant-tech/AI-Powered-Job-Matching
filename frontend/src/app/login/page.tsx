'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('reset') === 'success') {
      setNotice('Your password has been reset. You can now sign in.');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 502/503/504 usually mean the backend free instance is cold-starting;
      // retry once after a short pause instead of showing a hard error.
      const COLD_START = new Set([502, 503, 504]);
      let response: Response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
        }),
      });
      if (COLD_START.has(response.status)) {
        setError('Server is starting up, retrying…');
        await new Promise((r) => setTimeout(r, 3000));
        response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: formData.email,
            password: formData.password,
          }),
        });
        setError('');
      }

      const responseBody = await response.text();
      let data: Record<string, unknown> = {};
      try {
        const parsedBody: unknown = JSON.parse(responseBody);
        if (typeof parsedBody === 'object' && parsedBody !== null) {
          data = parsedBody as Record<string, unknown>;
        }
      } catch {
        // Non-JSON body (gateway/proxy error page) — mapped to a clear message below.
      }

      if (!response.ok) {
        let message: string;
        if (response.status === 401) {
          message = 'Invalid email or password';
        } else if (response.status === 429) {
          const retryAfter = Number(response.headers.get('Retry-After'));
          message = Number.isFinite(retryAfter) && retryAfter > 0
            ? `Too many login attempts. Please try again in ${retryAfter} seconds.`
            : 'Too many login attempts. Please wait a minute and try again.';
        } else if (COLD_START.has(response.status)) {
          message = 'The server is still starting up. Please wait a few seconds and try again.';
        } else if (typeof data.detail === 'string') {
          message = data.detail;
        } else {
          message = 'Login service is unavailable right now. Please try again in a moment.';
        }
        throw new Error(message);
      }

      if (typeof data.access_token !== 'string') {
        throw new Error('Login response did not include an access token');
      }

      localStorage.setItem('token', data.access_token);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
          <p className="text-gray-600 mt-2">Sign in to your account</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {notice && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
            {notice}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>

          <div className="text-right">
            <Link href="/forgot-password" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
              Forgot password?
            </Link>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link href="/register" className="text-indigo-600 hover:text-indigo-700 font-semibold">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
