import { Shield } from 'lucide-react';

const certColors = {
  'Organic EU': 'bg-green-50 text-green-700 border-green-200',
  'PDO': 'bg-amber-50 text-amber-700 border-amber-200',
  'PGI': 'bg-amber-50 text-amber-700 border-amber-200',
  'ISO 9001': 'bg-blue-50 text-blue-700 border-blue-200',
  'ISO 22000': 'bg-blue-50 text-blue-700 border-blue-200',
  'HACCP': 'bg-sky-50 text-sky-700 border-sky-200',
  'BRC': 'bg-purple-50 text-purple-700 border-purple-200',
  'IFS': 'bg-purple-50 text-purple-700 border-purple-200',
  'Kosher': 'bg-indigo-50 text-indigo-700 border-indigo-200',
  'Halal': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Fair Trade': 'bg-teal-50 text-teal-700 border-teal-200',
  'Vegan Certified': 'bg-lime-50 text-lime-700 border-lime-200',
  'Non-GMO': 'bg-orange-50 text-orange-700 border-orange-200',
};

export default function CertBadge({ cert, size = 'sm' }) {
  const colors = certColors[cert] || 'bg-gray-50 text-gray-700 border-gray-200';
  const sizeClasses = size === 'sm'
    ? 'text-[10px] px-2 py-0.5 gap-1'
    : 'text-xs px-2.5 py-1 gap-1.5';

  return (
    <span className={`inline-flex items-center rounded-full border font-medium ${colors} ${sizeClasses}`}>
      <Shield className={size === 'sm' ? 'w-2.5 h-2.5' : 'w-3 h-3'} />
      {cert}
    </span>
  );
}