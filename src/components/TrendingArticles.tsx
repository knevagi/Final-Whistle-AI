'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface TrendingArticle {
  id: string;
  title: string;
  excerpt: string;
  category: string;
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
  image?: string;
}

interface TrendingArticlesProps {
  apiBaseUrl?: string;
}

export default function TrendingArticles({ apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000' }: TrendingArticlesProps) {
  const router = useRouter();
  const [articles, setArticles] = useState<TrendingArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrendingArticles = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch more articles to ensure we can find 5 unique fixtures
        const response = await fetch(`${apiBaseUrl}/api/articles?limit=20&offset=0`);
        const data = await response.json();
        
        if (data.success) {
          // Filter articles to get unique fixtures
          const uniqueFixtureArticles: TrendingArticle[] = [];
          const seenFixtures = new Set<string>();
          
          for (const article of data.data) {
            const fixtureKey = `${article.home_team}-${article.away_team}-${article.match_date}`;
            
            if (!seenFixtures.has(fixtureKey) && uniqueFixtureArticles.length < 5) {
              seenFixtures.add(fixtureKey);
              uniqueFixtureArticles.push(article);
            }
          }
          
          setArticles(uniqueFixtureArticles);
        } else {
          setError(data.error || 'Failed to fetch recent articles');
        }
      } catch (err) {
        setError('Network error: Unable to fetch recent articles');
        console.error('Error fetching recent articles:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendingArticles();
  }, [apiBaseUrl]);

  if (loading) {
    return (
        <div className="space-y-6">
        {[...Array(5)].map((_, index) => (
          <div key={index} className="flex space-x-4 animate-pulse">
            <div className="w-24 h-18 bg-gray-200 rounded-lg"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error || articles.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="w-24 h-18 bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">⚽</span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-base line-clamp-2">
              Sample Match Analysis: Team Performance Review
            </h3>
            <p className="text-sm text-gray-600 mt-1">Sports Analyst • 5 mins ago</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="w-24 h-18 bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">🏆</span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-base line-clamp-2">
              Player Focus: Rising Stars in Modern Football
            </h3>
            <p className="text-sm text-gray-600 mt-1">Sports Writer • 12 mins ago</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="w-24 h-18 bg-gradient-to-br from-purple-500 via-pink-500 to-rose-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">📊</span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-base line-clamp-2">
              Tactical Analysis: Modern Formation Trends
            </h3>
            <p className="text-sm text-gray-600 mt-1">Tactical Expert • 25 mins ago</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="w-24 h-18 bg-gradient-to-br from-green-500 via-emerald-500 to-teal-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">🎯</span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-base line-clamp-2">
              Transfer News: Latest Market Movements
            </h3>
            <p className="text-sm text-gray-600 mt-1">Transfer Insider • 1 hour ago</p>
          </div>
        </div>
        <div className="flex items-center space-x-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="w-24 h-18 bg-gradient-to-br from-orange-500 via-red-500 to-pink-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-sm">📝</span>
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 text-base line-clamp-2">
              Weekly Roundup: Premier League Highlights
            </h3>
            <p className="text-sm text-gray-600 mt-1">Editor • 2 hours ago</p>
          </div>
        </div>
      </div>
    );
  }

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} mins ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hrs ago`;
    return `${Math.floor(diffInMinutes / 1440)} days ago`;
  };

  return (
    <div className="space-y-4">
      {articles.map((article, index) => (
        <div 
          key={article.id}
          onClick={() => router.push(`/article/${article.id}`)}
          className="flex items-center space-x-4 p-5 bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/50 hover:bg-white hover:shadow-lg transition-all duration-200 cursor-pointer group"
        >
            <div className="relative w-24 h-18 flex-shrink-0">
            {article.image ? (
              <img
                src={article.image}
                alt={`${article.fixture_match} thumbnail`}
                className="w-full h-full object-cover rounded-lg"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const parent = target.parentElement!;
                  const gradients = [
                    'from-indigo-500 via-violet-500 to-purple-600',
                    'from-blue-500 via-cyan-500 to-teal-600',
                    'from-purple-500 via-pink-500 to-rose-600',
                    'from-green-500 via-emerald-500 to-teal-600',
                    'from-orange-500 via-red-500 to-pink-600'
                  ];
                  parent.innerHTML = `
                    <div class="w-full h-full bg-gradient-to-br ${gradients[index % 5]} rounded-lg flex items-center justify-center">
                      <span class="text-white text-sm">⚽</span>
                    </div>
                  `;
                }}
              />
            ) : (
              <div className={`w-full h-full bg-gradient-to-br ${
                index === 0 ? 'from-indigo-500 via-violet-500 to-purple-600' :
                index === 1 ? 'from-blue-500 via-cyan-500 to-teal-600' :
                index === 2 ? 'from-purple-500 via-pink-500 to-rose-600' :
                index === 3 ? 'from-green-500 via-emerald-500 to-teal-600' :
                'from-orange-500 via-red-500 to-pink-600'
              } rounded-lg flex items-center justify-center`}>
                <span className="text-white text-sm">⚽</span>
              </div>
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-gray-900 text-base line-clamp-2 group-hover:text-indigo-600 transition-colors">
              {article.title}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {article.author} • {getTimeAgo(article.created_at)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
