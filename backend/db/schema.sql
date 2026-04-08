begin;

create extension if not exists pg_trgm;

create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table organizations (
  id bigint generated always as identity primary key,
  slug text not null unique,
  legal_name text,
  display_name text not null,
  vat_number text,
  company_registration_number text,
  organization_type text not null check (
    organization_type in (
      'producer',
      'manufacturer',
      'processor',
      'packaging_supplier',
      'logistics_provider',
      'mixed'
    )
  ),
  founded_year integer check (
    founded_year is null or founded_year between 1800 and 2100
  ),
  ownership_model text check (
    ownership_model in (
      'private_company',
      'cooperative',
      'producer_group',
      'public_company',
      'other'
    )
  ),
  employee_count_range text,
  website_url text check (website_url is null or website_url ~ '^https?://'),
  country_code char(2) not null default 'GR',
  headquarters_city text,
  headquarters_region text,
  serves_greece boolean not null default true,
  supported_languages text[] not null default '{}',
  summary text,
  export_license_status text not null default 'unknown' check (
    export_license_status in (
      'unknown',
      'not_required',
      'held',
      'not_held',
      'pending'
    )
  ),
  export_license_notes text,
  public_profile_status text not null default 'researching' check (
    public_profile_status in (
      'researching',
      'seeded',
      'contacted',
      'verified',
      'archived'
    )
  ),
  priority_tier smallint check (priority_tier between 1 and 3),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index organizations_display_name_trgm_idx
  on organizations using gin (display_name gin_trgm_ops);

create index organizations_type_idx on organizations (organization_type);
create index organizations_vat_number_idx on organizations (vat_number);
create index organizations_company_registration_number_idx
  on organizations (company_registration_number);

create table organization_aliases (
  id bigint generated always as identity primary key,
  organization_id bigint not null references organizations(id) on delete cascade,
  alias text not null,
  alias_kind text not null default 'alternate' check (
    alias_kind in ('alternate', 'transliteration', 'legal', 'brand')
  ),
  language_code text not null default '',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organization_id, alias, language_code)
);

create index organization_aliases_organization_id_idx
  on organization_aliases (organization_id);

create index organization_aliases_alias_trgm_idx
  on organization_aliases using gin (alias gin_trgm_ops);

