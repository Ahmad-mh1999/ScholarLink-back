import React from 'react';

// Dummy variables so this page never crashes if RTK Query providers are not mounted.
const isLoading = false;
const isFetching = false;
const articles = { results: [], count: 0 };
import * as ReactRouterDOM from 'react-router-dom';
import {
  Search,
  ChevronLeft,
  ChevronRight,
  Bookmark,
  Eye,
  Heart,
  User,
  CheckCircle,
} from 'lucide-react';
// NOTE: Keep this page self-contained for now; RTK Query hooks are not wired here.
// import { useGetArticlesQuery, useGetCategoriesQuery } from '../api/baseApi';

// Sub-component: Article Feed Card
const FeedCard = ({ article }) => (
  <ReactRouterDOM.Link to={`/article/${article.slug}`} className="block">
    <div className="bg-white rounded-[2rem] border border-gray-100 shadow-sm overflow-hidden flex flex-col md:flex-row gap-8 p-8 group hover:shadow-2xl hover:shadow-slate-200/50 transition-all duration-500 animate-in fade-in slide-in-from-bottom-4 cursor-pointer">
    {/* Image Container */}
    <div className="w-full md:w-80 h-64 md:h-auto shrink-0 rounded-2xl overflow-hidden relative">
      <img 
        src={article.image || 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&q=80&w=800'} 
        alt={article.title}
        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
      />
      <div className="absolute top-4 left-4">
        <span className="px-4 py-1.5 bg-accent/90 backdrop-blur-md text-white text-[10px] font-bold rounded-full uppercase tracking-widest">
          {article.category_name || 'Engineering'}
        </span>
      </div>
    </div>

    {/* Content Container */}
    <div className="flex-1 flex flex-col justify-between py-2">
      <div className="space-y-4">
        <div className="flex justify-between items-start">
          <h3 className="text-2xl font-bold text-primary leading-snug tracking-tight group-hover:text-accent transition-colors line-clamp-2">
            {article.title}
          </h3>
          <button className="p-2 text-gray-300 hover:text-primary transition-colors">
            <Bookmark className="w-6 h-6" />
          </button>
        </div>
        
        <p className="text-sm text-gray-500 font-medium leading-relaxed tracking-tight line-clamp-3 italic opacity-80">
          {article.abstract || "This study explores the recent advancements in bio-mimetic neural networks designed for industrial automation, prioritizing latency reduction and adaptive..."}
        </p>

        <div className="flex items-center gap-4 pt-4">
          <div className="w-10 h-10 rounded-full bg-accent/10 flex items-center justify-center text-accent overflow-hidden border-2 border-white shadow-sm">
            <User className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-bold text-primary leading-none mb-1">{article.author_name || "Dr. Alistair Vance"}</p>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{article.author_role || "Senior Fellow, MIT"}</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-8 pt-6 border-t border-gray-50 mt-6">
        <div className="flex items-center gap-2 text-gray-400">
          <Eye className="w-4 h-4" />
          <span className="text-[11px] font-bold uppercase tracking-widest">{article.views_count || '12.4k'}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-400">
          <Heart className="w-4 h-4" />
          <span className="text-[11px] font-bold uppercase tracking-widest">{article.likes_count || '2.1k'}</span>
        </div>
      </div>
    </div>
  </div>
 </ReactRouterDOM.Link>
);

// Sub-component: Recommended Sidebar Item
const RecommendedItem = ({ item }) => (
  <div className="space-y-2 group cursor-pointer">
    <p className="text-[9px] font-bold text-accent uppercase tracking-widest">{item.category}</p>
    <h4 className="text-sm font-bold text-primary leading-tight tracking-tight group-hover:underline line-clamp-2">
      {item.title}
    </h4>
    <p className="text-[10px] text-gray-400 font-medium">By {item.author} • {item.readTime}</p>
  </div>
);

// Sub-component: Researcher Item
const ResearcherItem = ({ researcher, index }) => (
  <div className="flex items-center justify-between group cursor-pointer">
    <div className="flex items-center gap-4">
      <span className="text-[11px] font-bold text-gray-300 w-4 italic">{index + 1}</span>
      <div className="w-10 h-10 rounded-full bg-primary/5 flex items-center justify-center text-primary font-bold border-2 border-white shadow-sm overflow-hidden">
        <User className="w-5 h-5" />
      </div>
      <div>
        <div className="flex items-center gap-1">
          <p className="text-sm font-bold text-primary leading-tight tracking-tight group-hover:text-accent transition-colors">{researcher.name}</p>
          {researcher.verified && <CheckCircle className="w-3 h-3 text-accent" fill="currentColor" />}
        </div>
        <p className="text-[10px] font-medium text-gray-400 tracking-tight">{researcher.publications} Publications</p>
      </div>
    </div>
  </div>
);

const ResearchFeed = () => {
  const [params, setParams] = React.useState({
    search: '',
    category__slug: '',
    page: 1,
    ordering: '-created_at',
    this_week: true,
    this_month: false,
  });

  const [handleSearchTimeout, setHandleSearchTimeout] = React.useState(null);

  const handleSearch = (e) => {
    const value = e.target.value;
    // debounce to avoid rapid refetch loops while typing
    if (handleSearchTimeout) clearTimeout(handleSearchTimeout);
    const t = setTimeout(() => {
      setParams(prev => ({ ...prev, search: value, page: 1 }));
    }, 250);
    setHandleSearchTimeout(t);
  };

  const handleCategoryChange = (slug) => {
    setParams(prev => ({ ...prev, category__slug: slug, page: 1 }));
  };

  const handleTimelineChange = (timeline) => {
    setParams(prev => ({
      ...prev,
      this_week: timeline === 'week',
      this_month: timeline === 'month',
      page: 1,
    }));
  };

  const handleSortChange = (e) => {
    setParams(prev => ({ ...prev, ordering: e.target.value, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    setParams(prev => ({ ...prev, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const demoRecommended = [
    { category: 'Architecture', title: 'Sustainable Urbanism: The vertical forest expansion in Milan.', author: 'Sarah Jenkins', readTime: '4 min read' },
    { category: 'Digital Ethics', title: 'The Algorithm Gap: Bias in decentralized hiring protocols.', author: 'Dr. Marcus Thorne', readTime: '8 min read' },
    { category: 'Philosophy', title: 'Cognitive Sovereignty in the Age of Artificial Intelligence.', author: 'Prof. Hana Sato', readTime: '12 min read' },
  ];

  const demoResearchers = [
    { name: 'Dr. Sofia Chen', publications: 24, verified: true },
    { name: 'Prof. Liam O\'Neil', publications: 19, verified: false },
    { name: 'Aria Montgomery', publications: 14, verified: false },
  ];

  return (
    <div className="flex flex-col lg:flex-row gap-12">
      {/* 1. Left Sidebar: Filters */}
      <aside className="lg:w-64 space-y-12 shrink-0">
        <div>
          <p className="text-[10px] font-bold text-gray-300 uppercase tracking-[0.3em] mb-8">Categories</p>
          <div className="space-y-2">
            <button 
              onClick={() => handleCategoryChange('')}
              className={`w-full text-left px-6 py-3.5 rounded-2xl text-sm font-bold tracking-tight transition-all flex items-center justify-between group
                ${params.category__slug === '' ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-gray-500 hover:bg-white hover:text-primary'}
              `}
            >
              All Disciplines
              {params.category__slug === '' && <div className="w-1.5 h-1.5 bg-accent rounded-full"></div>}
            </button>
            {['Engineering', 'Medical', 'Tech', 'Arts'].map((cat) => (
              <button 
                key={cat}
                onClick={() => handleCategoryChange(cat.toLowerCase())}
                className={`w-full text-left px-6 py-3.5 rounded-2xl text-sm font-bold tracking-tight transition-all flex items-center justify-between group
                  ${params.category__slug === cat.toLowerCase() ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-gray-500 hover:bg-white hover:text-primary'}
                `}
              >
                <div className="flex items-center gap-3">
                  <div className={`w-1.5 h-1.5 rounded-full transition-colors ${params.category__slug === cat.toLowerCase() ? 'bg-accent' : 'bg-gray-200 group-hover:bg-accent'}`}></div>
                  {cat}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-[10px] font-bold text-gray-300 uppercase tracking-[0.3em] mb-8">Timeline</p>
          <div className="space-y-4 px-2">
            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="radio" 
                name="timeline" 
                className="w-4 h-4 border-2 border-gray-200 text-accent focus:ring-accent"
                checked={params.this_week}
                onChange={() => handleTimelineChange('week')}
              />
              <span className="text-sm font-bold text-gray-500 group-hover:text-primary transition-colors">This Week</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer group">
              <input 
                type="radio" 
                name="timeline" 
                className="w-4 h-4 border-2 border-gray-200 text-accent focus:ring-accent"
                checked={params.this_month}
                onChange={() => handleTimelineChange('month')}
              />
              <span className="text-sm font-bold text-gray-500 group-hover:text-primary transition-colors">This Month</span>
            </label>
          </div>
        </div>

        <div>
          <p className="text-[10px] font-bold text-gray-300 uppercase tracking-[0.3em] mb-8">Sort By</p>
          <select 
            value={params.ordering}
            onChange={handleSortChange}
            className="w-full bg-white border-none rounded-2xl py-4 px-6 text-sm font-bold text-primary shadow-sm focus:ring-2 focus:ring-accent/20 transition-all cursor-pointer appearance-none"
          >
            <option value="-created_at">Newest First</option>
            <option value="-views_count">Most Viewed</option>
            <option value="-likes_count">Most Liked</option>
          </select>
        </div>
      </aside>

      {/* 2. Main Content: Feed */}
      <main className="flex-1 space-y-12">
        <div className="flex flex-col gap-2">
        <h1 className="text-5xl font-serif font-bold text-red-500 tracking-tight">HELLO WORLD TEST</h1>         <h1 className="text-5xl font-serif font-bold text-primary tracking-tight">Research Feed</h1>
          <p className="text-gray-400 font-medium italic">Curated developments across global academia.</p>
        </div>

        {/* Top Search Bar (Small Screen / Feed Header) */}
        <div className="relative group lg:hidden">
          <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-accent w-5 h-5 transition-colors" />
          <input
            type="text"
            placeholder="Search the archive..."
            value={params.search}
            onChange={handleSearch}
            className="w-full bg-white border-none rounded-2xl py-5 pl-14 pr-6 text-sm placeholder-gray-400 shadow-sm focus:ring-2 focus:ring-accent/20 outline-none transition-all"
          />
        </div>

        {/* Articles List */}
        <div className="space-y-8">
          {/* Safe fallback: render without RTK Query wiring to prevent blank-screen / infinite retries */}
          <div className="bg-white p-20 rounded-[2rem] text-center space-y-4">
            <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto text-gray-300">
              <Search className="w-10 h-10" />
            </div>
            <h3 className="text-xl font-bold text-primary">No results found</h3>
            <p className="text-gray-400">Try adjusting your filters or search terms.</p>
          </div>
        </div>

        {/* Pagination (disabled until RTK Query hooks are wired) */}
        {false && (
          <div className="flex items-center justify-center gap-2 pt-8">
            <button 
              onClick={() => handlePageChange(params.page - 1)}
              disabled={params.page === 1}
              className="p-3 rounded-xl bg-white text-gray-400 hover:text-primary disabled:opacity-30 transition-all shadow-sm"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-1">
              {[...Array(Math.min(5, Math.ceil(articles.count / 10)))].map((_, i) => (
                <button
                  key={i + 1}
                  onClick={() => handlePageChange(i + 1)}
                  className={`w-11 h-11 rounded-xl text-sm font-bold transition-all
                    ${params.page === i + 1 ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'bg-white text-gray-500 hover:bg-gray-50'}
                  `}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <button 
              onClick={() => handlePageChange(params.page + 1)}
              disabled={params.page >= Math.ceil(articles.count / 10)}
              className="p-3 rounded-xl bg-white text-gray-400 hover:text-primary disabled:opacity-30 transition-all shadow-sm"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </main>

      {/* 3. Right Sidebar: Recommendations & More */}
      <aside className="lg:w-80 space-y-12 shrink-0">
        <div className="bg-white p-10 rounded-[2.5rem] border border-gray-50 shadow-sm">
          <p className="text-[10px] font-bold text-gray-300 uppercase tracking-[0.3em] mb-10">Recommended For You</p>
          <div className="space-y-10">
            {demoRecommended.map((item, i) => (
              <RecommendedItem key={i} item={item} />
            ))}
          </div>
          <button className="w-full mt-12 py-4 rounded-xl border-2 border-gray-50 text-[10px] font-bold text-gray-400 uppercase tracking-widest hover:bg-gray-50 hover:text-primary transition-all">
            View All Recommendations
          </button>
        </div>

        <div className="px-4">
          <p className="text-[10px] font-bold text-gray-300 uppercase tracking-[0.3em] mb-10">Top Researchers</p>
          <div className="space-y-8">
            {demoResearchers.map((researcher, i) => (
              <ResearcherItem key={i} researcher={researcher} index={i} />
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
};

export default ResearchFeed;

