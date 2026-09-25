/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendProtocol = process.env.BACKEND_PROTOCOL || 'http'
    const backendHost = process.env.BACKEND_HOST || 'localhost:8000'

    return [
      {
        source: '/api/:path*',
        destination: `${backendProtocol}://${backendHost}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
