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
  image?: string;
}

export default function ArticlePage() {
  const params = useParams();
  const router = useRouter();
  const [article, setArticle] = useState<Article | null>(null);
  const [relatedArticles, setRelatedArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingRelated, setLoadingRelated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRelatedArticles = async (currentArticle: Article) => {
    try {
      setLoadingRelated(true);
      
      // Fetch articles from the same fixture (same teams and match date)
      const response = await fetch(`http://localhost:5000/api/articles?limit=20&offset=0`);
      const data = await response.json();
      
      if (data.success) {
        const related = data.data.filter((art: Article) => 
          art.id !== currentArticle.id && // Exclude current article
          art.home_team === currentArticle.home_team &&
          art.away_team === currentArticle.away_team &&
          art.match_date === currentArticle.match_date
        ).slice(0, 4); // Get up to 4 related articles
        
        setRelatedArticles(related);
      }
    } catch (err) {
      console.error('Error fetching related articles:', err);
    } finally {
      setLoadingRelated(false);
    }
  };

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
          // Fetch related articles after getting the main article
          fetchRelatedArticles(data.data);
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
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-700 to-violet-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
            <span className="ml-3 text-white/90">Loading article...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-700 to-violet-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white/90 backdrop-blur-md border border-white/20 rounded-xl p-6">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <span className="text-red-700">{error}</span>
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-700 to-violet-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center text-white/80 hover:text-white hover:bg-white/10 px-4 py-2 rounded-lg mb-8 transition-all duration-200"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Match Reports
        </button>

        {/* Article Layout */}
        <article className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          {/* Hero Section with Thumbnail and Title Overlay */}
          <div className="relative h-96 overflow-hidden">
            {article.image ? (
              <img
                src={article.image.startsWith('/api/') 
                  ? `http://localhost:5000${article.image}` 
                  : article.image
                }
                alt={`${article.title} thumbnail`}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  const parent = target.parentElement!;
                  parent.innerHTML = `
                    <div class="w-full h-full bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center">
                      <div class="text-center text-white">
                        <svg class="w-20 h-20 mx-auto mb-4 opacity-80" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd" />
                        </svg>
                        <p class="text-xl font-medium">Match Analysis</p>
                      </div>
                    </div>
                  `;
                }}
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center">
                <div className="text-center text-white">
                  <svg className="w-20 h-20 mx-auto mb-4 opacity-80" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                  </svg>
                  <p className="text-xl font-medium">Match Analysis</p>
                </div>
              </div>
            )}
            
            {/* Title Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-black/20 flex items-end">
              <div className="p-8 text-white w-full">
                <div className="mb-4">
                  <span className="inline-block bg-white/20 backdrop-blur-md px-4 py-2 rounded-full text-sm font-medium mb-4">
                    {article.competition}
                  </span>
                </div>
                <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold leading-tight mb-4">
                  {article.title}
                </h1>
                <div className="flex items-center space-x-6 text-white/90">
                  <span>{formatDate(article.match_date)}</span>
                  <span>•</span>
                  <span>By {article.author}</span>
                  <span>•</span>
                  <span>{article.readTime}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Article Content */}
          <div className="p-8 lg:p-12">
            {/* Article Meta */}
            <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-200/50">
              <div className="flex items-center space-x-4 text-base text-slate-600">
                <span>{article.word_count} words</span>
                <span>•</span>
                <span>Published {formatDate(article.created_at)}</span>
              </div>
              <span className="text-sm font-medium text-indigo-600 bg-indigo-100 px-4 py-2 rounded-full shadow-sm">
                {article.category.replace('_', ' ').toUpperCase()}
              </span>
            </div>

            {/* Tags */}
            <div className="flex flex-wrap gap-3 mb-8">
              {article.tags.map((tag, index) => (
                <span
                  key={index}
                  className="bg-slate-100/80 text-slate-700 px-4 py-2 rounded-full text-sm border border-slate-200/50 backdrop-blur-sm"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* Article Body */}
            <div className="prose prose-lg max-w-none prose-slate">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  h1: ({children}) => <h1 className="text-3xl font-bold text-slate-900 mb-4 mt-6">{children}</h1>,
                  h2: ({children}) => <h2 className="text-2xl font-bold text-slate-900 mb-3 mt-5">{children}</h2>,
                  h3: ({children}) => <h3 className="text-xl font-bold text-slate-900 mb-2 mt-4">{children}</h3>,
                  h4: ({children}) => <h4 className="text-lg font-bold text-slate-900 mb-2 mt-3">{children}</h4>,
                  p: ({children}) => <p className="mb-4 text-slate-700 leading-relaxed">{children}</p>,
                  ul: ({children}) => <ul className="list-disc list-inside mb-4 text-slate-700 space-y-1">{children}</ul>,
                  ol: ({children}) => <ol className="list-decimal list-inside mb-4 text-slate-700 space-y-1">{children}</ol>,
                  li: ({children}) => <li className="text-slate-700">{children}</li>,
                  strong: ({children}) => <strong className="font-bold text-slate-900">{children}</strong>,
                  em: ({children}) => <em className="italic text-slate-700">{children}</em>,
                  blockquote: ({children}) => <blockquote className="border-l-4 border-indigo-500 pl-4 italic text-slate-600 mb-4 bg-indigo-50 py-2">{children}</blockquote>,
                  code: ({children}) => <code className="bg-slate-100 px-2 py-1 rounded text-sm font-mono text-slate-800">{children}</code>,
                  pre: ({children}) => <pre className="bg-slate-100 p-4 rounded-lg overflow-x-auto mb-4">{children}</pre>,
                }}
              >
                {article.content}
              </ReactMarkdown>
            </div>

            {/* Article Footer */}
            <div className="mt-12 pt-8 border-t border-slate-200/50">
              <div className="flex items-center justify-between text-base text-slate-600">
                <span>Published on {formatDate(article.created_at)}</span>
                <button
                  onClick={() => router.back()}
                  className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 px-4 py-2 rounded-lg font-medium transition-all duration-200"
                >
                  ← Back to Match Reports
                </button>
              </div>
            </div>
          </div>
        </article>

        {/* Related Posts Strip */}
        {(relatedArticles.length > 0 || loadingRelated) && (
          <div className="mt-12">
            <div className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200/50">
              <div className="p-8">
                <h3 className="text-2xl font-bold text-slate-900 mb-6">
                  Related Posts from {article?.fixture_match}
                </h3>
                
                {loadingRelated ? (
                  <div className="flex space-x-6 overflow-x-auto pb-4">
                    {[...Array(4)].map((_, index) => (
                      <div key={index} className="flex-shrink-0 w-80 animate-pulse">
                        <div className="bg-gray-200 h-48 rounded-xl mb-4"></div>
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex space-x-6 overflow-x-auto pb-4 scrollbar-hide">
                    {relatedArticles.map((relatedArticle) => (
                      <div
                        key={relatedArticle.id}
                        onClick={() => router.push(`/article/${relatedArticle.id}`)}
                        className="flex-shrink-0 w-80 bg-white rounded-xl border border-slate-200/50 hover:shadow-lg transition-all duration-200 cursor-pointer group"
                      >
                        <div className="relative h-48 overflow-hidden rounded-t-xl">
                          {relatedArticle.image ? (
                            <img
                              src={relatedArticle.image.startsWith('/api/') 
                                ? `http://localhost:5000${relatedArticle.image}` 
                                : relatedArticle.image
                              }
                              alt={`${relatedArticle.title} thumbnail`}
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
                          <div className="absolute top-3 left-3">
                            <span className="bg-indigo-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                              {relatedArticle.category.replace('_', ' ').toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="p-6">
                          <h4 className="font-bold text-slate-900 mb-2 line-clamp-2 group-hover:text-indigo-600 transition-colors">
                            {relatedArticle.title}
                          </h4>
                          <p className="text-slate-600 text-sm mb-3 line-clamp-2">
                            {relatedArticle.content.substring(0, 120)}...
                          </p>
                          <div className="flex items-center justify-between text-xs text-slate-500">
                            <span>{relatedArticle.readTime}</span>
                            <span>{formatDate(relatedArticle.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                
                {relatedArticles.length === 0 && !loadingRelated && (
                  <div className="text-center py-8 text-slate-500">
                    <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                    </svg>
                    <p>No other articles found for this fixture.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
