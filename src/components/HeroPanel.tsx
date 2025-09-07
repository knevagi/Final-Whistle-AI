'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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
        <div className="bg-gradient-to-br from-green-500 via-blue-600 to-purple-600 rounded-3xl p-8 md:p-12 text-white overflow-hidden min-h-[400px] flex items-center justify-center shadow-lg">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <span className="ml-3 text-white">Loading featured article...</span>
        </div>
      </section>
    );
  }

  if (error || !featuredArticle) {
    return (
      <section className="mb-16">
        <div className="bg-gradient-to-br from-green-500 via-blue-600 to-purple-600 rounded-3xl p-8 md:p-12 text-white overflow-hidden min-h-[400px] flex items-center justify-center shadow-lg">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Final Whistle AI
              <span className="block text-yellow-300">Football Focus</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl opacity-90">
              Get the latest Premier League news, in-depth match analysis, player insights, and expert commentary from the beautiful game.
            </p>
            <button className="bg-white text-green-600 px-8 py-4 rounded-xl font-semibold text-lg hover:bg-gray-100 transition-colors shadow-lg">
              Explore Latest Articles
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="mb-16">
      <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-200">
        <div className="grid lg:grid-cols-2 gap-0">
          {/* Article Content */}
          <div className="p-8 md:p-12 flex flex-col justify-center order-2 lg:order-1">
            <div className="mb-4">
              <span className="inline-block bg-green-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-4">
                Featured Article
              </span>
              <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                <span>{featuredArticle.author}</span>
                <span>•</span>
                <span>{new Date(featuredArticle.created_at).toLocaleDateString()}</span>
                <span>•</span>
                <span>{featuredArticle.readTime}</span>
              </div>
            </div>
            
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-6 leading-tight">
              {featuredArticle.title}
            </h1>
            
            <p className="text-lg md:text-xl text-gray-600 mb-8 leading-relaxed">
              {featuredArticle.excerpt}
            </p>
            
            {/* Match Info */}
            <div className="flex items-center space-x-4 mb-6 p-4 bg-gray-50 rounded-xl border border-gray-200">
              <div className="text-center">
                <div className="text-sm text-gray-600">Match</div>
                <div className="font-bold text-gray-900">{featuredArticle.fixture_match}</div>
              </div>
              {featuredArticle.score && (
                <>
                  <div className="w-px h-8 bg-gray-300"></div>
                  <div className="text-center">
                    <div className="text-sm text-gray-600">Score</div>
                    <div className="font-bold text-green-600 text-lg">{featuredArticle.score}</div>
                  </div>
                </>
              )}
            </div>
            
            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-8">
              {featuredArticle.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm border border-gray-300"
                >
                  {tag}
                </span>
              ))}
            </div>
            
            <button 
              onClick={() => router.push(`/article/${featuredArticle.id}`)}
              className="bg-green-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-green-700 transition-colors self-start shadow-lg"
            >
              Read Full Article →
            </button>
          </div>
          
          {/* Featured Image */}
          <div className="relative h-64 lg:h-full min-h-[400px] order-1 lg:order-2">
            {/* Get or generate image for the featured article */}
            <div className="absolute inset-0">
              {featuredArticle.image && featuredArticle.image !== '/api/placeholder/400/250' ? (
                <>
                  <img
                    src={featuredArticle.image}
                    alt={`${featuredArticle.fixture_match} match thumbnail`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      // Hide the failed image
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      // Show the fallback by setting the parent's innerHTML
                      const parent = target.parentElement!;
                      parent.innerHTML = `
                        <div class="absolute inset-0 bg-gradient-to-br from-green-500 via-blue-600 to-purple-600 flex items-center justify-center">
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
                  
                  {/* Overlay gradient for better text readability */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent"></div>
                  
                  {/* Match info overlay */}
                  <div className="absolute bottom-6 left-6 right-6">
                    <div className="text-white">
                      <div className="text-lg font-medium mb-1">{featuredArticle.fixture_match}</div>
                      {featuredArticle.score && (
                        <div className="text-2xl font-bold">{featuredArticle.score}</div>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                // Fallback gradient design
                <div className="absolute inset-0 bg-gradient-to-br from-green-500 via-blue-600 to-purple-600 flex items-center justify-center">
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
            </div>
            
            {/* Category badge */}
            <div className="absolute top-6 left-6">
              <span className="bg-white/20 backdrop-blur-sm text-white px-3 py-1 rounded-full text-sm font-medium">
                {featuredArticle.category}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
