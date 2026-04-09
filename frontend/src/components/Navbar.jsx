import { Link, useLocation } from 'react-router-dom';
import { Search, Heart, BarChart3, Menu, X, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

export default function Navbar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-xl border-b border-border/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-primary flex items-center justify-center">
              <span className="text-white font-bold text-xs">fb</span>
            </div>
            <span className="font-display text-xl font-bold text-foreground tracking-tight">Foodbase</span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            <Link to="/create">
              <Button variant={isActive('/create') ? 'secondary' : 'ghost'} size="sm" className="text-sm font-medium gap-2">
                <Sparkles className="w-3.5 h-3.5" /> Create Product
              </Button>
            </Link>
            <Link to="/discover">
              <Button variant={isActive('/discover') ? 'secondary' : 'ghost'} size="sm" className="text-sm font-medium gap-2">
                <Search className="w-3.5 h-3.5" /> Discover
              </Button>
            </Link>
            <Link to="/compare">
              <Button variant={isActive('/compare') ? 'secondary' : 'ghost'} size="sm" className="text-sm font-medium gap-2">
                <BarChart3 className="w-3.5 h-3.5" /> Compare
              </Button>
            </Link>
            <Link to="/shortlist">
              <Button variant={isActive('/shortlist') ? 'secondary' : 'ghost'} size="sm" className="text-sm font-medium gap-2">
                <Heart className="w-3.5 h-3.5" /> Shortlist
              </Button>
            </Link>
          </div>

          {/* Actions */}
          <div className="hidden md:flex items-center gap-3">
            <Button variant="ghost" size="sm" className="text-sm">Log in</Button>
            <Link to="/create">
              <Button size="sm" className="text-sm bg-primary hover:bg-primary/90 gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Start Creating
              </Button>
            </Link>
          </div>

          {/* Mobile */}
          <button className="md:hidden p-2" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile nav */}
        {mobileOpen && (
          <div className="md:hidden pb-4 space-y-2">
            <Link to="/create" className="block" onClick={() => setMobileOpen(false)}>
              <Button variant="ghost" className="w-full justify-start gap-2"><Sparkles className="w-4 h-4" /> Create Product</Button>
            </Link>
            <Link to="/discover" className="block" onClick={() => setMobileOpen(false)}>
              <Button variant="ghost" className="w-full justify-start gap-2"><Search className="w-4 h-4" /> Discover Suppliers</Button>
            </Link>
            <Link to="/compare" className="block" onClick={() => setMobileOpen(false)}>
              <Button variant="ghost" className="w-full justify-start gap-2"><BarChart3 className="w-4 h-4" /> Compare</Button>
            </Link>
            <Link to="/shortlist" className="block" onClick={() => setMobileOpen(false)}>
              <Button variant="ghost" className="w-full justify-start gap-2"><Heart className="w-4 h-4" /> Shortlist</Button>
            </Link>
            <div className="pt-2 border-t space-y-2">
              <Button variant="outline" className="w-full">Log in</Button>
              <Link to="/create" className="block"><Button className="w-full">Start Creating</Button></Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}