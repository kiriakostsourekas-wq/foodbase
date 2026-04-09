import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { MapPin, Shield, Clock, Package, Globe, Users, Heart, Share2, MessageCircle, ArrowLeft, ChevronRight, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CertBadge from '@/components/CertBadge';
import InquiryModal from '@/components/InquiryModal';
import { apiFetch } from '@/lib/api';
import { mapOrganizationDetail } from '@/lib/foodbase';

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-xl bg-white border border-border/50">
      <div className="w-10 h-10 rounded-lg bg-primary/5 flex items-center justify-center flex-shrink-0">
        <Icon className="w-5 h-5 text-primary" />
      </div>
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-semibold text-foreground">{value}</p>
      </div>
    </div>
  );
}

export default function SupplierProfile() {
  const { slug } = useParams();
  const [inquiryOpen, setInquiryOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const { data, isLoading, error } = useQuery({
    queryKey: ['organization', slug],
    queryFn: async () => mapOrganizationDetail(await apiFetch(`/organizations/${slug}`)),
    enabled: Boolean(slug),
  });

  const supplier = data;

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center text-muted-foreground">
        Loading supplier profile...
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-lg font-medium">We could not load this supplier.</p>
        <p className="text-sm text-muted-foreground mt-2">{error.message}</p>
        <Link to="/discover">
          <Button className="mt-4">Back to Discover</Button>
        </Link>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-lg font-medium">Supplier not found</p>
        <Link to="/discover">
          <Button className="mt-4">Back to Discover</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Breadcrumbs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Link to="/discover" className="hover:text-foreground transition-colors flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" /> Suppliers
          </Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-foreground font-medium">{supplier.name}</span>
        </div>
      </div>

      {/* Hero */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div className="bg-white rounded-2xl border border-border/50 overflow-hidden shadow-sm">
          <div className="h-48 sm:h-64 relative">
            <img src={supplier.heroImage} alt="" className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
          </div>
          <div className="p-6 sm:p-8 -mt-12 relative">
            <div className="flex flex-col sm:flex-row items-start gap-4">
              <div className="w-20 h-20 rounded-2xl bg-white border-4 border-white shadow-lg overflow-hidden flex-shrink-0">
                <img src={supplier.logo} alt="" className="w-full h-full object-cover" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
                  <h1 className="text-2xl font-display font-bold text-foreground">{supplier.name}</h1>
                  <div className="flex items-center gap-2">
                    {supplier.verified && (
                      <Badge className="bg-emerald-50 text-emerald-700 border-emerald-200 gap-1">
                        <Shield className="w-3 h-3" /> Verified Supplier
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" /> {supplier.city}, {supplier.region}
                  </span>
                  <span className="flex items-center gap-1">
                    <Globe className="w-4 h-4" /> Est. {supplier.yearFounded}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" /> {supplier.employees}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSaved(!saved)}
                  className={saved ? 'text-red-500 border-red-200' : ''}
                >
                  <Heart className={`w-4 h-4 mr-1.5 ${saved ? 'fill-red-500' : ''}`} />
                  {saved ? 'Saved' : 'Save'}
                </Button>
                <Button variant="outline" size="sm">
                  <Share2 className="w-4 h-4 mr-1.5" /> Share
                </Button>
                <Button size="sm" onClick={() => setInquiryOpen(true)}>
                  <MessageCircle className="w-4 h-4 mr-1.5" /> Send Inquiry
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList className="bg-white border border-border/50 p-1 rounded-xl">
                <TabsTrigger value="overview" className="rounded-lg text-sm">Overview</TabsTrigger>
                <TabsTrigger value="products" className="rounded-lg text-sm">Products</TabsTrigger>
                <TabsTrigger value="sources" className="rounded-lg text-sm">Sources</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div className="bg-white rounded-2xl border border-border/50 p-6">
                  <h2 className="font-semibold text-lg mb-3">About</h2>
                  <p className="text-sm text-muted-foreground leading-relaxed">{supplier.description}</p>
                </div>

                <div className="grid sm:grid-cols-2 gap-3">
                  <StatCard icon={Package} label="Minimum Order" value={supplier.moq} />
                  <StatCard icon={Clock} label="Lead Time" value={supplier.leadTime} />
                  <StatCard icon={Globe} label="Capacity" value={supplier.capacity} />
                  <StatCard icon={Globe} label="Export Markets" value={supplier.exportMarkets.length || 'Not disclosed'} />
                </div>

                <div className="bg-white rounded-2xl border border-border/50 p-6">
                  <h2 className="font-semibold text-lg mb-3">Certifications</h2>
                  <div className="flex flex-wrap gap-2">
                    {supplier.certifications.map(cert => (
                      <CertBadge key={cert} cert={cert} size="md" />
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-2xl border border-border/50 p-6">
                  <h2 className="font-semibold text-lg mb-3">Export Markets</h2>
                  {supplier.exportMarkets.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {supplier.exportMarkets.map(market => (
                        <Badge key={market} variant="outline" className="text-xs">{market}</Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">Export markets have not been disclosed yet.</p>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="products" className="space-y-4">
                <div className="bg-white rounded-2xl border border-border/50 p-6">
                  <h2 className="font-semibold text-lg mb-4">Products & Capabilities</h2>
                  <div className="grid sm:grid-cols-2 gap-3">
                    {supplier.products.map(product => (
                      <div key={product} className="p-4 rounded-xl bg-muted/30 border border-border/30">
                        <p className="font-medium text-sm">{product}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-white rounded-2xl border border-border/50 p-6">
                  <h2 className="font-semibold text-lg mb-4">Packaging Options</h2>
                  {supplier.packagingOptions.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {supplier.packagingOptions.map(opt => (
                        <Badge key={opt} variant="secondary" className="text-xs">{opt}</Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">Packaging options have not been disclosed yet.</p>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="sources">
                <div className="bg-white rounded-2xl border border-border/50 p-6">
                  <h2 className="font-semibold text-lg mb-4">Source Evidence</h2>
                  <div className="space-y-3">
                    {supplier.sources.map((source) => (
                      <a
                        key={source.url}
                        href={source.url}
                        target="_blank"
                        rel="noreferrer"
                        className="block rounded-xl border border-border/50 p-4 hover:border-primary/40 hover:bg-muted/20 transition-colors"
                      >
                        <div className="flex items-center justify-between gap-4">
                          <div>
                            <p className="font-medium text-sm text-foreground">{source.title || source.url}</p>
                            <p className="text-xs text-muted-foreground mt-1">{source.source_type}</p>
                            {source.notes && <p className="text-sm text-muted-foreground mt-2">{source.notes}</p>}
                          </div>
                          <ExternalLink className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-border/50 p-6 sticky top-20">
              <h3 className="font-semibold mb-4">Quick Facts</h3>
              <div className="space-y-3">
                {[
                  ['Category', supplier.subcategory],
                  ['Private Label', supplier.privateLabel ? 'Available' : 'Not available'],
                  ['Export Ready', supplier.exportReady ? 'Yes' : 'No'],
                  ['Organic', supplier.organic ? 'Yes' : 'No'],
                  ['Founded', supplier.yearFounded || 'Undisclosed'],
                  ['Company Size', supplier.employees],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between text-sm">
                    <span className="text-muted-foreground">{label}</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>

              <Button className="w-full mt-6" onClick={() => setInquiryOpen(true)}>
                <MessageCircle className="w-4 h-4 mr-2" /> Send Inquiry
              </Button>
              <Button variant="outline" className="w-full mt-2">
                <Heart className="w-4 h-4 mr-2" /> Add to Shortlist
              </Button>
            </div>
          </div>
        </div>
      </div>

      <InquiryModal open={inquiryOpen} onOpenChange={setInquiryOpen} supplier={supplier} />
    </div>
  );
}
