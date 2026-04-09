import { Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SearchBar({
  size = 'lg',
  placeholder,
  className = '',
  onSearch,
  initialValue = '',
}) {
  const [query, setQuery] = useState(initialValue);
  const navigate = useNavigate();

  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(query);
    } else {
      navigate(`/discover?q=${encodeURIComponent(query)}`);
    }
  };

  const placeholderText = placeholder || 'Search Greek producers — e.g. "olive oil", "honey", "packaging"';

  const sizeClasses = size === 'lg'
    ? 'h-14 sm:h-16 text-base sm:text-lg pl-14 pr-6'
    : 'h-11 text-sm pl-10 pr-4';

  const iconClasses = size === 'lg'
    ? 'left-5 w-5 h-5'
    : 'left-3.5 w-4 h-4';

  return (
    <form onSubmit={handleSubmit} className={`relative ${className}`}>
      <Search className={`absolute top-1/2 -translate-y-1/2 text-muted-foreground ${iconClasses}`} />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholderText}
        className={`w-full bg-white border border-border/60 rounded-2xl shadow-sm hover:shadow-md 
          focus:shadow-lg focus:ring-2 focus:ring-primary/20 focus:border-primary/40 
          transition-all duration-200 outline-none placeholder:text-muted-foreground/60 ${sizeClasses}`}
      />
      {size === 'lg' && (
        <button
          type="submit"
          className="absolute right-2.5 top-1/2 -translate-y-1/2 bg-primary text-primary-foreground 
            px-5 py-2 rounded-xl text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          Search
        </button>
      )}
    </form>
  );
}
