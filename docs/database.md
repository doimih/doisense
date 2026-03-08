# Schema bazei de date – Doisense

## 1. Relații conceptuale

- **users_user**: utilizatori (auth)
- **profiles_userprofile**: 1:1 cu User, preferințe pentru AI (ton, sensibilități, stil). Aceste câmpuri sunt **actualizate automat de AI** pe baza textelor utilizatorului din jurnal (scan DB → structurare → update profil), indiferent de limbă/țară.
- **journal_journalquestion**: întrebări pentru jurnal (per limbă/categorie)
- **journal_journalentry**: răspunsuri utilizator la întrebări (user_id, question_id, content, emotions JSON)
- **programs_guidedprogram**: programe ghidate (titlu, descriere, limbă)
- **programs_guidedprogramday**: zile per program (day_number, content, question, ai_prompt)
- **ai_conversationtemplate**: template-uri pentru chat (name, language, prompt)
- **payments_payment**: legătură user – Stripe (customer_id, subscription_id, status)
- **ai_ailog** (opțional): log apeluri AI (user_id, model, prompt_hash, created_at)

## 2. Tabele (Django models)

### users_user
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| email | unique | |
| password | hashed | |
| language | char(2) | ro, en, de, it, es, pl |
| is_premium | bool | default False |
| created_at | datetime | |

### profiles_userprofile
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| user_id | FK(users_user) | unique |
| preferred_tone | varchar | |
| sensitivities | text/JSON | |
| communication_style | varchar | |
| emotional_baseline | varchar | |
| keywords | JSON | |

### journal_journalquestion
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| text | text | |
| category | varchar | |
| language | char(2) | |
| tags | JSON | |
| active | bool | default True |

### journal_journalentry
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| user_id | FK(users_user) | |
| question_id | FK(journal_journalquestion) | |
| content | text | |
| created_at | datetime | |
| emotions | JSON | |

### programs_guidedprogram
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| title | varchar | |
| description | text | |
| language | char(2) | |
| active | bool | default True |
| is_premium | bool | default False |

### programs_guidedprogramday
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| program_id | FK(programs_guidedprogram) | |
| day_number | int | |
| title | varchar | |
| content | text | |
| question | text | |
| ai_prompt | text | |

### ai_conversationtemplate
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| name | varchar | |
| language | char(2) | |
| prompt | text | |

### payments_payment
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| user_id | FK(users_user) | |
| stripe_customer_id | varchar, null | |
| stripe_subscription_id | varchar, null | |
| status | varchar | active, cancelled, past_due, etc. |
| created_at | datetime | |
| updated_at | datetime | |

### ai_ailog (opțional)
| Câmp | Tip | Note |
|------|-----|------|
| id | PK | |
| user_id | FK(users_user), null | |
| model | varchar | |
| prompt_hash | varchar | |
| created_at | datetime | |

## 3. Migrări

- Toate modificările de schemă se fac prin migrări Django: `python manage.py makemigrations` și `python manage.py migrate`.
- Fișierele de migrare sunt versionate în repo.
