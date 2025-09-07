'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface MatchReport {
  id: string;
  title: string;
  excerpt: string;
  category: string;
  word_count: number;
  created_at: string;
  fixture_id: number;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  match_date: string;
  match_time: string;
  competition: string;
  venue: string;
  matchday: number;
  fixture_match: string;
  score_display: string;
  result: 'W' | 'L' | 'D';
  tags: string[];
  author: string;
  readTime: string;
  image: string;
}

interface GameweekData {
  matchday: number;
  match_reports: MatchReport[];
  summary: {
    total_matches: number;
    total_goals: number;
    avg_goals_per_match: number;
    gameweek_complete: boolean;
  };
}

interface GameweekReportsProps {
  apiBaseUrl?: string;
  specificMatchday?: number;
}

export default function GameweekReports({ apiBaseUrl = 'http://localhost:5000', specificMatchday }: GameweekReportsProps) {
  const router = useRouter();
  const [gameweekData, setGameweekData] = useState<GameweekData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMatchday, setSelectedMatchday] = useState<number | null>(null);

  const fetchLatestGameweek = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiBaseUrl}/api/gameweek/latest`);
      const data = await response.json();
      
      if (data.success) {
        setGameweekData(data.data);
        setSelectedMatchday(data.data.matchday);
      } else {
        setError(data.error || 'Failed to fetch gameweek data');
      }
    } catch (err) {
      setError('Network error: Unable to fetch gameweek data');
      console.error('Error fetching latest gameweek:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSpecificGameweek = async (matchday: number) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiBaseUrl}/api/gameweek/${matchday}`);
      const data = await response.json();
      
      if (data.success) {
        setGameweekData(data.data);
        setSelectedMatchday(matchday);
      } else {
        setError(data.error || `Failed to fetch gameweek ${matchday} data`);
      }
    } catch (err) {
      setError('Network error: Unable to fetch gameweek data');
      console.error(`Error fetching gameweek ${matchday}:`, err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (specificMatchday) {
      fetchSpecificGameweek(specificMatchday);
    } else {
      fetchLatestGameweek();
    }
  }, [specificMatchday]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short'
    });
  };

  const getResultColor = (result: string) => {
    switch (result) {
      case 'W': return 'text-green-600 bg-green-100';
      case 'L': return 'text-red-600 bg-red-100';
      case 'D': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <section className="mb-16">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          <span className="ml-3 text-gray-600">Loading latest gameweek...</span>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="mb-16">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-red-700">{error}</span>
          </div>
          <button
            onClick={fetchLatestGameweek}
            className="mt-3 text-red-600 hover:text-red-700 font-medium text-sm"
          >
            Try Again →
          </button>
        </div>
      </section>
    );
  }

  if (!gameweekData) {
    return null;
  }

  return (
    <section className="mb-16">
      {/* Gameweek Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">
            Matchday {gameweekData.matchday} Match Reports
          </h2>
          <div className="flex items-center space-x-6 mt-2 text-sm text-gray-600">
            <span>{gameweekData.summary.total_matches} matches</span>
            <span>•</span>
            <span>{gameweekData.summary.total_goals} goals</span>
            <span>•</span>
            <span>{gameweekData.summary.avg_goals_per_match} avg goals/match</span>
            <span>•</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              gameweekData.summary.gameweek_complete 
                ? 'bg-green-100 text-green-700'
                : 'bg-yellow-100 text-yellow-700'
            }`}>
              {gameweekData.summary.gameweek_complete ? 'Complete' : 'In Progress'}
            </span>
          </div>
        </div>
        
        {/* Gameweek Selector */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => selectedMatchday && selectedMatchday > 1 && fetchSpecificGameweek(selectedMatchday - 1)}
            disabled={!selectedMatchday || selectedMatchday <= 1}
            className="p-2 text-gray-500 hover:text-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <span className="px-3 py-1 bg-gray-100 rounded-lg text-sm font-medium border border-gray-300">
            GW {selectedMatchday}
          </span>
          <button
            onClick={() => selectedMatchday && selectedMatchday < 38 && fetchSpecificGameweek(selectedMatchday + 1)}
            disabled={!selectedMatchday || selectedMatchday >= 38}
            className="p-2 text-gray-500 hover:text-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button
            onClick={fetchLatestGameweek}
            className="ml-3 px-3 py-1 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
          >
            Latest
          </button>
        </div>
      </div>

      {/* Match Reports Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {gameweekData.match_reports.map((report) => (
          <article key={report.id} className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-all hover:-translate-y-1 border border-gray-200">
            {/* Thumbnail Image */}
            <div className="relative h-48 w-full overflow-hidden">
              <img
                src={report.image}
                alt={`${report.home_team} vs ${report.away_team} match thumbnail`}
                className="w-full h-full object-cover transition-transform hover:scale-105"
                onError={(e) => {
                  // Fallback to a placeholder if image fails to load
                  const target = e.target as HTMLImageElement;
                  console.log(`Image failed to load for article ${report.id}:`, report.image);
                  
                  // Try multiple fallback options
                  if (target.src.includes('supabase')) {
                    // If it's a Supabase URL, try constructing a different format
                    const articleId = report.id;
                    const fallbackUrl = `https://via.placeholder.com/400x250/1e40af/ffffff?text=${encodeURIComponent(report.fixture_match)}`;
                    target.src = fallbackUrl;
                  } else {
                    // Use a generic football placeholder
                    target.src = `https://via.placeholder.com/400x250/1e40af/ffffff?text=${encodeURIComponent(report.fixture_match)}`;
                  }
                }}
              />
              {/* Overlay with match info */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent">
                <div className="absolute bottom-4 left-4 right-4">
                  <div className="text-white text-sm font-medium mb-1">
                    {report.home_team} vs {report.away_team}
                  </div>
                  <div className="text-white text-lg font-bold">
                    {report.score_display}
                  </div>
                </div>
              </div>
            </div>

            {/* Match Header */}
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                  {report.competition}
                </span>
                <span className="text-xs text-gray-500">
                  {formatDate(report.match_date)}
                </span>
              </div>
              
              {/* Match Result Badge */}
              <div className="flex justify-center">
                <span className={`text-xs px-3 py-1 rounded-full font-medium ${getResultColor(report.result)}`}>
                  {report.result === 'W' ? 'HOME WIN' : report.result === 'L' ? 'AWAY WIN' : 'DRAW'}
                </span>
              </div>
            </div>

            {/* Article Content */}
            <div className="p-4">
              <h3 className="text-lg font-bold text-gray-900 mb-2 leading-tight line-clamp-2">
                {report.title}
              </h3>
              <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                {report.excerpt}
              </p>
              
              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {report.tags.slice(0, 3).map((tag, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs border border-gray-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Footer */}
              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>{report.author}</span>
                <span>{report.readTime}</span>
              </div>
              
              <button 
                onClick={() => router.push(`/article/${report.id}`)}
                className="w-full mt-3 bg-green-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-green-700 transition-colors text-sm"
              >
                Read Full Report
              </button>
            </div>
          </article>
        ))}
      </div>

      {/* Empty State */}
      {gameweekData.match_reports.length === 0 && (
        <div className="text-center py-12">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Match Reports Yet
          </h3>
          <p className="text-gray-600">
            Match reports for Matchday {gameweekData.matchday} will appear here once matches are completed and analyzed.
          </p>
        </div>
      )}
    </section>
  );
}
