
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_contact: string;
  tax_region: string;
  language: string;
  is_premium: boolean;
  onboarding_completed: boolean;
  membership_tier: 'normal' | 'premium';
  has_saved_card: boolean;
  is_superuser: boolean;
  created_at: string;
}
