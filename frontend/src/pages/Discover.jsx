import { useCallback, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Map as MapIcon, SlidersHorizontal, X } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import SearchBar from '@/components/SearchBar';
import FilterSidebar from '@/components/FilterSidebar';
import SupplierCard from '@/components/SupplierCard';
import SupplierMap from '@/components/SupplierMap';
import { apiFetch } from '@/lib/api';
import { mapFacetOptions, mapOrganizationListItem } from '@/lib/foodbase';

const DEFAULT_FILTERS = {
  categories: [],
  regions: [],
  certifications: [],
  exportReady: false,
  privateLabel: false,
  organic: false,
  verified: false,
};

export default function Discover() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const initialQuery = params.get('q') || '';
  const initialCategory = params.get('category') || '';

  const [query, setQuery] = useState(initialQuery);
  const [filters, setFilters] = useState({
    ...DEFAULT_FILTERS,
    categories: initialCategory ? [initialCategory] : [],
  });
  const [highlightedId, setHighlightedId] = useState(null);
  const [flyTo, setFlyTo] = useState(null);

  const { data: organizationsResponse, isLoading, error } = useQuery({
    queryKey: ['organizations', query, filters],
    queryFn: async () => {
      const searchParams = new URLSearchParams({ limit: '100' });
      if (query) searchParams.set('q', query);
      if (filters.categories.length === 1) searchParams.set('category', filters.categories[0]);
      if (filters.regions.length === 1) searchParams.set('region', filters.regions[0]);
      if (filters.certifications.length === 1) {
        searchParams.set('certification', filters.certifications[0]);
      }
      if (filters.exportReady) searchParams.set('export_ready', 'true');
      if (filters.privateLabel) searchParams.set('private_label', 'true');
      if (filters.organic) searchParams.set('organic', 'true');
      if (filters.verified) searchParams.set('verified', 'true');
      return apiFetch(`/organizations?${searchParams.toString()}`);
    },
  });

  const { data: facetsResponse } = useQuery({
    queryKey: ['search-facets'],
    queryFn: () => apiFetch('/search-facets'),
  });

  const suppliers = useMemo(
    () => (organizationsResponse?.items || []).map(mapOrganizationListItem),
    [organizationsResponse]
  );
  const facets = useMemo(() => mapFacetOptions(facetsResponse), [facetsResponse]);

  const filteredSuppliers = useMemo(() => {
    return suppliers.filter(s => {
      if (query) {
        const q = query.toLowerCase();
        const match = s.name.toLowerCase().includes(q) ||
          (s.category || '').toLowerCase().includes(q) ||
          (s.subcategory || '').toLowerCase().includes(q) ||
          s.city.toLowerCase().includes(q) ||
          s.region.toLowerCase().includes(q) ||
          (s.shortDescription || '').toLowerCase().includes(q);
        if (!match) return false;
      }

      if (filters.categories.length && !filters.categories.includes(s.category)) return false;
      if (filters.regions.length && !filters.regions.includes(s.region)) return false;
      if (filters.certifications.length && !filters.certifications.some(c => s.certifications.includes(c))) return false;
      if (filters.exportReady && !s.exportReady) return false;
      if (filters.privateLabel && !s.privateLabel) return false;
      if (filters.organic && !s.organic) return false;
      if (filters.verified && !s.verified) return false;

      return true;
    });
  }, [suppliers, query, filters]);

  const handleHover = useCallback((id) => setHighlightedId(id), []);
  const handleLeave = useCallback(() => setHighlightedId(null), []);

  const handleClickMarker = useCallback((id) => {
    const supplier = filteredSuppliers.find(s => s.id === id);
    if (supplier) {
      setFlyTo({ center: [supplier.lat, supplier.lng], zoom: 10 });
      setHighlightedId(id);
    }
  }, [filteredSuppliers]);

  const activeFilterCount = Object.values(filters).reduce((sum, val) => {
    if (Array.isArray(val)) return sum + val.length;
    if (typeof val === 'boolean' && val) return sum + 1;
    return sum;
  }, 0);

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Top bar */}
      <div className="bg-white border-b border-border/50 px-4 py-3">
        <div className="max-w-full mx-auto flex items-center gap-3">
          <div className="flex-1 max-w-xl">
            <SearchBar
              size="sm"
              placeholder="Search suppliers, products, regions..."
              initialValue={initialQuery}
              onSearch={(q) => setQuery(q)}
            />
          </div>
          <div className="hidden sm:flex items-center gap-2">
            {query && (
              <Badge variant="secondary" className="gap-1.5 py-1 px-3">
                "{query}"
                <button onClick={() => setQuery('')}>
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            )}
            <span className="text-sm text-muted-foreground">
              {filteredSuppliers.length} supplier{filteredSuppliers.length !== 1 ? 's' : ''}
            </span>
          </div>
          {/* Mobile filter toggle */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline" size="sm" className="lg:hidden gap-1.5">
                <SlidersHorizontal className="w-4 h-4" />
                Filters
                {activeFilterCount > 0 && (
                  <Badge className="h-5 w-5 p-0 flex items-center justify-center text-[10px]">
                    {activeFilterCount}
                  </Badge>
                )}
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-80 p-5 overflow-y-auto">
              <FilterSidebar
                filters={filters}
                onFilterChange={setFilters}
                categories={facets.categories}
                regions={facets.regions}
                certifications={facets.certifications}
              />
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Filters - Desktop */}
        <div className="hidden lg:block w-72 border-r border-border/50 bg-white overflow-y-auto p-5 custom-scrollbar">
          <FilterSidebar
            filters={filters}
            onFilterChange={setFilters}
            categories={facets.categories}
            regions={facets.regions}
            certifications={facets.certifications}
          />
        </div>

        {/* Results list */}
        <div className="w-full lg:w-[380px] xl:w-[420px] bg-white border-r border-border/50 overflow-y-auto custom-scrollbar flex-shrink-0">
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between mb-1">
              <h2 className="font-semibold text-sm text-foreground">
                {filteredSuppliers.length} Results
              </h2>
            </div>

            {isLoading && (
              <div className="text-sm text-muted-foreground py-8">Loading suppliers...</div>
            )}

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {error.message}
              </div>
            )}

            {!isLoading && !error && (
              filteredSuppliers.length === 0 ? (
                <div className="text-center py-16">
                  <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto mb-4">
                    <MapIcon className="w-7 h-7 text-muted-foreground" />
                  </div>
                  <p className="font-medium text-foreground">No suppliers found</p>
                  <p className="text-sm text-muted-foreground mt-1">Try adjusting your filters or search query</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-4"
                    onClick={() => { setQuery(''); setFilters(DEFAULT_FILTERS); }}
                  >
                    Clear all filters
                  </Button>
                </div>
              ) : (
                filteredSuppliers.map(supplier => (
                  <SupplierCard
                    key={supplier.id}
                    supplier={supplier}
                    compact
                    isHighlighted={highlightedId === supplier.id}
                    onHover={handleHover}
                    onLeave={handleLeave}
                  />
                ))
              )
            )}
          </div>
        </div>

        {/* Map */}
        <div className="hidden sm:block flex-1 p-3">
          <SupplierMap
            suppliers={filteredSuppliers}
            highlightedId={highlightedId}
            onHoverSupplier={handleHover}
            onLeaveSupplier={handleLeave}
            onClickSupplier={handleClickMarker}
            flyTo={flyTo}
          />
        </div>
      </div>
    </div>
  );
}
