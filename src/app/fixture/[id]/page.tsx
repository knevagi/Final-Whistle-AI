'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

interface Article {
  id: string;
  title: string;
  content: string;
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
  image?: string;
}

interface FixtureInfo {
  fixture_id: string;
  home_team: string;
  away_team: string;
  match_date: string;
  match_time?: string;
  home_score?: number;
  away_score?: number;
  competition: string;
  venue?: string;
  matchday?: number;
}

export default function FixturePage() {
  const params = useParams();
  const router = useRouter();
  const [articles, setArticles] = useState<Article[]>([]);
  const [fixtureInfo, setFixtureInfo] = useState<FixtureInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFixtureArticles = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const fixtureId = params.id;
        
        // Fetch all articles for this fixture using the fixture_id parameter
        const response = await fetch(`http://localhost:5000/api/articles?fixture_id=${fixtureId}&limit=50&offset=0`);
        const data = await response.json();
        
        if (data.success) {
          const fixtureArticles = data.data;
          
          if (fixtureArticles.length > 0) {
            setArticles(fixtureArticles);
            // Use the first article to get fixture info
            const firstArticle = fixtureArticles[0];
            setFixtureInfo({
              fixture_id: fixtureId as string,
              home_team: firstArticle.home_team,
              away_team: firstArticle.away_team,
              match_date: firstArticle.match_date,
              competition: firstArticle.competition,
              home_score: firstArticle.score ? parseInt(firstArticle.score.split('-')[0]) : undefined,
              away_score: firstArticle.score ? parseInt(firstArticle.score.split('-')[1]) : undefined,
              matchday: 1 // We'll enhance this later
            });
          } else {
            setError('No articles found for this fixture');
          }
        } else {
          setError(data.error || 'Failed to fetch articles');
        }
      } catch (err) {
        setError('Network error: Unable to fetch articles');
        console.error('Error fetching fixture articles:', err);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchFixtureArticles();
    }
  }, [params.id]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      'match_report': 'bg-green-500',
      'player_focus': 'bg-blue-500', 
      'tactical_analysis': 'bg-purple-500',
      'transfer_news': 'bg-orange-500',
      'weekly_roundup': 'bg-red-500'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-500';
  };

  const getCategoryName = (category: string) => {
    const names = {
      'match_report': 'Match Report',
      'player_focus': 'Player Focus', 
      'tactical_analysis': 'Tactical Analysis',
      'transfer_news': 'Transfer News',
      'weekly_roundup': 'Weekly Roundup'
    };
    return names[category as keyof typeof names] || category.replace('_', ' ');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-700 to-violet-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Back Button Skeleton */}
          <div className="mb-8">
            <div className="w-40 h-10 bg-white/20 rounded-lg animate-pulse"></div>
          </div>
          
          {/* Header Skeleton */}
          <div className="mb-12">
            <div className="h-8 bg-white/20 rounded w-3/4 mb-4 animate-pulse"></div>
            <div className="h-6 bg-white/20 rounded w-1/2 animate-pulse"></div>
          </div>
          
          {/* Articles Grid Skeleton */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="bg-white/90 backdrop-blur-sm rounded-xl overflow-hidden animate-pulse">
                <div className="h-48 bg-gray-200"></div>
                <div className="p-6">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-700 to-violet-800 flex items-center justify-center">
        <div className="text-center text-white">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-80" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <h1 className="text-3xl font-bold mb-2">Fixture Not Found</h1>
          <p className="text-xl mb-6 opacity-90">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-white text-indigo-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-700 to-violet-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="bg-white/10 backdrop-blur-sm text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-colors flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back</span>
          </button>
        </div>

        {/* Fixture Header */}
        {fixtureInfo && (
          <div className="mb-12 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              {fixtureInfo.home_team} vs {fixtureInfo.away_team}
            </h1>
            {(fixtureInfo.home_score !== undefined && fixtureInfo.away_score !== undefined) && (
              <div className="text-3xl md:text-4xl font-bold text-white/90 mb-4">
                {fixtureInfo.home_score} - {fixtureInfo.away_score}
              </div>
            )}
            <div className="text-lg text-white/90 mb-2">
              {formatDate(fixtureInfo.match_date)}
            </div>
            <div className="text-md text-white/80">
              {fixtureInfo.competition} • {articles.length} Article{articles.length !== 1 ? 's' : ''}
            </div>
          </div>
        )}

        {/* Articles Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <div
              key={article.id}
              onClick={() => router.push(`/article/${article.id}`)}
              className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg overflow-hidden cursor-pointer hover:shadow-xl hover:-translate-y-1 transition-all duration-200 group"
            >
              {/* Article Image */}
              <div className="relative h-48 overflow-hidden">
                {article.image ? (
                  <img
                    src={article.image.startsWith('/api/') 
                      ? `http://localhost:5000${article.image}` 
                      : article.image
                    }
                    alt={`${article.title} thumbnail`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const parent = target.parentElement!;
                      parent.innerHTML = `
                        <div class="w-full h-full bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center">
                          <div class="text-center text-white">
                            <svg class="w-12 h-12 mx-auto mb-2 opacity-80" fill="currentColor" viewBox="0 0 20 20">
                              <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                            </svg>
                            <p class="text-sm font-medium">Article</p>
                          </div>
                        </div>
                      `;
                    }}
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center">
                    <div className="text-center text-white">
                      <svg className="w-12 h-12 mx-auto mb-2 opacity-80" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                      </svg>
                      <p className="text-sm font-medium">Article</p>
                    </div>
                  </div>
                )}
                
                {/* Category Badge */}
                <div className="absolute top-3 left-3">
                  <span className={`${getCategoryColor(article.category)} text-white px-3 py-1 rounded-full text-xs font-medium`}>
                    {getCategoryName(article.category)}
                  </span>
                </div>
              </div>

              {/* Article Content */}
              <div className="p-6">
                <h3 className="font-bold text-slate-900 mb-3 line-clamp-2 group-hover:text-indigo-600 transition-colors">
                  {article.title}
                </h3>
                <p className="text-slate-600 text-sm mb-4 line-clamp-3">
                  {article.excerpt}
                </p>
                
                {/* Meta Information */}
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>{article.readTime}</span>
                  <span>{formatTime(article.created_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {articles.length === 0 && !loading && (
          <div className="text-center py-16 text-white">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-80" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
            </svg>
            <h2 className="text-2xl font-bold mb-2">No Articles Found</h2>
            <p className="text-lg opacity-90">No articles have been published for this fixture yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
