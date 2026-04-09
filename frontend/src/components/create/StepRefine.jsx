import { useState } from 'react';
import { Sparkles, Zap, ChevronRight, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

const QUESTIONS = [
  {
    id: 'type',
    question: 'What type of product is this?',
    options: ['Food & Beverage', 'Supplements / Wellness', 'Natural Cosmetics', 'Ingredients / Raw Material', 'Packaged Snack', 'Condiment / Sauce'],
  },
  {
    id: 'customer',
    question: 'Who is the target customer?',
    options: ['Health-conscious consumers', 'Supermarket shoppers', 'Premium / gourmet buyers', 'HoReCa / foodservice', 'Export / international buyers', 'Online / DTC shoppers'],
  },
  {
    id: 'tier',
    question: 'What price tier are you targeting?',
    options: ['Mass market', 'Mid-range', 'Premium', 'Ultra-premium / luxury'],
  },
  {
    id: 'positioning',
    question: 'How would you position this product?',
    options: ['Organic', 'Private label', 'Export-first', 'Sustainable / eco', 'Functional / health', 'Artisan / heritage'],
    multi: true,
  },
  {
    id: 'packaging',
    question: 'What packaging format do you want?',
    options: ['Glass bottle / jar', 'Tin / metal can', 'Flexible pouch', 'Carton box', 'Plastic container', 'Not sure yet'],
  },
  {
    id: 'certifications',
    question: 'Which certifications matter?',
    options: ['EU Organic', 'ISO 22000', 'HACCP', 'PDO / PGI', 'Kosher', 'None required'],
    multi: true,
  },
  {
    id: 'volume',
    question: 'What production volume do you expect?',
    options: ['< 1,000 units/month', '1,000–10,000 units/month', '10,000–100,000 units/month', '100,000+ units/month', 'Not decided yet'],
  },
];

export default function StepRefine({ productData, onNext }) {
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState({});
  const [selected, setSelected] = useState([]);

  const q = QUESTIONS[currentQ];
  const progress = ((currentQ + 1) / QUESTIONS.length) * 100;

  const select = (opt) => {
    if (q.multi) {
      setSelected(prev => prev.includes(opt) ? prev.filter(o => o !== opt) : [...prev, opt]);
    } else {
      setSelected([opt]);
    }
  };

  const next = () => {
    const newAnswers = { ...answers, [q.id]: q.multi ? selected : selected[0] };
    setAnswers(newAnswers);
    setSelected([]);
    if (currentQ < QUESTIONS.length - 1) {
      setCurrentQ(c => c + 1);
    } else {
      onNext({ answers: newAnswers });
    }
  };

  const autoFill = () => {
    const filled = {};
    QUESTIONS.forEach(q => {
      filled[q.id] = q.multi ? [q.options[0], q.options[1]] : q.options[0];
    });
    onNext({ answers: filled, autoFilled: true });
  };

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 py-12">
      <div className="max-w-xl w-full mx-auto">
        {/* Header */}
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-primary" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-muted-foreground font-medium">Let's make this more precise</p>
            <div className="flex items-center gap-2 mt-1">
              <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
              </div>
              <span className="text-xs text-muted-foreground">{currentQ + 1}/{QUESTIONS.length}</span>
            </div>
          </div>
        </div>

        {/* AI Auto-Fill — always visible */}
        <div className="mb-6 bg-primary/5 border border-primary/20 rounded-2xl p-4 flex items-start gap-3">
          <Zap className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-foreground">AI Auto-Fill available</p>
            <p className="text-xs text-muted-foreground mt-0.5">Missing some details? I can auto-fill likely ingredients, packaging assumptions, and product specs based on your concept.</p>
          </div>
          <Button size="sm" variant="outline" onClick={autoFill} className="flex-shrink-0 gap-1.5 border-primary/30 text-primary hover:bg-primary/10">
            <Zap className="w-3 h-3" /> Auto-Fill
          </Button>
        </div>

        {/* Question */}
        <div className="bg-white rounded-2xl border border-border shadow-sm p-6 mb-4">
          <p className="text-xs text-muted-foreground font-medium mb-2">Question {currentQ + 1}</p>
          <h2 className="font-semibold text-foreground text-lg mb-5">{q.question}</h2>
          {q.multi && <p className="text-xs text-muted-foreground mb-3">Select all that apply</p>}
          <div className="grid grid-cols-2 gap-2">
            {q.options.map(opt => {
              const isSelected = selected.includes(opt);
              return (
                <button
                  key={opt}
                  onClick={() => select(opt)}
                  className={`text-sm px-3 py-2.5 rounded-xl border text-left transition-all duration-150 ${
                    isSelected
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'bg-background border-border hover:border-primary/40 hover:bg-primary/5 text-foreground'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {isSelected && <Check className="w-3.5 h-3.5 flex-shrink-0" />}
                    {opt}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex gap-3">
          <Button
            variant="ghost"
            onClick={() => { setSelected([]); next(); }}
            className="text-sm text-muted-foreground"
          >
            Skip
          </Button>
          <Button
            disabled={selected.length === 0}
            onClick={next}
            className="flex-1 gap-2"
          >
            {currentQ < QUESTIONS.length - 1 ? 'Next question' : 'Build my product'}
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}