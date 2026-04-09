const CATEGORY_IMAGES = {
  'olive-oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=1000&q=80',
  honey: 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=1000&q=80',
  dairy: 'https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?w=1000&q=80',
  packaging: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1000&q=80',
  default: 'https://images.unsplash.com/photo-1510186760950-5f17e436600d?w=1000&q=80',
};

const STORAGE_KEY = 'foodbase:last-product-profile';

function dedupe(values) {
  return [...new Set(values.filter(Boolean))];
}

function primaryOffering(record) {
  if (record.offerings?.length) {
    return record.offerings[0];
  }
  return null;
}

export function getCategoryImage(categorySlug) {
  return CATEGORY_IMAGES[categorySlug] || CATEGORY_IMAGES.default;
}

export function getSupplierImageUrl(supplier, variant = 'hero') {
  if (variant === 'logo' && supplier.logo) {
    return supplier.logo;
  }
  if (variant === 'hero' && supplier.heroImage) {
    return supplier.heroImage;
  }
  return getCategoryImage(supplier.category);
}

export function mapOrganizationListItem(item) {
  return {
    id: String(item.id),
    rawId: item.id,
    slug: item.slug,
    name: item.name,
    city: item.city || 'Unknown city',
    region: item.region || 'Unknown region',
    lat: item.lat,
    lng: item.lng,
    category: item.category,
    subcategory: item.subcategory || item.category_label || 'Supplier',
    description: item.description || '',
    shortDescription: item.short_description || item.description || '',
    certifications: item.certifications || [],
    moq: item.moq || 'On request',
    capacity: item.capacity || 'On request',
    leadTime: item.lead_time || 'On request',
    exportReady: Boolean(item.export_ready),
    privateLabel: Boolean(item.private_label),
    organic: Boolean(item.organic),
    verified: Boolean(item.verified),
    responseRate: null,
    responseTime: null,
    pricingTier: null,
    sustainabilityScore: null,
    yearFounded: item.year_founded || null,
    employees: item.employees || 'Undisclosed',
    exportMarkets: item.export_markets || [],
    rating: null,
    reviewCount: null,
    logo: getCategoryImage(item.category),
    heroImage: getCategoryImage(item.category),
  };
}

export function mapOrganizationDetail(detail) {
  const offering = primaryOffering(detail);
  const products = dedupe(
    (detail.offerings || []).map((item) =>
      item.variety_or_cultivar
        ? `${item.subcategory || item.name} (${item.variety_or_cultivar})`
        : item.subcategory || item.name
    )
  );
  const packagingOptions = dedupe(
    (detail.offerings || []).flatMap((item) => item.packaging_formats || [])
  );
  const certifications = dedupe((detail.certifications || []).map((item) => item.name));

  return {
    id: String(detail.id),
    rawId: detail.id,
    slug: detail.slug,
    name: detail.name,
    legalName: detail.legal_name,
    city: detail.city || 'Unknown city',
    region: detail.region || 'Unknown region',
    lat: detail.lat,
    lng: detail.lng,
    category: offering?.category || null,
    subcategory: offering?.subcategory || offering?.category_label || 'Supplier',
    description: detail.summary || '',
    shortDescription: detail.summary || '',
    certifications,
    moq: detail.moq || 'On request',
    capacity: detail.capacity || 'On request',
    leadTime: detail.lead_time || 'On request',
    exportReady: Boolean(detail.export_ready),
    privateLabel: Boolean(detail.private_label),
    organic: Boolean(detail.organic),
    verified: Boolean(detail.verified),
    yearFounded: detail.year_founded || null,
    employees: detail.employees || 'Undisclosed',
    exportMarkets: detail.export_markets || [],
    products,
    packagingOptions,
    facilities: detail.facilities || [],
    contacts: detail.contacts || [],
    sources: detail.sources || [],
    offerings: detail.offerings || [],
    capacityRecords: detail.capacity_records || [],
    geographicalIndications: detail.geographical_indications || [],
    logo: detail.logo_url || getCategoryImage(offering?.category),
    heroImage: detail.hero_image_url || getCategoryImage(offering?.category),
    gallery: detail.gallery_urls?.length ? detail.gallery_urls : [getCategoryImage(offering?.category)],
    rating: detail.rating ?? null,
    reviewCount: detail.review_count ?? null,
    responseRate: detail.response_rate ?? null,
    responseTime: detail.response_time || null,
    pricingTier: detail.pricing_tier || null,
    sustainabilityScore: detail.sustainability_score ?? null,
    websiteUrl: detail.website_url || null,
    supportedLanguages: detail.supported_languages || [],
  };
}

export function mapFacetOptions(facets) {
  return {
    categories: (facets?.categories || []).map((option) => ({
      value: option.value,
      label: option.label,
      count: option.count,
    })),
    regions: (facets?.regions || []).map((option) => ({
      value: option.value,
      label: option.label,
      count: option.count,
    })),
    certifications: (facets?.certifications || []).map((option) => ({
      value: option.value,
      label: option.label,
      count: option.count,
    })),
  };
}

export function productProfileImage(productProfile) {
  return getCategoryImage(productProfile?.category_slug);
}

export function storeProductProfile(productProfile) {
  window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(productProfile));
}

export function loadStoredProductProfile() {
  const rawValue = window.sessionStorage.getItem(STORAGE_KEY);
  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue);
  } catch {
    return null;
  }
}
