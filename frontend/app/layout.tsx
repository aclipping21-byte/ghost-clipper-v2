import './globals.css'

export const metadata = {
  title: 'Ghost Clipper V2',
  description: 'AI-powered short-form video clipping',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-900 text-slate-50">
        {children}
      </body>
    </html>
  )
}
