import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, MapPin, ArrowRight, RefreshCw, CheckCircle, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiFetch } from '@/lib/api';
import { getCategoryImage, loadStoredProductProfile } from '@/lib/foodbase';

export default function SupplierTeam() {
  const location = useLocation();
  const [swapping, setSwapping] = useState(null);
  const [team, setTeam] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const productProfile = location.state?.productProfile || loadStoredProductProfile();

  useEffect(() => {
    if (!productProfile) {
      return;
    }

    let isMounted = true;
    setLoading(true);
    setError(null);

    apiFetch('/ai/supplier-team', {
      method: 'POST',
      body: JSON.stringify({
        product_profile: productProfile,
      }),
    })
      .then((response) => {
        if (!isMounted) return;
        setTeam(response);
      })
      .catch((requestError) => {
        if (!isMounted) return;
        setError(requestError.message);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [productProfile]);

  if (!productProfile) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <h1 className="font-display text-4xl font-bold text-foreground">No product brief yet</h1>
        <p className="text-muted-foreground mt-3">
          Generate a product profile first so Foodbase can match suppliers from the live database.
        </p>
        <Link to="/create">
          <Button className="mt-6">Create a Product Brief</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 bg-primary/10 text-primary text-sm font-semibold px-4 py-2 rounded-full mb-5">
          <Sparkles className="w-4 h-4" /> AI-curated supplier team
        </div>
        <h1 className="font-display text-4xl sm:text-5xl font-bold text-foreground mb-3">
          Your recommended<br />supplier team
        </h1>
        <p className="text-muted-foreground text-lg max-w-xl mx-auto">
          We assembled the best-fit shortlist available in the current Foodbase pilot database for your product concept.
        </p>
      </div>

      {/* Score summary */}
      {loading ? (
        <div className="bg-white border border-border rounded-2xl p-8 text-center text-muted-foreground mb-8">
          Matching suppliers from the live database...
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-red-700 mb-8">
          {error}
        </div>
      ) : team && (
      <div className="bg-white border border-border rounded-2xl p-5 flex flex-wrap gap-6 justify-around mb-8">
        <div className="text-center">
          <p className="font-display text-3xl font-bold text-primary">{team.average_fit_score}</p>
          <p className="text-xs text-muted-foreground">Avg. Team Fit Score</p>
        </div>
        <div className="text-center">
          <p className="font-display text-3xl font-bold text-emerald-600">{team.suppliers.length}</p>
          <p className="text-xs text-muted-foreground">Suppliers Selected</p>
        </div>
        <div className="text-center">
          <p className="font-display text-3xl font-bold text-foreground">
            {team.suppliers.filter((supplier) => supplier.verified).length}/{team.suppliers.length}
          </p>
          <p className="text-xs text-muted-foreground">Verified Suppliers</p>
        </div>
        <div className="text-center">
          <p className="font-display text-3xl font-bold text-foreground">{team.estimated_lead_time}</p>
          <p className="text-xs text-muted-foreground">Est. Lead Time</p>
        </div>
      </div>
      )}

      {team && (
        <div className="bg-primary/5 border border-primary/15 rounded-2xl p-5 text-sm text-foreground mb-8">
          <p className="font-medium">{team.summary}</p>
          <p className="text-muted-foreground mt-2">{team.dataset_note}</p>
        </div>
      )}

      {/* Team list */}
      <div className="space-y-4 mb-10">
        {team?.suppliers.map((supplier, idx) => (
          <div key={supplier.name} className="bg-white border border-border rounded-2xl overflow-hidden hover:shadow-md transition-shadow">
            <div className="flex gap-4 p-5">
              <div className="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0">
                <img src={getCategoryImage(productProfile.category_slug)} alt={supplier.name} className="w-full h-full object-cover" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3 flex-wrap">
                  <div>
                    <Badge variant="secondary" className="text-[10px] mb-1">{supplier.role}</Badge>
                    <h3 className="font-semibold text-foreground flex items-center gap-2">
                      {supplier.name}
                      {supplier.verified && <Shield className="w-3.5 h-3.5 text-emerald-500" />}
                    </h3>
                    <div className="flex items-center gap-1 mt-0.5">
                      <MapPin className="w-3 h-3 text-muted-foreground" />
                      <span className="text-xs text-muted-foreground">{supplier.city}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-center">
                      <p className="text-lg font-bold text-primary">{supplier.fit_score}%</p>
                      <p className="text-[9px] text-muted-foreground">FIT SCORE</p>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">{supplier.reason}</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {supplier.certifications.map(c => (
                    <Badge key={c} variant="outline" className="text-[10px] px-1.5 py-0 h-5">{c}</Badge>
                  ))}
                </div>
              </div>
            </div>
            <div className="border-t border-border/50 px-5 py-3 flex items-center justify-between bg-muted/20">
              <Link to={`/supplier/${supplier.slug}`} className="text-xs text-primary font-medium hover:underline flex items-center gap-1">
                View profile <ArrowRight className="w-3 h-3" />
              </Link>
              <button
                onClick={() => setSwapping(swapping === idx ? null : idx)}
                className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Replace supplier
              </button>
            </div>
            {swapping === idx && (
              <div className="px-5 pb-4 bg-muted/20 text-sm text-muted-foreground italic">
                Swap functionality — browse alternative suppliers from the <Link to="/discover" className="text-primary underline">discovery page</Link>.
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button size="lg" className="flex-1 gap-2">
          <CheckCircle className="w-4 h-4" /> Shortlist this team
        </Button>
        <Link to="/discover" className="flex-1">
          <Button variant="outline" size="lg" className="w-full gap-2">
            <MapPin className="w-4 h-4" /> Explore the map instead
          </Button>
        </Link>
      </div>
    </div>
  );
}
