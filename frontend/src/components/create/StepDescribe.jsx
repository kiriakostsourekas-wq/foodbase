import { useState } from 'react';
import { Sparkles, ArrowRight, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';

const EXAMPLES = [
  'I want to launch a premium organic olive oil for export',
  'I want a honey-based wellness drink for supermarkets',
  'I want a private label Greek herb tea line',
  'I want a functional dairy snack for the EU market',
  'I want a natural cosmetics line with olive-derived ingredients',
];

export default function StepDescribe({ initialPrompt, onNext }) {
  const [prompt, setPrompt] = useState(initialPrompt || '');
  const [focused, setFocused] = useState(false);

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center px-4 py-16">
      <div className="max-w-2xl w-full mx-auto">
        {/* AI badge */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center gap-2 bg-primary/10 text-primary text-sm font-medium px-4 py-2 rounded-full">
            <Sparkles className="w-4 h-4" />
            Foodbase AI — Product Creator
          </div>
        </div>

        <h1 className="font-display text-4xl sm:text-5xl font-bold text-foreground text-center leading-tight mb-4">
          Describe your<br />product idea
        </h1>
        <p className="text-center text-muted-foreground text-lg mb-10">
          Tell us what you want to create. Use plain language — AI will handle the rest.
        </p>

        {/* Input */}
        <div className={`bg-white rounded-2xl border-2 transition-all duration-200 shadow-sm ${focused ? 'border-primary shadow-lg shadow-primary/10' : 'border-border'}`}>
          <div className="flex items-start gap-3 p-4">
            <Sparkles className="w-5 h-5 text-primary mt-1 flex-shrink-0" />
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="e.g. I want to launch a premium organic olive oil for the European export market..."
              className="flex-1 bg-transparent outline-none resize-none text-foreground placeholder:text-muted-foreground/60 text-base leading-relaxed min-h-[100px]"
              rows={4}
            />
          </div>
          <div className="flex items-center justify-between px-4 pb-3 border-t border-border/40 pt-3">
            <span className="text-xs text-muted-foreground">{prompt.length} characters</span>
            <Button
              disabled={prompt.trim().length < 10}
              onClick={() => onNext({ prompt })}
              className="gap-2"
            >
              Continue <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* AI Auto-Fill prompt */}
        <div className="mt-4 flex items-center justify-center">
          <button
            onClick={() => onNext({ prompt: prompt || EXAMPLES[0], autoFill: true })}
            className="flex items-center gap-2 text-sm text-primary font-medium hover:underline"
          >
            <Zap className="w-4 h-4" />
            Or use AI Auto-Fill — skip to AI-generated details
          </button>
        </div>

        {/* Examples */}
        <div className="mt-10">
          <p className="text-xs text-muted-foreground text-center mb-3 font-medium uppercase tracking-wide">Try an example</p>
          <div className="flex flex-col gap-2">
            {EXAMPLES.map(ex => (
              <button
                key={ex}
                onClick={() => setPrompt(ex)}
                className="text-left text-sm text-muted-foreground bg-muted hover:bg-muted/70 px-4 py-3 rounded-xl transition-colors hover:text-foreground border border-transparent hover:border-border/50"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
