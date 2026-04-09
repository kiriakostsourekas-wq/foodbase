import { useEffect, useState } from 'react';
import StepDescribe from '@/components/create/StepDescribe';
import StepRefine from '@/components/create/StepRefine';
import StepProcessing from '@/components/create/StepProcessing';
import StepReady from '@/components/create/StepReady';
import { apiFetch } from '@/lib/api';
import { storeProductProfile } from '@/lib/foodbase';

const STEPS = ['describe', 'refine', 'processing', 'ready'];

export default function CreateProduct() {
  const urlParams = new URLSearchParams(window.location.search);
  const initialPrompt = urlParams.get('q') || '';

  const [step, setStep] = useState('describe');
  const [productData, setProductData] = useState({ prompt: initialPrompt });
  const [generationError, setGenerationError] = useState(null);
  const [generationAttempt, setGenerationAttempt] = useState(0);

  const goNext = (data = {}) => {
    const merged = { ...productData, ...data };
    setProductData(merged);
    const idx = STEPS.indexOf(step);
    if (idx < STEPS.length - 1) setStep(STEPS[idx + 1]);
  };

  useEffect(() => {
    if (step !== 'processing') {
      return;
    }

    let isMounted = true;
    setGenerationError(null);

    async function generateProductProfile() {
      try {
        const generatedProfile = await apiFetch('/ai/product-profile', {
          method: 'POST',
          body: JSON.stringify({
            prompt: productData.prompt,
            answers: productData.answers || {},
          }),
        });
        if (!isMounted) return;
        storeProductProfile(generatedProfile);
        setProductData((current) => ({ ...current, generatedProfile }));
        setStep('ready');
      } catch (error) {
        if (!isMounted) return;
        setGenerationError(error.message);
      }
    }

    generateProductProfile();

    return () => {
      isMounted = false;
    };
  }, [step, productData.prompt, productData.answers, generationAttempt]);

  return (
    <div className="min-h-screen bg-background">
      {/* Progress bar */}
      <div className="fixed top-16 left-0 right-0 z-40 h-0.5 bg-border">
        <div
          className="h-full bg-primary transition-all duration-500"
          style={{ width: `${((STEPS.indexOf(step) + 1) / STEPS.length) * 100}%` }}
        />
      </div>

      <div className="pt-6">
        {step === 'describe' && <StepDescribe initialPrompt={initialPrompt} onNext={goNext} />}
        {step === 'refine' && <StepRefine productData={productData} onNext={goNext} />}
        {step === 'processing' && (
          <StepProcessing
            error={generationError}
            onRetry={() => setGenerationAttempt((current) => current + 1)}
            onBack={() => setStep('refine')}
          />
        )}
        {step === 'ready' && <StepReady productData={productData} />}
      </div>
    </div>
  );
}
