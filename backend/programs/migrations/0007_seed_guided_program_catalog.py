from django.db import migrations


CATALOG = {
    "wellness": [
        ("Reset de hidratare", "Un program pentru ritm, hidratare si energie stabila.", 7, "basic"),
        ("Somn mai linistit", "Igiena somnului cu pasi simpli si repetabili.", 10, "basic"),
        ("Respira si recentreaza-te", "Respiratie constienta pentru claritate mentala.", 7, "basic"),
        ("Mornings cu energie", "Rutina de dimineata pentru focus si tonus.", 14, "premium"),
        ("Reset anti-stres", "Strategii practice pentru reducerea stresului cotidian.", 14, "premium"),
        ("Mindful nutrition", "Obiceiuri alimentare constiente si usor de urmat.", 10, "premium"),
        ("Miscare constanta", "Micro-antrenamente si plimbari ghidate zilnic.", 21, "premium"),
        ("Longevitate urbana", "Obiceiuri zilnice pentru recuperare si vitalitate.", 21, "vip"),
        ("Wellness executiv", "Echilibru intre performanta si refacere.", 14, "vip"),
        ("Reset total 30", "Program complet de refacere fizica si mentala.", 30, "vip"),
    ],
    "coaching": [
        ("Claritate personala", "Obiective, valori si actiuni aliniate.", 7, "basic"),
        ("Obiceiuri care tin", "Structura simpla pentru obiceiuri sustenabile.", 10, "basic"),
        ("Focus fara haos", "Reduci zgomotul mental si alegi prioritatile bune.", 7, "basic"),
        ("Leadership interior", "Autoghidare si disciplina blanda.", 14, "premium"),
        ("Decizii mai bune", "Cadru practic pentru decizii rapide si sanatoase.", 14, "premium"),
        ("Rutina de performanta", "Structura zilnica pentru lucru profund si pauze utile.", 21, "premium"),
        ("Comunicare calma", "Exersezi raspunsuri clare in contexte tensionate.", 10, "premium"),
        ("Coaching strategic VIP", "Plan personalizat pentru obiective majore.", 21, "vip"),
        ("Sprint de transformare", "Executie ghidata cu revizuire si optimizare zilnica.", 30, "vip"),
        ("Executive alignment", "Claritate, delegare si energie pentru lideri.", 14, "vip"),
    ],
    "educatie": [
        ("Bazele reglajului emotional", "Intelegi mecanisme simple ale starii emotionale.", 7, "basic"),
        ("Cum functioneaza obiceiurile", "Inveti bucla obiceiurilor si cum o folosesti in favoarea ta.", 10, "basic"),
        ("ABC-ul mindfulness", "Fundamente practice pentru prezenta si atentie.", 7, "basic"),
        ("Neuroplasticitate aplicata", "Inveti cum schimbi tipare prin repetitie constienta.", 14, "premium"),
        ("Psihologia motivatiei", "Intelegi ce te porneste si ce te blocheaza.", 14, "premium"),
        ("Somn si creier", "Legatura dintre odihna, claritate si rezilienta.", 10, "premium"),
        ("Educatie pentru stres", "Cum se construieste rezistenta sanatoasa.", 14, "premium"),
        ("Masterclass wellbeing", "Lectii extinse cu aplicatii zilnice in ritmul tau.", 21, "vip"),
        ("Educatie emotionala avansata", "Concepte avansate cu reflectii ghidate.", 21, "vip"),
        ("AI learning companion", "Program exclusiv cu recomandari adaptive zilnice.", 14, "vip"),
    ],
    "suport": [
        ("Revenire dupa zile grele", "Pasi blanzi pentru stabilizare dupa perioade solicitante.", 7, "basic"),
        ("Ancore pentru anxietate", "Instrumente simple pentru revenire in prezent.", 10, "basic"),
        ("Jurnal de sprijin", "Reflectii scurte pentru claritate si descarcare.", 7, "basic"),
        ("Suport emotional zilnic", "Micro-check-in-uri si exercitii pentru reglaj constant.", 14, "premium"),
        ("Rutina de siguranta", "Pasi practici pentru zile cu incarcatura mare.", 14, "premium"),
        ("Boundary reset", "Inveti limite blande si protectie emotionala.", 10, "premium"),
        ("Stabilitate relationala", "Exersezi raspunsuri si pauze utile in relatii.", 14, "premium"),
        ("Suport VIP adaptiv", "Interventii ghidate si ajustari dinamice zilnice.", 21, "vip"),
        ("Recovery executive", "Recuperare emotionala pentru ritm profesional intens.", 14, "vip"),
        ("Calm architecture", "Reconstruiesti stabilitatea prin pasi zilnici foarte clari.", 30, "vip"),
    ],
}


def _day_task_type(day_number):
    return ["check-in", "exercise", "reflection", "reminder", "journaling"][(day_number - 1) % 5]


def seed_program_catalog(apps, schema_editor):
    GuidedProgram = apps.get_model("programs", "GuidedProgram")
    GuidedProgramDay = apps.get_model("programs", "GuidedProgramDay")

    focus_by_category = {
        "wellness": "reglaj corporal si energie sustenabila",
        "coaching": "claritate, prioritate si executie consecventa",
        "educatie": "intelegere practica si integrare zilnica",
        "suport": "stabilizare emotionala si siguranta interioara",
    }

    for category, rows in CATALOG.items():
        for title, description, duration_days, plan_access in rows:
            program, created = GuidedProgram.objects.get_or_create(
                title=title,
                language="ro",
                defaults={
                    "description": description,
                    "category": category,
                    "duration_days": duration_days,
                    "plan_access": plan_access,
                    "active": True,
                    "is_premium": plan_access in {"premium", "vip"},
                },
            )
            if not created:
                program.description = description
                program.category = category
                program.duration_days = duration_days
                program.plan_access = plan_access
                program.active = True
                program.is_premium = plan_access in {"premium", "vip"}
                program.save(update_fields=["description", "category", "duration_days", "plan_access", "active", "is_premium"])

            GuidedProgramDay.objects.filter(program=program).delete()
            for day_number in range(1, duration_days + 1):
                focus = focus_by_category[category]
                GuidedProgramDay.objects.create(
                    program=program,
                    day_number=day_number,
                    title=f"Ziua {day_number}: {title}",
                    content=(
                        f"Astazi lucrezi pe {focus}. Alege 10-20 minute pentru a parcurge pasul zilei, "
                        f"noteaza ce observi si mentine ritmul fara presiune inutila. "
                        f"Acesta este pasul {day_number} din {duration_days} in programul {title}."
                    ),
                    task_type=_day_task_type(day_number),
                    estimated_time_minutes=10 + ((day_number - 1) % 3) * 5,
                    question=f"Care este cel mai util lucru pe care il observi in ziua {day_number}?",
                    ai_prompt=f"Ofera un check-in scurt si practic pentru ziua {day_number} din programul {title}.",
                )


class Migration(migrations.Migration):

    dependencies = [
        ("programs", "0006_alter_guidedprogram_options_guidedprogram_category_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_program_catalog, migrations.RunPython.noop),
    ]
