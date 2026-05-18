
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_contact: string;
  tax_region: string;
  language: string;
  is_premium: boolean;
  plan_tier: 'free' | 'trial' | 'basic' | 'premium' | 'premium_discounted' | 'vip';
  early_discount_eligible: boolean;
  onboarding_completed: boolean;
  membership_tier: 'free' | 'trial' | 'normal' | 'premium' | 'basic' | 'vip';
  trial_ends_at?: string | null;
  has_saved_card: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  created_at: string;
}
