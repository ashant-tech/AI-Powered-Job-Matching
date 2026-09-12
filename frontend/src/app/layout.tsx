import './globals.css'

export const metadata = {
  title: 'AI Job Matching System',
  description: 'AI-powered job matching platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
