'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import TrendingArticles from './TrendingArticles';

interface FeaturedArticle {
  id: string;
  title: string;
  excerpt: string;
  category: string;
  word_count: number;
  created_at: string;
  fixture_match: string;
  match_date: string;
  home_team: string;
  away_team: string;
  score: string;
  competition: string;
  tags: string[];
  author: string;
  readTime: string;
  featured: boolean;
  image: string;
}

interface HeroPanelProps {
  apiBaseUrl?: string;
}

export default function HeroPanel({ apiBaseUrl = 'http://localhost:5000' }: HeroPanelProps) {
  const router = useRouter();
  const [featuredArticle, setFeaturedArticle] = useState<FeaturedArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFeaturedArticle = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(`${apiBaseUrl}/api/featured`);
        const data = await response.json();
        
        if (data.success) {
          setFeaturedArticle(data.data);
        } else {
          setError(data.error || 'Failed to fetch featured article');
        }
      } catch (err) {
        setError('Network error: Unable to fetch featured article');
        console.error('Error fetching featured article:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFeaturedArticle();
  }, [apiBaseUrl]);

  if (loading) {
    return (
      <section className="mb-16">
        <div className="grid lg:grid-cols-10 gap-8">
          <div className="lg:col-span-7">
            <div className="relative bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 rounded-3xl overflow-hidden h-[600px] flex items-center justify-center shadow-2xl">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
              <span className="ml-3 text-white">Loading featured article...</span>
            </div>
          </div>
          <div className="lg:col-span-3">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-slate-200/50 h-[600px] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-8">Trending Now</h2>
              <TrendingArticles apiBaseUrl={apiBaseUrl} />
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (error || !featuredArticle) {
    return (
      <section className="mb-16">
        <div className="grid lg:grid-cols-10 gap-8">
          <div className="lg:col-span-7">
            <div className="relative bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 rounded-3xl overflow-hidden h-[600px] flex items-center justify-center shadow-2xl">
              <div className="text-center p-8">
                <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight text-white">
                  Final Whistle AI
                  <span className="block text-yellow-200">Football Focus</span>
                </h1>
                <p className="text-xl md:text-2xl mb-8 max-w-3xl opacity-90 text-white">
                  Get the latest Premier League news, in-depth match analysis, player insights, and expert commentary from the beautiful game.
                </p>
                <button className="bg-white/95 text-indigo-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white hover:scale-105 transition-all duration-200 shadow-lg backdrop-blur-sm">
                  Explore Latest Articles
                </button>
              </div>
            </div>
          </div>
          <div className="lg:col-span-3">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-slate-200/50 h-[600px] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-8">Trending Now</h2>
              <TrendingArticles apiBaseUrl={apiBaseUrl} />
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="mb-16">
      <div className="grid lg:grid-cols-10 gap-8">
        {/* Featured Article - 70% */}
        <div className="lg:col-span-7">
          <div 
            className="relative bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200/50 cursor-pointer group h-[600px]"
            onClick={() => router.push(`/article/${featuredArticle.id}`)}
          >
            {/* Background Image */}
            <div className="absolute inset-0">
              {featuredArticle.image && featuredArticle.image !== '/api/placeholder/400/250' ? (
                <img
                  src={featuredArticle.image}
                  alt={`${featuredArticle.fixture_match} match thumbnail`}
                  className="w-full h-full object-cover transition-transform group-hover:scale-105"
                  onError={(e) => {
                    // Hide the failed image
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    // Show the fallback by setting the parent's innerHTML
                    const parent = target.parentElement!;
                    parent.innerHTML = `
                      <div class="absolute inset-0 bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center">
                        <div class="text-white text-center">
                          <div class="text-6xl mb-4">⚽</div>
                          <div class="text-lg font-medium">${featuredArticle.fixture_match}</div>
                          ${featuredArticle.score ? `<div class="text-2xl font-bold mt-2">${featuredArticle.score}</div>` : ''}
                        </div>
                        <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                        <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-12 -translate-x-12"></div>
                      </div>
                    `;
                  }}
                />
              ) : (
                // Fallback gradient design
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center">
                  <div className="text-white text-center">
                    <div className="text-6xl mb-4">⚽</div>
                    <div className="text-lg font-medium">{featuredArticle.fixture_match}</div>
                    {featuredArticle.score && (
                      <div className="text-2xl font-bold mt-2">{featuredArticle.score}</div>
                    )}
                  </div>
                  
                  {/* Decorative elements */}
                  <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                  <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-12 -translate-x-12"></div>
                </div>
              )}
              
              {/* Dark overlay for text readability */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/20"></div>
            </div>

            {/* Content Overlay */}
            <div className="absolute inset-0 flex flex-col justify-between p-8">
              {/* Top Section - Category & News Source */}
              <div className="flex items-start justify-between">
                <span className="bg-gradient-to-r from-indigo-600 to-violet-600 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
                  {featuredArticle.category}
                </span>
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                    <span className="text-xs">⚽</span>
                  </div>
                  <span className="text-white text-xs font-medium bg-black/50 px-2 py-1 rounded">
                    Final Whistle AI
                  </span>
                </div>
              </div>

              {/* Bottom Section - Title and Meta Info */}
              <div className="space-y-4">
                {/* Match Score */}
                {featuredArticle.score && (
                  <div className="flex items-center space-x-3">
                    <span className="bg-black/80 backdrop-blur-sm text-white px-3 py-1 rounded-lg text-sm font-bold">
                      {featuredArticle.score}
                    </span>
                    <span className="text-white/80 text-sm">
                      {featuredArticle.fixture_match}
                    </span>
                  </div>
                )}

                {/* Article Title */}
                <h1 className="text-white text-3xl md:text-4xl lg:text-5xl font-bold leading-tight line-clamp-3 group-hover:text-yellow-200 transition-colors">
                  {featuredArticle.title}
                </h1>

                {/* Author and Date */}
                <div className="flex items-center space-x-4 text-base text-white/80">
                  <span>{featuredArticle.author}</span>
                  <span>•</span>
                  <span>{new Date(featuredArticle.created_at).toLocaleDateString()}</span>
                  <span>•</span>
                  <span>{featuredArticle.readTime}</span>
                </div>
              </div>
            </div>

            {/* Featured Article Badge */}
            <div className="absolute top-6 left-6">
              <span className="bg-yellow-500 text-black px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">
                Featured
              </span>
            </div>
          </div>
        </div>
        
        {/* Trending Articles - 30% */}
        <div className="lg:col-span-3">
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-slate-200/50 h-[600px] overflow-y-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-8">Trending Now</h2>
            <TrendingArticles apiBaseUrl={apiBaseUrl} />
          </div>
        </div>
      </div>
    </section>
  );
}
