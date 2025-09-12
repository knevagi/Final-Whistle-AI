'use client';

import { useParams } from 'next/navigation';
import GameweekReports from '../../../components/GameweekReports';
import Link from 'next/link';

export default function GameweekPage() {
  const params = useParams();
  const matchday = params.matchday as string;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">⚽</span>
              </div>
              <span className="text-xl font-bold text-gray-900">
                Final Whistle AI
              </span>
            </Link>

            {/* Navigation */}
            <div className="flex items-center space-x-4">
              <Link 
                href="/"
                className="text-gray-700 hover:text-green-600 transition-colors"
              >
                ← Back to Home
              </Link>
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Matchday {matchday} Reports
          </h1>
          <p className="text-gray-600 text-lg">
            Complete coverage of all matches from Matchday {matchday}
          </p>
        </div>

        {/* Gameweek Reports */}
        <GameweekReports 
          apiBaseUrl={process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'} 
          specificMatchday={parseInt(matchday)}
        />
      </main>
    </div>
  );
}
