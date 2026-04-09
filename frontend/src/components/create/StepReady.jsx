import { Link } from 'react-router-dom';
import { useState } from 'react';
import { Sparkles, ArrowRight, Users, TrendingUp, Globe, MapPin } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { productProfileImage } from '@/lib/foodbase';

export default function StepReady({ productData }) {
  const [tab, setTab] = useState('overview');
  const product = productData.generatedProfile || productData.productProfile;

  if (!product) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <h1 className="font-display text-3xl font-bold text-foreground">No product profile yet</h1>
        <p className="text-muted-foreground mt-3">Generate a product concept first.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Headline */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center gap-2 bg-emerald-100 text-emerald-700 text-sm font-semibold px-4 py-2 rounded-full mb-5">
          <Sparkles className="w-4 h-4" /> Product generated
        </div>
        <h1 className="font-display text-5xl sm:text-6xl font-bold text-foreground tracking-tight mb-3">
          YOUR PRODUCT<br /><span className="text-primary">IS READY</span>
        </h1>
        <p className="text-muted-foreground text-lg">Foodbase AI built your complete product profile. Review it below and start sourcing.</p>
      </div>

      {/* Product card */}
      <div className="bg-white rounded-3xl border border-border shadow-xl overflow-hidden mb-8">
        <div className="grid md:grid-cols-2">
          {/* Image */}
          <div className="relative h-64 md:h-auto overflow-hidden">
            <img src={productProfileImage(product)} alt={product.name} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
            <div className="absolute bottom-4 left-4 flex gap-2 flex-wrap">
              {product.certifications.map(c => (
                <span key={c} className="text-[10px] bg-white/90 text-foreground px-2 py-0.5 rounded-full font-medium">{c}</span>
              ))}
            </div>
            {/* Readiness score */}
            <div className="absolute top-4 right-4 bg-white rounded-xl px-3 py-2 text-center shadow-lg">
              <p className="text-2xl font-bold text-emerald-600">{product.readiness_score}</p>
              <p className="text-[9px] text-muted-foreground font-medium">READINESS</p>
            </div>
          </div>

          {/* Info */}
          <div className="p-6 md:p-8">
            <Badge variant="secondary" className="mb-3 text-xs">{product.category_label} — {product.subcategory}</Badge>
            <h2 className="font-display text-2xl font-bold text-foreground mb-2">{product.name}</h2>
            <p className="text-sm text-muted-foreground leading-relaxed mb-5">{product.description}</p>

            <div className="grid grid-cols-2 gap-3 mb-5">
              <div className="bg-muted/50 rounded-xl p-3">
                <p className="text-[10px] text-muted-foreground font-medium mb-0.5">PRICE TIER</p>
                <p className="text-sm font-semibold text-foreground">{product.price_tier}</p>
              </div>
              <div className="bg-muted/50 rounded-xl p-3">
                <p className="text-[10px] text-muted-foreground font-medium mb-0.5">SALES ESTIMATE</p>
                <p className="text-sm font-semibold text-emerald-700">{product.sales_estimate}</p>
              </div>
              <div className="bg-muted/50 rounded-xl p-3">
                <p className="text-[10px] text-muted-foreground font-medium mb-0.5">MIN. ORDER</p>
                <p className="text-sm font-semibold text-foreground">{product.moq}</p>
              </div>
              <div className="bg-muted/50 rounded-xl p-3">
                <p className="text-[10px] text-muted-foreground font-medium mb-0.5">LEAD TIME</p>
                <p className="text-sm font-semibold text-foreground">{product.lead_time}</p>
              </div>
            </div>

            <p className="text-xs text-muted-foreground italic bg-muted/30 rounded-xl p-3 leading-relaxed">
              <span className="font-medium text-foreground">AI Rationale:</span> {product.rationale}
            </p>
          </div>
        </div>

        {/* Details tabs */}
        <div className="border-t border-border">
          <div className="flex gap-0 border-b border-border">
            {['overview', 'ingredients', 'market'].map(t => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-5 py-3 text-sm font-medium capitalize transition-colors ${tab === t ? 'text-primary border-b-2 border-primary' : 'text-muted-foreground hover:text-foreground'}`}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="p-6">
            {tab === 'overview' && (
              <div className="grid sm:grid-cols-2 gap-4 text-sm">
                <div><p className="text-muted-foreground text-xs font-medium mb-1">PACKAGING</p><p>{product.packaging}</p></div>
                <div><p className="text-muted-foreground text-xs font-medium mb-1">POSITIONING</p><p>{product.positioning.join(' · ')}</p></div>
                <div><p className="text-muted-foreground text-xs font-medium mb-1">TARGET AUDIENCE</p><p>{product.target_audience.join(', ')}</p></div>
                <div><p className="text-muted-foreground text-xs font-medium mb-1">CHANNELS</p><p>{product.channels.join(', ')}</p></div>
              </div>
            )}
            {tab === 'ingredients' && (
              <ul className="space-y-2">
                {product.ingredients.map(i => (
                  <li key={i} className="flex items-center gap-2 text-sm"><span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />{i}</li>
                ))}
              </ul>
            )}
            {tab === 'market' && (
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-2"><TrendingUp className="w-4 h-4 text-primary" /><span>Year 1 estimate: <strong>{product.sales_estimate}</strong></span></div>
                <div className="flex items-center gap-2"><Globe className="w-4 h-4 text-primary" /><span>Primary channels: {product.channels.join(', ')}</span></div>
                <div className="flex items-center gap-2"><Users className="w-4 h-4 text-primary" /><span>Audience: {product.target_audience.join(', ')}</span></div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Next: sourcing CTAs */}
      <div className="text-center mb-6">
        <h3 className="font-semibold text-foreground text-lg mb-1">Choose how to find your partners</h3>
        <p className="text-muted-foreground text-sm">Explore Greece's producers manually, or let AI assemble your ideal supplier team.</p>
      </div>
      <div className="grid sm:grid-cols-2 gap-4">
        <Link to="/discover">
          <div className="bg-white border border-border rounded-2xl p-6 hover:shadow-md transition-all hover:border-primary/40 cursor-pointer group">
            <MapPin className="w-8 h-8 text-primary mb-3" />
            <h4 className="font-semibold text-foreground mb-1">Explore the map</h4>
            <p className="text-sm text-muted-foreground">Browse producers, manufacturers, and distributors across Greece interactively.</p>
            <div className="flex items-center gap-1 text-primary text-sm font-medium mt-3">Explore manually <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" /></div>
          </div>
        </Link>
        <Link to="/supplier-team" state={{ productProfile: product }}>
          <div className="bg-primary text-primary-foreground rounded-2xl p-6 hover:bg-primary/95 transition-all cursor-pointer group shadow-lg shadow-primary/20">
            <Sparkles className="w-8 h-8 text-primary-foreground/90 mb-3" />
            <h4 className="font-semibold mb-1">Auto-pick my suppliers</h4>
            <p className="text-sm text-primary-foreground/80">Let AI assemble the perfect production and distribution team for your product.</p>
            <div className="flex items-center gap-1 text-sm font-medium mt-3 text-primary-foreground/90">Get my AI team <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" /></div>
          </div>
        </Link>
      </div>
    </div>
  );
}
