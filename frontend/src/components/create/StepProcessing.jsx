import { useEffect, useState } from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

const STAGES = [
  { label: 'Analyzing your concept', duration: 1400 },
  { label: 'Estimating product attributes', duration: 1200 },
  { label: 'Building your product profile', duration: 1600 },
  { label: 'Matching likely market positioning', duration: 1100 },
  { label: 'Assembling sourcing insights', duration: 900 },
];

export default function StepProcessing({ error, onRetry, onBack }) {
  const [stageIdx, setStageIdx] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let total = 0;
    const timers = [];
    STAGES.forEach((s, i) => {
      const t = setTimeout(() => setStageIdx(i % STAGES.length), total);
      timers.push(t);
      total += s.duration;
    });

    const interval = setInterval(() => {
      setProgress(p => {
        if (error) return p;
        return p >= 94 ? 26 : p + 1.2;
      });
    }, 80);

    return () => { timers.forEach(clearTimeout); clearInterval(interval); };
  }, [error]);

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4">
      <div className="max-w-sm w-full text-center">
        {/* Animated orb */}
        <div className="relative w-24 h-24 mx-auto mb-10">
          <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
          <div className="absolute inset-2 rounded-full bg-primary/30 animate-pulse" />
          <div className="relative w-full h-full rounded-full bg-primary flex items-center justify-center shadow-xl shadow-primary/30">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
        </div>

        <h2 className="font-display text-2xl font-bold text-foreground mb-2">Building your product</h2>
        <p className="text-muted-foreground text-sm mb-10">
          {error ? 'Foodbase AI hit an error.' : 'Foodbase AI is at work...'}
        </p>

        {/* Progress bar */}
        <div className="w-full bg-muted rounded-full h-2 mb-6 overflow-hidden">
          <div
            className="h-full bg-primary rounded-full transition-all duration-200"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Stages */}
        <div className="space-y-2">
          {STAGES.map((s, i) => (
            <div key={s.label} className={`flex items-center gap-2.5 text-sm transition-all duration-300 ${i <= stageIdx ? 'text-foreground' : 'text-muted-foreground/40'}`}>
              <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${i < stageIdx ? 'bg-emerald-500' : i === stageIdx ? 'bg-primary animate-pulse' : 'bg-muted-foreground/30'}`} />
              {s.label}
            </div>
          ))}
        </div>

        {error && (
          <div className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-4 text-left">
            <p className="text-sm font-medium text-red-800">AI generation failed</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <div className="flex gap-3 mt-4">
              <Button size="sm" onClick={onRetry}>Try again</Button>
              <Button size="sm" variant="outline" onClick={onBack}>Back</Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
