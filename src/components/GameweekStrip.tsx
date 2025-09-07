'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface StripCard {
  id: string;
  title: string;
  fixture_id: number;
  fixture_label: string;
  home_team: string;
  away_team: string;
  score: string;
  image: string;
  match_date: string;
}

interface GameweekStripData {
  matchday: number;
  total_matches: number;
  strip_cards: StripCard[];
}

interface GameweekStripProps {
  apiBaseUrl?: string;
}

export default function GameweekStrip({ apiBaseUrl = 'http://localhost:5000' }: GameweekStripProps) {
  const router = useRouter();
  const [stripData, setStripData] = useState<GameweekStripData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStripData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${apiBaseUrl}/api/gameweek/strip`);
        const data = await response.json();
        
        if (data.success) {
          setStripData(data.data);
        } else {
          setError(data.error || 'Failed to fetch gameweek strip data');
        }
      } catch (err) {
        setError('Network error: Unable to fetch gameweek strip data');
        console.error('Error fetching gameweek strip:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStripData();
  }, [apiBaseUrl]);

  if (loading) {
    return (
      <section className="mb-16">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
          <span className="ml-3 text-gray-600">Loading latest results...</span>
        </div>
      </section>
    );
  }

  if (error || !stripData) {
    return (
      <section className="mb-16">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      </section>
    );
  }

  if (!stripData.strip_cards || stripData.strip_cards.length === 0) {
    return (
      <section className="mb-16">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Matchday {stripData?.matchday} Results
        </h2>
        <div className="text-center py-12">
          <div className="text-gray-500">
            No match reports available for the latest gameweek yet.
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="mb-16">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Matchday {stripData.matchday} Results
        </h2>
        <div className="text-sm text-gray-600">
          {stripData.total_matches} matches
        </div>
      </div>
      
      {/* Horizontal Scrolling Strip */}
      <div className="relative">
        <div className="flex overflow-x-auto pb-4 space-x-4 scrollbar-hide">
          {stripData.strip_cards.map((card) => (
            <div
              key={card.id}
              onClick={() => router.push(`/article/${card.id}`)}
              className="flex-shrink-0 w-64 h-40 relative bg-white rounded-xl shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-all hover:-translate-y-1 group border border-gray-200"
            >
              {/* Background Image */}
              <div className="absolute inset-0">
                <img
                  src={card.image}
                  alt={`${card.fixture_label} match thumbnail`}
                  className="w-full h-full object-cover transition-transform group-hover:scale-105"
                  onError={(e) => {
                    // Fallback to gradient background
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.parentElement!.className += ' bg-gradient-to-br from-green-500 via-blue-600 to-purple-600';
                  }}
                />
                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
              </div>
              
              {/* Content */}
              <div className="relative z-10 h-full flex flex-col justify-between p-4">
                {/* Score badge */}
                {card.score && (
                  <div className="self-end">
                    <span className="bg-white/20 backdrop-blur-sm text-white px-2 py-1 rounded-full text-sm font-bold">
                      {card.score}
                    </span>
                  </div>
                )}
                
                {/* Match label */}
                <div className="text-white">
                  <div className="font-bold text-lg leading-tight">
                    {card.fixture_label}
                  </div>
                  <div className="text-white/80 text-sm mt-1">
                    {new Date(card.match_date).toLocaleDateString('en-GB', {
                      day: 'numeric',
                      month: 'short'
                    })}
                  </div>
                </div>
              </div>
              
              {/* Hover effect indicator */}
              <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          ))}
        </div>
        
        {/* Scroll indicators */}
        <div className="absolute top-1/2 -translate-y-1/2 left-0 right-0 pointer-events-none">
          <div className="flex justify-between">
            <div className="w-8 h-16 bg-gradient-to-r from-gray-50 to-transparent"></div>
            <div className="w-8 h-16 bg-gradient-to-l from-gray-50 to-transparent"></div>
          </div>
        </div>
      </div>
      
      {/* View all button */}
      <div className="text-center mt-6">
        <button 
          onClick={() => router.push(`/gameweek/${stripData.matchday}`)}
          className="text-green-600 hover:text-green-700 font-medium transition-colors"
        >
          View all Matchday {stripData.matchday} reports →
        </button>
      </div>
    </section>
  );
}
