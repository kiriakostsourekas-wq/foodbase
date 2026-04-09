import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Shield, X, Plus, ArrowRight, Check, Minus, Globe } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { apiFetch } from '@/lib/api';
import { mapOrganizationListItem } from '@/lib/foodbase';

const COMPARE_FIELDS = [
  { key: 'location', label: 'Location', render: (s) => `${s.city}, ${s.region}` },
  { key: 'category', label: 'Category', render: (s) => s.subcategory },
  { key: 'moq', label: 'Min. Order Quantity', render: (s) => s.moq },
  { key: 'leadTime', label: 'Lead Time', render: (s) => s.leadTime },
  { key: 'capacity', label: 'Production Capacity', render: (s) => s.capacity },
  { key: 'certifications', label: 'Certifications', render: (s) => (
    <div className="flex flex-wrap gap-1">
      {s.certifications.map(c => (
        <Badge key={c} variant="outline" className="text-[10px]">{c}</Badge>
      ))}
    </div>
  )},
  { key: 'privateLabel', label: 'Private Label', render: (s) => s.privateLabel ? (
    <span className="flex items-center gap-1 text-emerald-600"><Check className="w-4 h-4" /> Available</span>
  ) : (
    <span className="flex items-center gap-1 text-muted-foreground"><Minus className="w-4 h-4" /> No</span>
  )},
  { key: 'exportReady', label: 'Export Ready', render: (s) => s.exportReady ? (
    <span className="flex items-center gap-1 text-emerald-600"><Check className="w-4 h-4" /> Yes</span>
  ) : (
    <span className="flex items-center gap-1 text-muted-foreground"><Minus className="w-4 h-4" /> No</span>
  )},
  { key: 'verified', label: 'Verified', render: (s) => s.verified ? (
    <span className="flex items-center gap-1 text-emerald-600"><Check className="w-4 h-4" /> Yes</span>
  ) : (
    <span className="flex items-center gap-1 text-muted-foreground"><Minus className="w-4 h-4" /> No</span>
  )},
  { key: 'organic', label: 'Organic', render: (s) => s.organic ? (
    <span className="flex items-center gap-1 text-emerald-600"><Check className="w-4 h-4" /> Certified</span>
  ) : (
    <span className="flex items-center gap-1 text-muted-foreground"><Minus className="w-4 h-4" /> No</span>
  )},
  { key: 'exportMarkets', label: 'Export Markets', render: (s) => (
    <div className="flex flex-wrap gap-1">
      {s.exportMarkets.length > 0 ? s.exportMarkets.map((market) => (
        <Badge key={market} variant="outline" className="text-[10px]">{market}</Badge>
      )) : <span className="text-muted-foreground">Not disclosed</span>}
    </div>
  )},
  { key: 'employees', label: 'Company Size', render: (s) => `${s.employees} employees` },
  { key: 'yearFounded', label: 'Founded', render: (s) => s.yearFounded },
];

export default function Compare() {
  const [selected, setSelected] = useState([]);
  const { data, isLoading, error } = useQuery({
    queryKey: ['compare-organizations'],
    queryFn: async () => apiFetch('/organizations?limit=20'),
  });
  const allSuppliers = useMemo(
    () => (data?.items || []).map(mapOrganizationListItem),
    [data]
  );

  useEffect(() => {
    if (allSuppliers.length >= 3 && selected.length === 0) {
      setSelected(allSuppliers.slice(0, 3).map((supplier) => supplier.id));
    }
  }, [allSuppliers, selected.length]);

  const suppliers = selected.map(id => allSuppliers.find(s => s.id === id)).filter(Boolean);

  const addSlot = () => {
    if (selected.length >= 4) return;
    const available = allSuppliers.find(s => !selected.includes(s.id));
    if (available) setSelected([...selected, available.id]);
  };

  const removeSlot = (id) => {
    if (selected.length <= 2) return;
    setSelected(selected.filter(sid => sid !== id));
  };

  const changeSupplier = (index, newId) => {
    const next = [...selected];
    next[index] = newId;
    setSelected(next);
  };

  if (isLoading) {
    return <div className="max-w-7xl mx-auto px-4 py-12 text-muted-foreground">Loading comparison data...</div>;
  }

  if (error) {
    return <div className="max-w-7xl mx-auto px-4 py-12 text-red-700">{error.message}</div>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-foreground">Compare Suppliers</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Compare capabilities, certifications, and capacity side by side
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-border/50 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full">
            {/* Header with supplier cards */}
            <thead>
              <tr className="border-b border-border/50">
                <th className="w-48 p-4 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider bg-muted/20 sticky left-0 z-10">
                  Attribute
                </th>
                {suppliers.map((s, i) => (
                  <th key={s.id} className="p-4 min-w-[220px]">
                    <div className="text-left">
                      <div className="flex items-start justify-between mb-3">
                        <div className="w-12 h-12 rounded-xl bg-muted overflow-hidden flex items-center justify-center">
                          <Globe className="w-5 h-5 text-muted-foreground" />
                        </div>
                        <button
                          onClick={() => removeSlot(s.id)}
                          className="w-6 h-6 rounded-full bg-muted hover:bg-destructive/10 flex items-center justify-center transition-colors"
                        >
                          <X className="w-3 h-3 text-muted-foreground hover:text-destructive" />
                        </button>
                      </div>
                      <Select value={s.id} onValueChange={(val) => changeSupplier(i, val)}>
                        <SelectTrigger className="h-8 text-sm font-semibold border-0 p-0 shadow-none focus:ring-0">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {allSuppliers.map(sup => (
                            <SelectItem key={sup.id} value={sup.id}>
                              {sup.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <div className="flex items-center gap-1 mt-0.5 text-xs text-muted-foreground">
                        <MapPin className="w-3 h-3" /> {s.city}
                        {s.verified && <Shield className="w-3 h-3 text-emerald-500 ml-1" />}
                      </div>
                      <Link to={`/supplier/${s.slug}`}>
                        <Button variant="ghost" size="sm" className="mt-2 text-xs gap-1 p-0 h-auto">
                          View Profile <ArrowRight className="w-3 h-3" />
                        </Button>
                      </Link>
                    </div>
                  </th>
                ))}
                {selected.length < 4 && (
                  <th className="p-4 min-w-[180px]">
                    <button
                      onClick={addSlot}
                      className="w-full h-32 border-2 border-dashed border-border/60 rounded-xl flex flex-col items-center justify-center gap-2 text-muted-foreground hover:border-primary/30 hover:text-primary transition-colors"
                    >
                      <Plus className="w-5 h-5" />
                      <span className="text-xs font-medium">Add Supplier</span>
                    </button>
                  </th>
                )}
              </tr>
            </thead>

            {/* Comparison rows */}
            <tbody>
              {COMPARE_FIELDS.map((field, i) => (
                <tr key={field.key} className={`border-b border-border/30 ${i % 2 === 0 ? 'bg-muted/10' : ''}`}>
                  <td className="p-4 text-sm font-medium text-muted-foreground sticky left-0 z-10 bg-inherit">
                    {field.label}
                  </td>
                  {suppliers.map(s => (
                    <td key={s.id} className="p-4 text-sm">
                      {field.render(s)}
                    </td>
                  ))}
                  {selected.length < 4 && <td className="p-4" />}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
