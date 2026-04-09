import { Link } from 'react-router-dom';
import { Sparkles, MapPin, ArrowRight, CheckCircle, Zap, Globe, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

const EXAMPLES = [
  'I want to launch a premium organic olive oil for export',
  'I want a honey-based wellness product for supermarkets',
  'I want a private label Greek herb tea line',
  'I want a functional dairy snack for the EU market',
];

const STEPS = [
  { num: '01', icon: Sparkles, label: 'Describe your product', desc: 'Tell Foodbase what you want to create — in plain language.' },
  { num: '02', icon: Zap, label: 'AI refines it with you', desc: 'Answer a few quick questions or let AI Auto-Fill the details.' },
  { num: '03', icon: Package, label: 'Your product is ready', desc: 'Get a full product profile with specs, positioning, and packaging.' },
  { num: '04', icon: MapPin, label: 'Find your supplier team', desc: "Explore Greece's best producers on the map, or let AI assemble your team." },
];

const STATS = [
  { value: '2,400+', label: 'Greek producers' },
  { value: '180+', label: 'Product categories' },
  { value: '94%', label: 'Match accuracy' },
  { value: '12 days', label: 'Avg. time to sourcing' },
];

export default function Landing() {
  const [prompt, setPrompt] = useState('');

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="relative overflow-hidden pt-20 pb-28 px-4">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5 pointer-events-none" />
        <div className="max-w-4xl mx-auto text-center relative">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            <Sparkles className="w-3.5 h-3.5" />
            AI-powered food sourcing platform
          </div>
          <h1 className="font-display text-5xl sm:text-6xl md:text-7xl font-bold text-foreground leading-tight mb-6">
            From idea to<br />
            <span className="text-primary">Greek producer</span><br />
            in minutes.
          </h1>
          <p className="text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            Describe your food or CPG product. Foodbase uses AI to refine it, generate a full product profile, and connect you with the right producers and distributors across Greece.
          </p>

          {/* AI Input */}
          <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-border shadow-lg p-2 flex gap-2">
            <div className="flex-1 flex items-center gap-3 px-3">
              <Sparkles className="w-5 h-5 text-primary flex-shrink-0" />
              <input
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder="Describe your product idea..."
                className="flex-1 bg-transparent outline-none text-sm text-foreground placeholder:text-muted-foreground py-2"
              />
            </div>
            <Link to={`/create${prompt ? `?q=${encodeURIComponent(prompt)}` : ''}`}>
              <Button className="gap-2 rounded-xl px-5">
                Start <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </div>

          {/* Example prompts */}
          <div className="flex flex-wrap justify-center gap-2 mt-4">
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                onClick={() => setPrompt(ex)}
                className="text-xs text-muted-foreground bg-muted hover:bg-muted/80 px-3 py-1.5 rounded-full transition-colors hover:text-foreground"
              >
                {ex.slice(0, 42)}...
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border/50 bg-white py-8">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {STATS.map(s => (
            <div key={s.label}>
              <p className="font-display text-3xl font-bold text-primary">{s.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="font-display text-3xl sm:text-4xl font-bold text-foreground mb-3">How Foodbase works</h2>
            <p className="text-muted-foreground text-lg">Four steps from concept to sourcing partner.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {STEPS.map(step => (
              <div key={step.num} className="bg-white rounded-2xl border border-border/50 p-6 hover:shadow-md transition-shadow">
                <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                  <step.icon className="w-5 h-5 text-primary" />
                </div>
                <p className="text-xs font-semibold text-muted-foreground mb-1">{step.num}</p>
                <h3 className="font-semibold text-foreground mb-2">{step.label}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Auto-Fill highlight */}
      <section className="py-16 px-4 bg-primary/5">
        <div className="max-w-3xl mx-auto text-center">
          <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-5">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <h2 className="font-display text-3xl font-bold text-foreground mb-4">Don't know all the details?</h2>
          <p className="text-lg text-muted-foreground mb-6 leading-relaxed">
            Use <span className="font-semibold text-primary">AI Auto-Fill</span> — Foodbase intelligently fills in missing ingredients, packaging assumptions, and product specs based on your concept. Move fast, even when you don't have everything figured out.
          </p>
          <Link to="/create">
            <Button size="lg" className="gap-2">
              <Sparkles className="w-4 h-4" /> Try AI Auto-Fill
            </Button>
          </Link>
        </div>
      </section>

      {/* Map preview */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-accent/10 text-accent text-sm font-medium px-3 py-1 rounded-full mb-4">
                <Globe className="w-3.5 h-3.5" /> Greece-first sourcing
              </div>
              <h2 className="font-display text-3xl sm:text-4xl font-bold text-foreground mb-4">
                Explore 2,400+ producers on the map
              </h2>
              <p className="text-muted-foreground text-lg leading-relaxed mb-6">
                Our interactive Greece map lets you discover producers, manufacturers, and distributors by region. Or let AI assemble your entire supplier team automatically.
              </p>
              <div className="space-y-3 mb-8">
                {['Hover markers to preview suppliers', 'Filter by category, region, certification', 'Auto-pick your AI-curated supplier team'].map(f => (
                  <div key={f} className="flex items-center gap-2.5">
                    <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                    <span className="text-sm text-muted-foreground">{f}</span>
                  </div>
                ))}
              </div>
              <div className="flex gap-3 flex-wrap">
                <Link to="/discover"><Button className="gap-2">Explore the map <ArrowRight className="w-4 h-4" /></Button></Link>
                <Link to="/create"><Button variant="outline" className="gap-2"><Sparkles className="w-4 h-4" /> Auto-pick suppliers</Button></Link>
              </div>
            </div>
            <div className="bg-muted rounded-2xl overflow-hidden aspect-square flex items-center justify-center border border-border/50 relative">
              <img
                src="https://images.unsplash.com/photo-1527838832700-5059252407fa?w=600&q=80"
                alt="Greece map"
                className="w-full h-full object-cover opacity-60"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="bg-white/90 backdrop-blur rounded-2xl p-5 shadow-xl border border-border/50 text-center max-w-xs">
                  <MapPin className="w-8 h-8 text-primary mx-auto mb-2" />
                  <p className="font-semibold text-foreground">Interactive Greece Map</p>
                  <p className="text-xs text-muted-foreground mt-1">Producers, manufacturers & distributors</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 bg-primary text-primary-foreground">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="font-display text-4xl font-bold mb-4">Ready to source smarter?</h2>
          <p className="text-primary-foreground/80 text-lg mb-8">Start with your product idea. Foodbase does the rest.</p>
          <Link to="/create">
            <Button size="lg" variant="secondary" className="gap-2 text-primary font-semibold">
              <Sparkles className="w-4 h-4" /> Describe your product
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-8 px-4">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <span className="text-white text-[10px] font-bold">fb</span>
            </div>
            <span className="font-display font-bold text-foreground">Foodbase</span>
          </div>
          <p className="text-sm text-muted-foreground">© 2026 Foodbase. Greece-first food sourcing platform.</p>
          <div className="flex gap-4 text-sm text-muted-foreground">
            <a href="#" className="hover:text-foreground">Privacy</a>
            <a href="#" className="hover:text-foreground">Terms</a>
            <a href="#" className="hover:text-foreground">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
