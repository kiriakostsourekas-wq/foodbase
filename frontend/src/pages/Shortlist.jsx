import { Heart, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import SupplierCard from '@/components/SupplierCard';
import { SUPPLIERS } from '@/lib/mockData';

export default function Shortlist() {
  // Mock: show first 3 as "saved"
  const savedSuppliers = SUPPLIERS.slice(0, 3);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="font-display text-2xl font-bold text-foreground">Your Shortlist</h1>
        <p className="text-muted-foreground text-sm mt-1">
          {savedSuppliers.length} saved supplier{savedSuppliers.length !== 1 ? 's' : ''}
        </p>
      </div>

      {savedSuppliers.length === 0 ? (
        <div className="text-center py-24">
          <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mx-auto mb-6">
            <Heart className="w-9 h-9 text-muted-foreground" />
          </div>
          <h2 className="text-xl font-semibold text-foreground">No saved suppliers yet</h2>
          <p className="text-sm text-muted-foreground mt-2 max-w-md mx-auto">
            Browse suppliers and click the heart icon to save them to your shortlist for easy comparison later.
          </p>
          <Link to="/discover">
            <Button className="mt-6 gap-2">
              Discover Suppliers <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {savedSuppliers.map(supplier => (
            <SupplierCard key={supplier.id} supplier={supplier} />
          ))}
        </div>
      )}
    </div>
  );
}