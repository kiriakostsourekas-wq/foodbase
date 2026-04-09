import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Link } from 'react-router-dom';
import { MapPin, Shield, Package, Clock } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import { getSupplierImageUrl } from '@/lib/foodbase';

// Fix leaflet default icon
delete window.L?.Icon?.Default?.prototype?._getIconUrl;

function createMarkerIcon(isActive) {
  const color = isActive ? '#c8860a' : '#1e3a5f';
  const size = isActive ? 38 : 30;
  const inner = isActive ? 12 : 8;
  
  return window.L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      width:${size}px;height:${size}px;border-radius:50%;
      background:${color};border:3px solid white;
      box-shadow:0 2px 10px rgba(0,0,0,${isActive ? 0.35 : 0.2});
      display:flex;align-items:center;justify-content:center;
      transition:all 0.2s ease;
      ${isActive ? 'z-index:1000;' : ''}
    "><div style="width:${inner}px;height:${inner}px;border-radius:50%;background:white;"></div></div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
}

function MapUpdater({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.flyTo(center, zoom || 8, { duration: 0.8 });
    }
  }, [center, zoom, map]);
  return null;
}

function MapPopupContent({ supplier }) {
  const heroImage = getSupplierImageUrl(supplier, 'hero');

  return (
    <div className="w-64">
      <div className="relative h-28 overflow-hidden">
        <img src={heroImage} alt={supplier.name} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <div className="absolute bottom-2 left-2">
          <p className="text-white font-semibold text-sm">{supplier.name}</p>
          <div className="flex items-center gap-1">
            <MapPin className="w-3 h-3 text-white/80" />
            <span className="text-white/80 text-xs">{supplier.city}</span>
          </div>
        </div>
      </div>
      <div className="p-3">
        <p className="text-xs text-muted-foreground line-clamp-2">{supplier.shortDescription}</p>
        <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1"><Package className="w-3 h-3" />{supplier.moq}</span>
          <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{supplier.leadTime}</span>
          {supplier.verified && <span className="flex items-center gap-1 text-emerald-600"><Shield className="w-3 h-3" />Verified</span>}
        </div>
        <Link to={`/supplier/${supplier.slug}`} className="block mt-2 text-center text-xs bg-primary text-primary-foreground rounded-lg py-1.5 font-medium hover:bg-primary/90 transition-colors">
          View Profile
        </Link>
      </div>
    </div>
  );
}

function SupplierMarker({ supplier, isHighlighted, onHover, onLeave, onClick }) {
  const markerRef = useRef(null);

  useEffect(() => {
    if (isHighlighted && markerRef.current) {
      markerRef.current.openPopup();
    }
  }, [isHighlighted]);

  return (
    <Marker
      ref={markerRef}
      position={[supplier.lat, supplier.lng]}
      icon={createMarkerIcon(isHighlighted)}
      eventHandlers={{
        mouseover: () => onHover?.(supplier.id),
        mouseout: () => onLeave?.(),
        click: () => onClick?.(supplier.id),
      }}
    >
      <Popup>
        <MapPopupContent supplier={supplier} />
      </Popup>
    </Marker>
  );
}

export default function SupplierMap({ suppliers, highlightedId, onHoverSupplier, onLeaveSupplier, onClickSupplier, flyTo }) {
  const GREECE_CENTER = [38.5, 23.8];
  const GREECE_ZOOM = 6.5;

  return (
    <div className="w-full h-full rounded-2xl overflow-hidden border border-border/50 shadow-sm">
      <MapContainer
        center={GREECE_CENTER}
        zoom={GREECE_ZOOM}
        className="w-full h-full"
        zoomControl={true}
        scrollWheelZoom={true}
        minZoom={5}
        maxZoom={14}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        {flyTo && <MapUpdater center={flyTo.center} zoom={flyTo.zoom} />}
        {suppliers.map(supplier => (
          <SupplierMarker
            key={supplier.id}
            supplier={supplier}
            isHighlighted={highlightedId === supplier.id}
            onHover={onHoverSupplier}
            onLeave={onLeaveSupplier}
            onClick={onClickSupplier}
          />
        ))}
      </MapContainer>
    </div>
  );
}
