import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Send, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';

export default function InquiryModal({ open, onOpenChange, supplier }) {
  const [sent, setSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setSent(true);
    setTimeout(() => {
      setSent(false);
      onOpenChange(false);
    }, 2000);
  };

  if (sent) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <div className="text-center py-8">
            <div className="w-14 h-14 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-7 h-7 text-emerald-600" />
            </div>
            <h3 className="text-lg font-semibold">Inquiry Sent!</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Your message has been sent to {supplier?.name}. They typically respond within {supplier?.responseTime}.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="font-display">Contact {supplier?.name}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-xs">Your Name</Label>
              <Input placeholder="Full name" required />
            </div>
            <div className="space-y-1.5">
              <Label className="text-xs">Company</Label>
              <Input placeholder="Company name" required />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Email</Label>
            <Input type="email" placeholder="you@company.com" required />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Product Interest</Label>
            <Input placeholder="e.g. Extra Virgin Olive Oil, 5000L" />
          </div>
          <div className="space-y-1.5">
            <Label className="text-xs">Message</Label>
            <Textarea
              placeholder="Describe your requirements, quantities, packaging needs..."
              rows={4}
              required
            />
          </div>
          <Button type="submit" className="w-full gap-2">
            <Send className="w-4 h-4" /> Send Inquiry
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}