create table source_documents (
  id bigint generated always as identity primary key,
  url text not null unique check (url ~ '^https?://'),
  source_type text not null check (
    source_type in (
      'official_website',
      'technical_document',
      'catalog',
      'trade_directory',
      'manual_note'
    )
  ),
  title text,
  domain text generated always as (regexp_replace(url, '^https?://([^/]+)/?.*$', '\1')) stored,
  language_code text,
  accessed_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index source_documents_domain_idx on source_documents (domain);

create table organization_sources (
  organization_id bigint not null references organizations(id) on delete cascade,
  source_document_id bigint not null references source_documents(id) on delete cascade,
  relevance text not null default 'profile' check (
    relevance in ('profile', 'contact', 'offering', 'certification', 'facility', 'other')
  ),
  notes text,
  created_at timestamptz not null default now(),
  primary key (organization_id, source_document_id)
);

create index organization_sources_source_document_id_idx
  on organization_sources (source_document_id);

create table facilities (
  id bigint generated always as identity primary key,
  organization_id bigint not null references organizations(id) on delete cascade,
  facility_type text not null check (
    facility_type in (
      'head_office',
      'factory',
      'warehouse',
      'cold_store',
      'distribution_center',
      'other'
    )
  ),
  name text,
  city text,
  region text,
  address text,
  temperature_zones text[] not null default '{}',
  notes text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index facilities_organization_id_idx on facilities (organization_id);

create table contacts (
  id bigint generated always as identity primary key,
  organization_id bigint not null references organizations(id) on delete cascade,
  source_document_id bigint references source_documents(id) on delete set null,
  contact_type text not null check (
    contact_type in ('email', 'phone', 'website', 'linkedin', 'contact_form')
  ),
  label text,
  value text not null,
  is_primary boolean not null default false,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index contacts_organization_id_idx on contacts (organization_id);
create index contacts_source_document_id_idx on contacts (source_document_id);

create unique index contacts_primary_per_type_idx
  on contacts (organization_id, contact_type)
  where is_primary = true;

create table supply_chain_stages (
  id bigint generated always as identity primary key,
  code text not null unique,
  name text not null,
  sort_order smallint not null unique,
  created_at timestamptz not null default now()
);

insert into supply_chain_stages (code, name, sort_order)
values
  ('ingredient_sourcing', 'Ingredient Sourcing', 10),
  ('agricultural_production', 'Agricultural Production', 20),
  ('primary_processing', 'Primary Processing', 30),
  ('product_development', 'Product Development', 40),
  ('manufacturing', 'Manufacturing', 50),
  ('private_label', 'Private Label', 60),
  ('packaging', 'Packaging', 70),
  ('warehousing', 'Warehousing', 80),
  ('cold_chain', 'Cold Chain', 90),
  ('distribution', 'Distribution', 100),
  ('export_shipping', 'Export Shipping', 110);

create table organization_stage_coverage (
  organization_id bigint not null references organizations(id) on delete cascade,
  stage_id bigint not null references supply_chain_stages(id) on delete cascade,
  coverage_type text not null default 'primary' check (
    coverage_type in ('primary', 'secondary', 'supporting')
  ),
  notes text,
  created_at timestamptz not null default now(),
  primary key (organization_id, stage_id)
);

create index organization_stage_coverage_stage_id_idx
  on organization_stage_coverage (stage_id);

create table market_channels (
  id bigint generated always as identity primary key,
  code text not null unique,
  name text not null,
  created_at timestamptz not null default now()
);

insert into market_channels (code, name)
values
  ('retail', 'Retail'),
  ('horeca', 'HORECA'),
  ('wholesale', 'Wholesale'),
  ('distributor', 'Distributor'),
  ('industrial', 'Industrial Buyer'),
  ('export', 'Export'),
  ('ecommerce', 'Ecommerce');

create table organization_channels (
  organization_id bigint not null references organizations(id) on delete cascade,
  market_channel_id bigint not null references market_channels(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (organization_id, market_channel_id)
);

create index organization_channels_market_channel_id_idx
  on organization_channels (market_channel_id);

create table organization_service_regions (
  organization_id bigint not null references organizations(id) on delete cascade,
  country_code char(2) not null default 'GR',
  region_name text not null,
  coverage_type text not null default 'served' check (
    coverage_type in (
      'headquarters',
      'served',
      'operates',
      'storage',
      'distribution'
    )
  ),
  notes text,
  created_at timestamptz not null default now(),
  primary key (organization_id, country_code, region_name, coverage_type)
);

create index organization_service_regions_region_name_idx
  on organization_service_regions (region_name);

create table organization_export_markets (
  organization_id bigint not null references organizations(id) on delete cascade,
  market_name text not null,
  country_code char(2),
  market_status text not null default 'current' check (
    market_status in ('current', 'target', 'former')
  ),
  notes text,
  created_at timestamptz not null default now(),
  primary key (organization_id, market_name, market_status)
);

create index organization_export_markets_country_code_idx
  on organization_export_markets (country_code);

create table product_categories (
  id bigint generated always as identity primary key,
  parent_id bigint references product_categories(id) on delete set null,
  slug text not null unique,
  name text not null,
  category_type text not null check (
    category_type in ('ingredient', 'finished_product', 'packaging', 'service')
  ),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index product_categories_parent_id_idx on product_categories (parent_id);

create table offerings (
  id bigint generated always as identity primary key,
  organization_id bigint not null references organizations(id) on delete cascade,
  product_category_id bigint references product_categories(id) on delete set null,
  name text not null,
  subcategory text,
  variety_or_cultivar text,
  offering_type text not null check (
    offering_type in (
      'ingredient',
      'finished_product',
      'packaging',
      'logistics_service',
      'service'
    )
  ),
  private_label_supported boolean,
  packaging_formats text[] not null default '{}',
  description text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (organization_id, name)
);

create index offerings_organization_id_idx on offerings (organization_id);
create index offerings_product_category_id_idx on offerings (product_category_id);
create index offerings_type_idx on offerings (offering_type);

create table offering_stage_links (
  offering_id bigint not null references offerings(id) on delete cascade,
  stage_id bigint not null references supply_chain_stages(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (offering_id, stage_id)
);

create index offering_stage_links_stage_id_idx on offering_stage_links (stage_id);

create table capacity_records (
  id bigint generated always as identity primary key,
  organization_id bigint not null references organizations(id) on delete cascade,
  offering_id bigint references offerings(id) on delete cascade,
  facility_id bigint references facilities(id) on delete cascade,
  source_document_id bigint references source_documents(id) on delete set null,
  capacity_scope text not null check (
    capacity_scope in (
      'organization',
      'offering',
      'facility',
      'offering_at_facility'
    )
  ),
  capacity_kind text not null check (
    capacity_kind in (
      'annual_production',
      'available_capacity',
      'storage_capacity',
      'throughput'
    )
  ),
  quantity numeric(14,2),
  unit text,
  available_quantity numeric(14,2),
  available_unit text,
  season_start_month smallint check (
    season_start_month is null or season_start_month between 1 and 12
  ),
  season_end_month smallint check (
    season_end_month is null or season_end_month between 1 and 12
  ),
  lead_time_weeks numeric(6,2),
  minimum_order_quantity text,
  notes text,
  valid_until date,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index capacity_records_organization_id_idx on capacity_records (organization_id);
create index capacity_records_offering_id_idx on capacity_records (offering_id);
create index capacity_records_facility_id_idx on capacity_records (facility_id);
create index capacity_records_source_document_id_idx
  on capacity_records (source_document_id);

create table capability_tags (
  id bigint generated always as identity primary key,
  code text not null unique,
  name text not null,
  created_at timestamptz not null default now()
);

insert into capability_tags (code, name)
values
  ('private_label', 'Private Label'),
  ('custom_product_development', 'Custom Product Development'),
  ('packaging_design_support', 'Packaging Design Support'),
  ('traceability', 'Traceability'),
  ('warehouse_management_system', 'Warehouse Management System'),
  ('live_tracking', 'Live Tracking'),
  ('smart_routing', 'Smart Routing'),
  ('gluten_free_facility', 'Gluten-Free Facility'),
  ('export_shipping', 'Export Shipping'),
  ('custom_molds', 'Custom Molds'),
  ('food_packaging_production', 'Food Packaging Production'),
  ('micro_picking', 'Micro Picking'),
  ('multi_temperature_fleet', 'Multi-Temperature Fleet');

create table organization_capabilities (
  organization_id bigint not null references organizations(id) on delete cascade,
  capability_tag_id bigint not null references capability_tags(id) on delete cascade,
  notes text,
  created_at timestamptz not null default now(),
  primary key (organization_id, capability_tag_id)
);

create index organization_capabilities_capability_tag_id_idx
  on organization_capabilities (capability_tag_id);

create table certifications (
  id bigint generated always as identity primary key,
  name text not null unique,
  certification_type text not null check (
    certification_type in (
      'food_safety',
      'quality',
      'organic',
      'origin_label',
      'religious',
      'social_compliance',
      'facility_registration',
      'market_access',
      'other'
    )
  ),
  issuing_body text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table organization_certifications (
  organization_id bigint not null references organizations(id) on delete cascade,
  certification_id bigint not null references certifications(id) on delete cascade,
  source_document_id bigint references source_documents(id) on delete set null,
  certificate_number text,
  certified_by text,
  scope text,
  status text not null default 'claimed' check (
    status in ('claimed', 'requested', 'verified', 'expired')
  ),
  issued_at date,
  expires_at date,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (organization_id, certification_id)
);

create index organization_certifications_certification_id_idx
  on organization_certifications (certification_id);

create index organization_certifications_source_document_id_idx
  on organization_certifications (source_document_id);

create table geographical_indications (
  id bigint generated always as identity primary key,
  name text not null,
  designation_type text not null check (
    designation_type in ('PDO', 'PGI', 'TSG')
  ),
  country_code char(2) not null default 'GR',
  product_category text,
  source_registry text not null default 'eambrosia' check (
    source_registry in ('ministry', 'elgo_dimitra', 'eambrosia', 'manual')
  ),
  registry_url text check (
    registry_url is null or registry_url ~ '^https?://'
  ),
  specification_url text check (
    specification_url is null or specification_url ~ '^https?://'
  ),
  status text not null default 'active' check (
    status in ('active', 'amended', 'cancelled')
  ),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (country_code, name, designation_type)
);

create index geographical_indications_designation_type_idx
  on geographical_indications (designation_type);

create table organization_geographical_indications (
  organization_id bigint not null references organizations(id) on delete cascade,
  geographical_indication_id bigint not null references geographical_indications(id) on delete cascade,
  source_document_id bigint references source_documents(id) on delete set null,
  approval_status text not null default 'claimed' check (
    approval_status in (
      'claimed',
      'authorized',
      'verified',
      'revoked',
      'expired'
    )
  ),
  approved_by text,
  approval_reference text,
  valid_from date,
  valid_until date,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (organization_id, geographical_indication_id)
);

create index organization_geographical_indications_gi_id_idx
  on organization_geographical_indications (geographical_indication_id);
create index organization_geographical_indications_source_document_id_idx
  on organization_geographical_indications (source_document_id);

create table outreach_leads (
  organization_id bigint primary key references organizations(id) on delete cascade,
  lead_status text not null default 'research_ready' check (
    lead_status in (
      'research_ready',
      'queued',
      'contacted',
      'replied',
      'qualified',
      'disqualified',
      'on_hold'
    )
  ),
  lead_score numeric(5,2),
  owner_name text,
  next_action text,
  next_action_due_at timestamptz,
  last_contacted_at timestamptz,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index outreach_leads_status_idx on outreach_leads (lead_status);
create index outreach_leads_next_action_due_at_idx on outreach_leads (next_action_due_at);

create table outreach_events (
  id bigint generated always as identity primary key,
  organization_id bigint not null references organizations(id) on delete cascade,
  source_document_id bigint references source_documents(id) on delete set null,
  event_type text not null check (
    event_type in ('email', 'call', 'meeting', 'linkedin', 'form', 'note')
  ),
  occurred_at timestamptz not null default now(),
  subject text,
  body text,
  outcome text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index outreach_events_organization_id_idx on outreach_events (organization_id);
create index outreach_events_source_document_id_idx on outreach_events (source_document_id);
create index outreach_events_occurred_at_idx on outreach_events (occurred_at desc);

create table ingestion_runs (
  id bigint generated always as identity primary key,
  organization_id bigint references organizations(id) on delete set null,
  source_document_id bigint references source_documents(id) on delete set null,
  run_status text not null check (
    run_status in ('queued', 'running', 'succeeded', 'failed')
  ),
  parser_version text,
  raw_payload jsonb not null default '{}'::jsonb,
  extracted_payload jsonb not null default '{}'::jsonb,
  error_message text,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index ingestion_runs_organization_id_idx on ingestion_runs (organization_id);
create index ingestion_runs_source_document_id_idx on ingestion_runs (source_document_id);
create index ingestion_runs_status_idx on ingestion_runs (run_status);

create trigger organizations_set_updated_at
before update on organizations
for each row execute function set_updated_at();

create trigger organization_aliases_set_updated_at
before update on organization_aliases
for each row execute function set_updated_at();

create trigger source_documents_set_updated_at
before update on source_documents
for each row execute function set_updated_at();

create trigger facilities_set_updated_at
before update on facilities
for each row execute function set_updated_at();

create trigger contacts_set_updated_at
before update on contacts
for each row execute function set_updated_at();

create trigger product_categories_set_updated_at
before update on product_categories
for each row execute function set_updated_at();

create trigger offerings_set_updated_at
before update on offerings
for each row execute function set_updated_at();

create trigger capacity_records_set_updated_at
before update on capacity_records
for each row execute function set_updated_at();

create trigger certifications_set_updated_at
before update on certifications
for each row execute function set_updated_at();

create trigger organization_certifications_set_updated_at
before update on organization_certifications
for each row execute function set_updated_at();

create trigger geographical_indications_set_updated_at
before update on geographical_indications
for each row execute function set_updated_at();

create trigger organization_geographical_indications_set_updated_at
before update on organization_geographical_indications
for each row execute function set_updated_at();

create trigger outreach_leads_set_updated_at
before update on outreach_leads
for each row execute function set_updated_at();

create trigger outreach_events_set_updated_at
before update on outreach_events
for each row execute function set_updated_at();

create trigger ingestion_runs_set_updated_at
before update on ingestion_runs
for each row execute function set_updated_at();

commit;
