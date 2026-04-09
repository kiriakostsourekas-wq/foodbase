import { Star, MapPin, Shield, ArrowRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function MapPopupContent({ supplier }) {
  return (
    <div className="w-[280px]">
      {/* Image */}
      <div className="h-28 relative overflow-hidden">
        <img src={supplier.heroImage} alt="" className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <div className="absolute bottom-2 left-3 right-3 flex items-end justify-between">
          <div>
            <h3 className="text-white font-semibold text-sm leading-tight">{supplier.name}</h3>
            <div className="flex items-center gap-1 mt-0.5">
              <MapPin className="w-3 h-3 text-white/80" />
              <span className="text-white/80 text-xs">{supplier.city}</span>
            </div>
          </div>
          <div className="flex items-center gap-1 bg-white/90 backdrop-blur-sm px-1.5 py-0.5 rounded-md">
            <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
            <span className="text-xs font-bold">{supplier.rating}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-3">
        <p className="text-xs text-muted-foreground line-clamp-2">{supplier.shortDescription}</p>
        
        <div className="flex flex-wrap gap-1 mt-2">
          {supplier.verified && (
            <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[10px] px-1.5 py-0 h-4 gap-0.5">
              <Shield className="w-2.5 h-2.5" /> Verified
            </Badge>
          )}
          {supplier.certifications.slice(0, 2).map(cert => (
            <Badge key={cert} variant="outline" className="text-[10px] px-1.5 py-0 h-4">
              {cert}
            </Badge>
          ))}
        </div>

        <div className="grid grid-cols-3 gap-2 mt-2 pt-2 border-t border-border/40 text-center">
          <div>
            <p className="text-[10px] text-muted-foreground">MOQ</p>
            <p className="text-[11px] font-medium">{supplier.moq}</p>
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground">Lead</p>
            <p className="text-[11px] font-medium">{supplier.leadTime}</p>
          </div>
          <div>
            <p className="text-[10px] text-muted-foreground">Response</p>
            <p className="text-[11px] font-medium">{supplier.responseRate}%</p>
          </div>
        </div>

        <a
          href={`/supplier/${supplier.slug}`}
          className="flex items-center justify-center gap-1 w-full mt-2.5 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors"
        >
          View Profile <ArrowRight className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
}