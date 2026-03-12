# Feature Access Matrix

Matricea de acces per tier folosită în backend (`core/feature_access.py`).

## Tier Order

- free
- trial
- basic
- premium
- vip

## Features

- analytics_track
  - free, trial, basic, premium, vip
- chat_ai
  - trial, basic, premium, vip
- journal_access
  - trial, basic, premium, vip
- programs_access
  - trial, basic, premium, vip
- premium_programs
  - premium, vip
- payment_checkout
  - free, trial, basic, premium, vip
- payment_upgrade
  - trial, basic, premium, vip

## Governance Behavior

- fiecare verificare de acces scrie audit log în `core_featureaccesslog`
- fiecare verificare generează event analytics `feature_access_checked`
- decorator reutilizabil: `require_feature("feature_key")`
