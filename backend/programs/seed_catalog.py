from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProgramSeed:
    category: str
    title: str
    description: str
    duration_days: int
    plan_access: str


_CATALOG: dict[str, list[tuple[str, str, int, str]]] = {
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
        ("Rutina de siguranta", "Pași practici pentru zile cu incarcatura mare.", 14, "premium"),
        ("Boundary reset", "Inveti limite blande si protectie emotionala.", 10, "premium"),
        ("Stabilitate relationala", "Exersezi raspunsuri si pauze utile in relatii.", 14, "premium"),
        ("Suport VIP adaptiv", "Interventii ghidate si ajustari dinamice zilnice.", 21, "vip"),
        ("Recovery executive", "Recuperare emotionala pentru ritm profesional intens.", 14, "vip"),
        ("Calm architecture", "Reconstruiesti stabilitatea prin pași zilnici foarte clari.", 30, "vip"),
    ],
}


def iter_program_seeds() -> list[ProgramSeed]:
    items: list[ProgramSeed] = []
    for category, rows in _CATALOG.items():
        for title, description, duration_days, plan_access in rows:
            items.append(
                ProgramSeed(
                    category=category,
                    title=title,
                    description=description,
                    duration_days=duration_days,
                    plan_access=plan_access,
                )
            )
    return items