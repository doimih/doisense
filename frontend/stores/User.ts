
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_contact: string;
  tax_region: string;
  language: string;
  is_premium: boolean;
  plan_tier: 'free' | 'trial' | 'basic' | 'premium' | 'vip';
  trial_ends_at: string | null;
  onboarding_completed: boolean;
  membership_tier: 'free' | 'trial' | 'basic' | 'premium' | 'vip';
  has_saved_card: boolean;
  is_superuser: boolean;
  created_at: string;
}
