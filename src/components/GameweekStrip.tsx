'use client';

import { useState, useEffect, useRef } from 'react';
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

export default function GameweekStrip({ apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000' }: GameweekStripProps) {
  const router = useRouter();
  const [stripData, setStripData] = useState<GameweekStripData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

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

  // Check scroll state
  const checkScrollState = () => {
    if (scrollContainerRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollContainerRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  // Scroll functions
  const scrollLeft = () => {
    if (scrollContainerRef.current) {
      const cardWidth = 288 + 16; // w-72 (288px) + gap (16px)
      scrollContainerRef.current.scrollBy({
        left: -cardWidth,
        behavior: 'smooth'
      });
    }
  };

  const scrollRight = () => {
    if (scrollContainerRef.current) {
      const cardWidth = 288 + 16; // w-72 (288px) + gap (16px)
      scrollContainerRef.current.scrollBy({
        left: cardWidth,
        behavior: 'smooth'
      });
    }
  };

  // Update scroll state when strip data changes
  useEffect(() => {
    if (stripData && scrollContainerRef.current) {
      checkScrollState();
      const container = scrollContainerRef.current;
      container.addEventListener('scroll', checkScrollState);
      
      // Also check on window resize
      window.addEventListener('resize', checkScrollState);
      
      return () => {
        container.removeEventListener('scroll', checkScrollState);
        window.removeEventListener('resize', checkScrollState);
      };
    }
  }, [stripData]);

  if (loading) {
    return (
      <section className="mb-16">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          <span className="ml-3 text-gray-600">Loading latest gameweek fixtures...</span>
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
          Latest Gameweek {stripData?.matchday} Fixtures
        </h2>
        <div className="text-center py-12">
          <div className="text-gray-500">
            No fixtures available for the latest gameweek yet.
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="mb-16">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Latest Gameweek {stripData.matchday} Fixtures
          </h2>
          <p className="text-sm text-gray-500 mt-1">Scroll horizontally to see all fixtures</p>
        </div>
      </div>
      
      {/* Horizontal Scrolling Strip */}
      <div className="relative">
        {/* Left Arrow */}
        {canScrollLeft && (
          <button
            onClick={scrollLeft}
            className="absolute left-2 top-1/2 -translate-y-1/2 z-10 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full shadow-lg border border-gray-200 flex items-center justify-center hover:bg-white hover:scale-110 transition-all duration-200"
            aria-label="Scroll left"
          >
            <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}

        {/* Right Arrow */}
        {canScrollRight && (
          <button
            onClick={scrollRight}
            className="absolute right-2 top-1/2 -translate-y-1/2 z-10 w-10 h-10 bg-white/90 backdrop-blur-sm rounded-full shadow-lg border border-gray-200 flex items-center justify-center hover:bg-white hover:scale-110 transition-all duration-200"
            aria-label="Scroll right"
          >
            <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}

        <div 
          ref={scrollContainerRef}
          className="flex overflow-x-auto pb-4 space-x-4 scrollbar-hide"
        >
          {stripData.strip_cards.map((card, index) => (
          <div
            key={card.id}
            onClick={() => {
              // Navigate to fixture page to show all articles for this fixture
              if (card.fixture_id) {
                router.push(`/fixture/${card.fixture_id}`);
              } else {
                // Fallback to gameweek page if no fixture_id
                router.push(`/gameweek/${stripData.matchday}`);
              }
            }}
            className="flex-shrink-0 w-72 relative bg-white rounded-xl shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-all hover:-translate-y-1 group border border-gray-200"
          >
            {/* Image Section */}
            <div className="h-44 relative overflow-hidden">
              <img
                src={card.image}
                alt={`${card.fixture_label} match thumbnail`}
                className="w-full h-full object-cover transition-transform group-hover:scale-105"
                onError={(e) => {
                  // Fallback to gradient background
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const gradients = [
                    'from-indigo-500 via-violet-500 to-purple-600',
                    'from-blue-500 via-cyan-500 to-teal-600',
                    'from-purple-500 via-pink-500 to-rose-600',
                    'from-green-500 via-emerald-500 to-teal-600'
                  ];
                  target.parentElement!.innerHTML = `
                    <div class="w-full h-full bg-gradient-to-br ${gradients[index % 4]} flex items-center justify-center">
                      <span class="text-white text-2xl">⚽</span>
                    </div>
                  `;
                }}
              />
              {/* Score overlay */}
              {card.score && (
                <div className="absolute top-3 right-3">
                  <span className="bg-black/80 backdrop-blur-sm text-white px-2 py-1 rounded-lg text-sm font-bold">
                    {card.score}
                  </span>
                </div>
              )}
              {/* News source badge */}
              <div className="absolute bottom-3 left-3">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                    <span className="text-xs">⚽</span>
                  </div>
                  <span className="text-white text-xs font-medium bg-black/50 px-2 py-1 rounded">
                    {card.title ? 'Match Report' : 'Fixture'}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Content Section */}
            <div className="p-4">
              {/* Match Details */}
              <div className="mb-2">
                <h3 className="font-bold text-gray-900 text-base group-hover:text-indigo-600 transition-colors">
                  {card.fixture_label}
                </h3>
                {card.score && (
                  <div className="text-lg font-bold text-indigo-600 mt-1">
                    {card.score}
                  </div>
                )}
              </div>
              
              {/* Date */}
              <p className="text-xs text-gray-500">
                {new Date(card.match_date).toLocaleDateString('en-GB', {
                  weekday: 'short',
                  day: 'numeric',
                  month: 'short'
                })}
              </p>
            </div>
            
            {/* Hover effect indicator */}
            <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
          ))}
        </div>
      </div>
    </section>
  );
}
