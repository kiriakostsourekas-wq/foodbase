import { Globe, MapPin, Shield, Clock, Package, ArrowRight, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { getSupplierImageUrl } from '@/lib/foodbase';

export default function SupplierCard({ supplier, onHover, onLeave, isHighlighted, compact = false }) {
  const [saved, setSaved] = useState(false);
  const heroImage = getSupplierImageUrl(supplier, 'hero');
  const logoImage = getSupplierImageUrl(supplier, 'logo');
  const marketsLabel = supplier.exportMarkets?.length
    ? `${supplier.exportMarkets.length} mkts`
    : 'N/A';

  if (compact) {
    return (
      <div
        onMouseEnter={() => onHover?.(supplier.id)}
        onMouseLeave={() => onLeave?.()}
        className={`group p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
          isHighlighted
            ? 'border-primary/40 bg-primary/5 shadow-md ring-1 ring-primary/20'
            : 'border-border/50 bg-white hover:shadow-md hover:border-border'
        }`}
      >
        <div className="flex gap-3">
          <div className="w-12 h-12 rounded-lg bg-muted overflow-hidden flex-shrink-0">
            <img src={logoImage} alt="" className="w-full h-full object-cover" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <h3 className="font-semibold text-sm text-foreground truncate">{supplier.name}</h3>
              {supplier.verified && (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-5 gap-1 bg-emerald-50 text-emerald-700 border-emerald-200">
                  <Shield className="w-2.5 h-2.5" /> Verified
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-1 mt-0.5">
              <MapPin className="w-3 h-3 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">{supplier.city}, {supplier.region}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{supplier.shortDescription}</p>
            <div className="flex items-center gap-1.5 mt-2 flex-wrap">
              {supplier.organic && (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-5 bg-green-50 text-green-700 border-green-200">
                  Organic
                </Badge>
              )}
              {supplier.privateLabel && (
                <Badge variant="secondary" className="text-[10px] px-1.5 py-0 h-5">
                  Private Label
                </Badge>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      onMouseEnter={() => onHover?.(supplier.id)}
      onMouseLeave={() => onLeave?.()}
      className={`group bg-white rounded-2xl border overflow-hidden transition-all duration-300 ${
        isHighlighted
          ? 'border-primary/40 shadow-lg ring-1 ring-primary/20 scale-[1.01]'
          : 'border-border/50 hover:shadow-lg hover:border-border hover:scale-[1.005]'
      }`}
    >
      {/* Image */}
      <div className="relative h-40 overflow-hidden">
        <img
          src={heroImage}
          alt={supplier.name}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
        <button
          onClick={(e) => { e.preventDefault(); setSaved(!saved); }}
          className="absolute top-3 right-3 w-8 h-8 rounded-full bg-white/90 backdrop-blur-sm flex items-center justify-center transition-transform hover:scale-110"
        >
          <Heart className={`w-4 h-4 ${saved ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} />
        </button>
        <div className="absolute bottom-3 left-3 flex items-center gap-1.5">
          {supplier.verified && (
            <Badge className="bg-emerald-500/90 text-white text-[10px] gap-1 backdrop-blur-sm border-0">
              <Shield className="w-3 h-3" /> Verified
            </Badge>
          )}
          {supplier.exportReady && (
            <Badge className="bg-blue-500/90 text-white text-[10px] backdrop-blur-sm border-0">
              Export Ready
            </Badge>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors">
              {supplier.name}
            </h3>
            <div className="flex items-center gap-1.5 mt-1">
              <MapPin className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">{supplier.city}, {supplier.region}</span>
            </div>
          </div>
          {supplier.verified && (
            <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200">
              Verified
            </Badge>
          )}
        </div>

        <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{supplier.shortDescription}</p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-border/50">
          <div className="text-center">
            <Package className="w-3.5 h-3.5 mx-auto text-muted-foreground mb-0.5" />
            <p className="text-[10px] text-muted-foreground">MOQ</p>
            <p className="text-xs font-medium">{supplier.moq}</p>
          </div>
          <div className="text-center">
            <Clock className="w-3.5 h-3.5 mx-auto text-muted-foreground mb-0.5" />
            <p className="text-[10px] text-muted-foreground">Lead Time</p>
            <p className="text-xs font-medium">{supplier.leadTime}</p>
          </div>
          <div className="text-center">
            <Globe className="w-3.5 h-3.5 mx-auto text-muted-foreground mb-0.5" />
            <p className="text-[10px] text-muted-foreground">Markets</p>
            <p className="text-xs font-medium">{marketsLabel}</p>
          </div>
        </div>

        {/* Certifications */}
        <div className="flex flex-wrap gap-1 mt-3">
          {supplier.certifications.slice(0, 3).map(cert => (
            <Badge key={cert} variant="outline" className="text-[10px] px-1.5 py-0 h-5 font-normal">
              {cert}
            </Badge>
          ))}
          {supplier.certifications.length > 3 && (
            <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-5 font-normal">
              +{supplier.certifications.length - 3}
            </Badge>
          )}
        </div>

        {/* CTA */}
        <Link to={`/supplier/${supplier.slug}`}>
          <Button variant="ghost" size="sm" className="w-full mt-3 text-sm gap-1 group/btn">
            View Profile
            <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
