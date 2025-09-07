'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Article {
  id: string;
  title: string;
  content: string;
  category: string;
  word_count: number;
  created_at: string;
  fixture_match: string;
  match_date: string;
  match_time: string;
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
  competition: string;
  venue: string;
  tags: string[];
  author: string;
  readTime: string;
}

export default function ArticlePage() {
  const params = useParams();
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const articleId = params.id;
        const response = await fetch(`http://localhost:5000/api/articles/${articleId}`);
        const data = await response.json();
        
        if (data.success) {
          setArticle(data.data);
        } else {
          setError(data.error || 'Failed to fetch article');
        }
      } catch (err) {
        setError('Network error: Unable to fetch article');
        console.error('Error fetching article:', err);
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchArticle();
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

  const formatTime = (timeString: string) => {
    if (!timeString) return '';
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-GB', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">Loading article...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="text-red-700 dark:text-red-400">{error}</span>
            </div>
            <button
              onClick={() => router.back()}
              className="mt-3 text-red-600 hover:text-red-700 font-medium text-sm"
            >
              ← Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!article) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center text-gray-600 dark:text-gray-400 hover:text-green-600 dark:hover:text-green-400 mb-6 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Match Reports
        </button>

        {/* Article Header */}
        <article className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          {/* Match Info Header */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium bg-green-500 bg-opacity-30 px-3 py-1 rounded-full">
                {article.competition}
              </span>
              <span className="text-sm opacity-90">
                {formatDate(article.match_date)}
                {article.match_time && ` • ${formatTime(article.match_time)}`}
              </span>
            </div>
            
            <div className="text-center">
              <h1 className="text-2xl font-bold mb-4">{article.fixture_match}</h1>
              <div className="flex items-center justify-center space-x-8">
                <div className="text-center">
                  <div className="text-lg font-semibold">{article.home_team}</div>
                  <div className="text-3xl font-bold">{article.home_score}</div>
                </div>
                <div className="text-2xl font-bold">-</div>
                <div className="text-center">
                  <div className="text-lg font-semibold">{article.away_team}</div>
                  <div className="text-3xl font-bold">{article.away_score}</div>
                </div>
              </div>
              {article.venue && (
                <div className="text-sm opacity-90 mt-2">
                  {article.venue}
                </div>
              )}
            </div>
          </div>

          {/* Article Content */}
          <div className="p-6">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 leading-tight">
              {article.title}
            </h2>
            
            {/* Article Meta */}
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                <span>By {article.author}</span>
                <span>•</span>
                <span>{article.readTime}</span>
                <span>•</span>
                <span>{article.word_count} words</span>
              </div>
              <span className="text-sm font-medium text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900 px-3 py-1 rounded-full">
                {article.category.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-6">
              {article.tags.map((tag, index) => (
                <span
                  key={index}
                  className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm dark:bg-gray-700 dark:text-gray-300"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* Article Body */}
            <div className="prose prose-lg max-w-none dark:prose-invert">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({children}) => <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 mt-6">{children}</h1>,
                  h2: ({children}) => <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3 mt-5">{children}</h2>,
                  h3: ({children}) => <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 mt-4">{children}</h3>,
                  h4: ({children}) => <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2 mt-3">{children}</h4>,
                  p: ({children}) => <p className="mb-4 text-gray-800 dark:text-gray-200 leading-relaxed">{children}</p>,
                  ul: ({children}) => <ul className="list-disc list-inside mb-4 text-gray-800 dark:text-gray-200 space-y-1">{children}</ul>,
                  ol: ({children}) => <ol className="list-decimal list-inside mb-4 text-gray-800 dark:text-gray-200 space-y-1">{children}</ol>,
                  li: ({children}) => <li className="text-gray-800 dark:text-gray-200">{children}</li>,
                  strong: ({children}) => <strong className="font-bold text-gray-900 dark:text-white">{children}</strong>,
                  em: ({children}) => <em className="italic text-gray-800 dark:text-gray-200">{children}</em>,
                  blockquote: ({children}) => <blockquote className="border-l-4 border-green-500 pl-4 italic text-gray-700 dark:text-gray-300 mb-4">{children}</blockquote>,
                  code: ({children}) => <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm font-mono">{children}</code>,
                  pre: ({children}) => <pre className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-x-auto mb-4">{children}</pre>,
                }}
              >
                {article.content}
              </ReactMarkdown>
            </div>

            {/* Article Footer */}
            <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                <span>Published on {formatDate(article.created_at)}</span>
                <button
                  onClick={() => router.back()}
                  className="text-green-600 hover:text-green-700 font-medium"
                >
                  ← Back to Match Reports
                </button>
              </div>
            </div>
          </div>
        </article>
      </div>
    </div>
  );
}
