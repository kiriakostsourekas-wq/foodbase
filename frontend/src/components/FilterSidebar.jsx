import { useState } from 'react';
import { ChevronDown, X, SlidersHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';

function FilterSection({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border-b border-border/50 pb-4 mb-4 last:border-0">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full text-sm font-semibold text-foreground mb-3"
      >
        {title}
        <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="space-y-2">{children}</div>}
    </div>
  );
}

function CheckboxItem({ label, checked, onChange, count }) {
  return (
    <label className="flex items-center gap-2.5 cursor-pointer group">
      <Checkbox checked={checked} onCheckedChange={onChange} />
      <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors flex-1">
        {label}
      </span>
      {count !== undefined && (
        <span className="text-xs text-muted-foreground/60">{count}</span>
      )}
    </label>
  );
}

export default function FilterSidebar({
  filters,
  onFilterChange,
  categories = [],
  regions = [],
  certifications = [],
}) {
  const activeCount = Object.values(filters).reduce((sum, val) => {
    if (Array.isArray(val)) return sum + val.length;
    if (typeof val === 'boolean' && val) return sum + 1;
    return sum;
  }, 0);

  const toggleArrayFilter = (key, value) => {
    const arr = filters[key] || [];
    onFilterChange({
      ...filters,
      [key]: arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value],
    });
  };

  const toggleBoolFilter = (key) => {
    onFilterChange({ ...filters, [key]: !filters[key] });
  };

  return (
    <div className="space-y-0">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-muted-foreground" />
          <h3 className="font-semibold text-sm">Filters</h3>
          {activeCount > 0 && (
            <Badge variant="secondary" className="text-[10px] h-5 px-1.5">
              {activeCount}
            </Badge>
          )}
        </div>
        {activeCount > 0 && (
          <Button
            variant="ghost"
            size="sm"
            className="text-xs h-7 text-muted-foreground"
            onClick={() => onFilterChange({
              categories: [], regions: [], certifications: [],
              exportReady: false, privateLabel: false, organic: false, verified: false,
            })}
          >
            <X className="w-3 h-3 mr-1" /> Clear all
          </Button>
        )}
      </div>

      {/* Category */}
      <FilterSection title="Product Category">
        {categories.map(cat => (
          <CheckboxItem
            key={cat.value}
            label={cat.label}
            count={cat.count}
            checked={(filters.categories || []).includes(cat.value)}
            onChange={() => toggleArrayFilter('categories', cat.value)}
          />
        ))}
      </FilterSection>

      {/* Region */}
      <FilterSection title="Region" defaultOpen={false}>
        {regions.map(region => (
          <CheckboxItem
            key={region.value}
            label={region.label}
            count={region.count}
            checked={(filters.regions || []).includes(region.value)}
            onChange={() => toggleArrayFilter('regions', region.value)}
          />
        ))}
      </FilterSection>

      {/* Certifications */}
      <FilterSection title="Certifications" defaultOpen={false}>
        {certifications.map(cert => (
          <CheckboxItem
            key={cert.value}
            label={cert.label}
            count={cert.count}
            checked={(filters.certifications || []).includes(cert.value)}
            onChange={() => toggleArrayFilter('certifications', cert.value)}
          />
        ))}
      </FilterSection>

      {/* Quick Filters */}
      <FilterSection title="Quick Filters">
        <CheckboxItem
          label="Verified suppliers only"
          checked={filters.verified || false}
          onChange={() => toggleBoolFilter('verified')}
        />
        <CheckboxItem
          label="Export ready"
          checked={filters.exportReady || false}
          onChange={() => toggleBoolFilter('exportReady')}
        />
        <CheckboxItem
          label="Private label available"
          checked={filters.privateLabel || false}
          onChange={() => toggleBoolFilter('privateLabel')}
        />
        <CheckboxItem
          label="Organic / Sustainable"
          checked={filters.organic || false}
          onChange={() => toggleBoolFilter('organic')}
        />
      </FilterSection>
    </div>
  );
}
