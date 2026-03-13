"""Localized templates for user-facing email notifications."""

from __future__ import annotations

from core.i18n import translate


FALLBACK_NAMES = {
    "ro": "prietene",
    "en": "there",
    "de": "da",
    "fr": "ami",
    "it": "amico",
    "es": "amigo",
    "pl": "przyjacielu",
}


NOTIFICATION_TEMPLATES = {
    "trial_expiration_warning": {
        "ro": {
            "subject": "⏰ Doar {days_left} zile ramase din trialul gratuit!",
            "body": "Salut {name}!\n\nTrialul tau gratuit la Doisense expira in {days_left} zile.\n\nActiveaza un abonament pentru a pastra accesul la:\n✓ Chat AI nelimitat\n✓ Rapoarte si insight-uri\n✓ Planuri personalizate de wellbeing\n✓ Si multe altele\n\n=== Link rapid ===\n{url}\n\nCu grija,\nEchipa Doisense",
        },
        "en": {
            "subject": "⏰ Only {days_left} days left in your free trial!",
            "body": "Hi {name}!\n\nYour free trial at Doisense expires in {days_left} days.\n\nActivate a subscription to keep access to:\n✓ Unlimited AI chat\n✓ Reports and insights\n✓ Personalized wellbeing plans\n✓ And more\n\n=== Quick link ===\n{url}\n\nWarmly,\nThe Doisense Team",
        },
        "de": {
            "subject": "⏰ Nur noch {days_left} Tage in deiner kostenlosen Testphase!",
            "body": "Hallo {name}!\n\nDeine kostenlose Testphase bei Doisense endet in {days_left} Tagen.\n\nAktiviere ein Abonnement, um weiter Zugriff zu haben auf:\n✓ Unbegrenzten KI-Chat\n✓ Berichte und Erkenntnisse\n✓ Personalisierte Wellbeing-Plaene\n✓ Und mehr\n\n=== Direktlink ===\n{url}\n\nViele Gruesse,\nDas Doisense-Team",
        },
        "fr": {
            "subject": "⏰ Plus que {days_left} jours dans votre essai gratuit !",
            "body": "Bonjour {name} !\n\nVotre essai gratuit Doisense expire dans {days_left} jours.\n\nActivez un abonnement pour conserver l'acces a :\n✓ Chat IA illimite\n✓ Rapports et analyses\n✓ Plans de bien-etre personnalises\n✓ Et plus encore\n\n=== Lien rapide ===\n{url}\n\nBien a vous,\nL'equipe Doisense",
        },
        "it": {
            "subject": "⏰ Mancano solo {days_left} giorni alla fine della prova gratuita!",
            "body": "Ciao {name}!\n\nLa tua prova gratuita Doisense scade tra {days_left} giorni.\n\nAttiva un abbonamento per continuare ad avere accesso a:\n✓ Chat AI illimitata\n✓ Report e insight\n✓ Piani personalizzati di wellbeing\n✓ E molto altro\n\n=== Link rapido ===\n{url}\n\nA presto,\nIl team Doisense",
        },
        "es": {
            "subject": "⏰ Solo quedan {days_left} dias de tu prueba gratuita!",
            "body": "Hola {name}!\n\nTu prueba gratuita de Doisense termina en {days_left} dias.\n\nActiva una suscripcion para conservar acceso a:\n✓ Chat AI ilimitado\n✓ Informes e insights\n✓ Planes personalizados de bienestar\n✓ Y mas\n\n=== Enlace rapido ===\n{url}\n\nUn saludo,\nEl equipo Doisense",
        },
        "pl": {
            "subject": "⏰ Do konca darmowego okresu probnego zostalo tylko {days_left} dni!",
            "body": "Czesc {name}!\n\nTwoj darmowy okres probny w Doisense konczy sie za {days_left} dni.\n\nAktywuj subskrypcje, aby zachowac dostep do:\n✓ Nielimitowanego chatu AI\n✓ Raportow i wnioskow\n✓ Spersonalizowanych planow dobrostanu\n✓ I wielu innych funkcji\n\n=== Szybki link ===\n{url}\n\nPozdrawiamy,\nZespol Doisense",
        },
    },
    "inactivity_reminder": {
        "ro": {
            "subject": "❤️ Ne lipsesti! Revino pe Doisense",
            "body": "Salut {name}!\n\nNu te-am mai vazut pe platforma de {days_inactive} zile.\n\nDoisense te poate ajuta zilnic cu:\n✓ Gestionarea stresului\n✓ Obiceiuri sanatoase\n✓ Intelegerea emotiilor\n✓ Obiective personale\n\n=== Intra acum ===\n{url}\n\nTe asteptam,\nDoisense",
        },
        "en": {
            "subject": "❤️ We miss you! Come back to Doisense",
            "body": "Hi {name}!\n\nWe have not seen you on Doisense for {days_inactive} days.\n\nDaily support for:\n✓ Stress management\n✓ Healthy habits\n✓ Better emotional understanding\n✓ Personal goals\n\n=== Jump back in ===\n{url}\n\nSee you soon,\nDoisense",
        },
        "de": {
            "subject": "❤️ Wir vermissen dich! Komm zu Doisense zurueck",
            "body": "Hallo {name}!\n\nWir haben dich seit {days_inactive} Tagen nicht mehr auf Doisense gesehen.\n\nTaegliche Unterstuetzung bei:\n✓ Stressmanagement\n✓ Gesunden Gewohnheiten\n✓ Besserem Verstaendnis deiner Emotionen\n✓ Persoenlichen Zielen\n\n=== Jetzt zurueckkehren ===\n{url}\n\nBis bald,\nDoisense",
        },
        "fr": {
            "subject": "❤️ Vous nous manquez ! Revenez sur Doisense",
            "body": "Bonjour {name} !\n\nNous ne vous avons pas vu sur Doisense depuis {days_inactive} jours.\n\nUn soutien quotidien pour :\n✓ La gestion du stress\n✓ Les habitudes saines\n✓ Une meilleure comprehension emotionnelle\n✓ Les objectifs personnels\n\n=== Revenir maintenant ===\n{url}\n\nA bientot,\nDoisense",
        },
        "it": {
            "subject": "❤️ Ci manchi! Torna su Doisense",
            "body": "Ciao {name}!\n\nNon ti vediamo su Doisense da {days_inactive} giorni.\n\nSupporto quotidiano per:\n✓ Gestione dello stress\n✓ Abitudini sane\n✓ Maggiore consapevolezza emotiva\n✓ Obiettivi personali\n\n=== Torna ora ===\n{url}\n\nA presto,\nDoisense",
        },
        "es": {
            "subject": "❤️ Te echamos de menos! Vuelve a Doisense",
            "body": "Hola {name}!\n\nNo te hemos visto en Doisense desde hace {days_inactive} dias.\n\nApoyo diario para:\n✓ Gestionar el estres\n✓ Crear habitos saludables\n✓ Comprender mejor tus emociones\n✓ Alcanzar tus objetivos personales\n\n=== Volver ahora ===\n{url}\n\nHasta pronto,\nDoisense",
        },
        "pl": {
            "subject": "❤️ Brakuje nam Ciebie! Wroc do Doisense",
            "body": "Czesc {name}!\n\nNie widzielismy Cie w Doisense od {days_inactive} dni.\n\nCodzienne wsparcie w obszarach:\n✓ Zarzadzanie stresem\n✓ Zdrowe nawyki\n✓ Lepsze rozumienie emocji\n✓ Cele osobiste\n\n=== Wroc teraz ===\n{url}\n\nDo zobaczenia,\nDoisense",
        },
    },
    "journal_reminder": {
        "ro": {
            "subject": "📔 Reflexia zilei - ce ai pe gand azi?",
            "body": "Salut {name}!\n\nNu ai scris in jurnal astazi. E un moment bun pentru reflectie.\n\nRaspunde la intrebarile personalizate si:\n✓ Intelege-ti emotiile mai bine\n✓ Observa tipare personale\n✓ Construieste progres real\n\n=== Deschide jurnalul ===\n{url}\n\nReflectie buna,\nDoisense",
        },
        "en": {
            "subject": "📔 Reflection prompt - what's on your mind today?",
            "body": "Hi {name}!\n\nYou have not made a journal entry today yet. This is a good moment for reflection.\n\nAnswer personalized prompts and:\n✓ Understand your emotions better\n✓ Spot personal patterns\n✓ Build real progress\n\n=== Open journal ===\n{url}\n\nToday's reflection,\nDoisense",
        },
        "de": {
            "subject": "📔 Reflexionsimpuls - was beschaeftigt dich heute?",
            "body": "Hallo {name}!\n\nDu hast heute noch keinen Tagebucheintrag erstellt. Das ist ein guter Moment fuer Reflexion.\n\nBeantworte persoenliche Fragen und:\n✓ Verstehe deine Emotionen besser\n✓ Erkenne Muster\n✓ Baue echten Fortschritt auf\n\n=== Tagebuch oeffnen ===\n{url}\n\nEine gute Reflexion,\nDoisense",
        },
        "fr": {
            "subject": "📔 Invitation a la reflexion - que ressentez-vous aujourd'hui ?",
            "body": "Bonjour {name} !\n\nVous n'avez pas encore ecrit dans votre journal aujourd'hui. C'est un bon moment pour reflechir.\n\nRepondez aux invites personnalisees et :\n✓ Comprenez mieux vos emotions\n✓ Reperez vos schémas\n✓ Construisez un vrai progres\n\n=== Ouvrir le journal ===\n{url}\n\nBonne reflexion,\nDoisense",
        },
        "it": {
            "subject": "📔 Spunto di riflessione - cosa hai in mente oggi?",
            "body": "Ciao {name}!\n\nNon hai ancora scritto nel diario oggi. E un buon momento per fermarti a riflettere.\n\nRispondi ai prompt personalizzati e:\n✓ Comprendi meglio le tue emozioni\n✓ Riconosci i tuoi schemi\n✓ Costruisci un progresso reale\n\n=== Apri il diario ===\n{url}\n\nBuona riflessione,\nDoisense",
        },
        "es": {
            "subject": "📔 Propuesta de reflexion - que tienes en mente hoy?",
            "body": "Hola {name}!\n\nTodavia no has escrito en tu diario hoy. Es un buen momento para reflexionar.\n\nResponde a las preguntas personalizadas y:\n✓ Entiende mejor tus emociones\n✓ Detecta tus patrones\n✓ Construye progreso real\n\n=== Abrir diario ===\n{url}\n\nBuena reflexion,\nDoisense",
        },
        "pl": {
            "subject": "📔 Pytanie do refleksji - co masz dzisiaj na mysli?",
            "body": "Czesc {name}!\n\nNie dodales jeszcze dzis wpisu do dziennika. To dobry moment na refleksje.\n\nOdpowiedz na spersonalizowane pytania i:\n✓ Lepiej zrozum swoje emocje\n✓ Zauwaz wlasne schematy\n✓ Buduj realny postep\n\n=== Otworz dziennik ===\n{url}\n\nDobrej refleksji,\nDoisense",
        },
    },
    "daily_plan_reminder": {
        "ro": {
            "subject": "🎯 Planul tau pentru azi - esti gata?",
            "body": "Salut {name}!\n\nRezerva 2 minute pentru a-ti planifica ziua:\n✓ Ce 1-3 lucruri vrei sa realizezi?\n✓ Ce iti da energie?\n✓ Cum iti marchezi reusitele?\n\n=== Planifica azi ===\n{url}\n\nSucces,\nDoisense",
        },
        "en": {
            "subject": "🎯 Your plan for today - ready?",
            "body": "Hi {name}!\n\nTake 2 minutes to plan your day:\n✓ What 1-3 things do you want to achieve?\n✓ What will give you energy?\n✓ How will you mark your wins?\n\n=== Plan today ===\n{url}\n\nGo for it,\nDoisense",
        },
        "de": {
            "subject": "🎯 Dein Plan fuer heute - bereit?",
            "body": "Hallo {name}!\n\nNimm dir 2 Minuten fuer deinen Tagesplan:\n✓ Welche 1-3 Dinge willst du erreichen?\n✓ Was gibt dir Energie?\n✓ Wie feierst du deine Erfolge?\n\n=== Heute planen ===\n{url}\n\nViel Erfolg,\nDoisense",
        },
        "fr": {
            "subject": "🎯 Votre plan pour aujourd'hui - pret ?",
            "body": "Bonjour {name} !\n\nPrenez 2 minutes pour planifier votre journee :\n✓ Quelles 1 a 3 choses voulez-vous accomplir ?\n✓ Qu'est-ce qui vous donne de l'energie ?\n✓ Comment celebrerez-vous vos progres ?\n\n=== Planifier aujourd'hui ===\n{url}\n\nBon courage,\nDoisense",
        },
        "it": {
            "subject": "🎯 Il tuo piano per oggi - pronto?",
            "body": "Ciao {name}!\n\nDedica 2 minuti a pianificare la giornata:\n✓ Quali 1-3 cose vuoi realizzare?\n✓ Cosa ti dara energia?\n✓ Come celebrerai i tuoi progressi?\n\n=== Pianifica oggi ===\n{url}\n\nBuon lavoro,\nDoisense",
        },
        "es": {
            "subject": "🎯 Tu plan para hoy - listo?",
            "body": "Hola {name}!\n\nDedica 2 minutos a planificar tu dia:\n✓ Que 1-3 cosas quieres lograr?\n✓ Que te dara energia?\n✓ Como celebrarás tus avances?\n\n=== Planifica hoy ===\n{url}\n\nA por ello,\nDoisense",
        },
        "pl": {
            "subject": "🎯 Twoj plan na dzis - gotowy?",
            "body": "Czesc {name}!\n\nPoswiec 2 minuty na zaplanowanie dnia:\n✓ Jakie 1-3 rzeczy chcesz osiagnac?\n✓ Co da Ci energie?\n✓ Jak uczcisz swoje sukcesy?\n\n=== Zaplanuj dzis ===\n{url}\n\nPowodzenia,\nDoisense",
        },
    },
    "wellbeing_checkin_reminder": {
        "ro": {
            "subject": "💚 Check-in-ul zilei - cum te simti?",
            "body": "Salut {name}!\n\nIa un minut pentru check-in-ul de azi:\n✓ Cum te simti emotional?\n✓ Care este nivelul tau de energie?\n✓ Ce te-ar ajuta azi?\n\n=== Check-in acum ===\n{url}\n\nCu grija,\nDoisense",
        },
        "en": {
            "subject": "💚 Today's check-in - how are you feeling?",
            "body": "Hi {name}!\n\nTake one minute for today's check-in:\n✓ How are you feeling emotionally?\n✓ What is your energy level?\n✓ What would help today?\n\n=== Check in now ===\n{url}\n\nTake care,\nDoisense",
        },
        "de": {
            "subject": "💚 Heutiger Check-in - wie fuehlst du dich?",
            "body": "Hallo {name}!\n\nNimm dir eine Minute fuer den heutigen Check-in:\n✓ Wie fuehlst du dich emotional?\n✓ Wie ist dein Energielevel?\n✓ Was wuerde dir heute helfen?\n\n=== Jetzt einchecken ===\n{url}\n\nPass gut auf dich auf,\nDoisense",
        },
        "fr": {
            "subject": "💚 Check-in du jour - comment vous sentez-vous ?",
            "body": "Bonjour {name} !\n\nPrenez une minute pour le check-in d'aujourd'hui :\n✓ Comment vous sentez-vous ?\n✓ Quel est votre niveau d'energie ?\n✓ Qu'est-ce qui vous aiderait aujourd'hui ?\n\n=== Faire le check-in ===\n{url}\n\nPrenez soin de vous,\nDoisense",
        },
        "it": {
            "subject": "💚 Check-in del giorno - come ti senti?",
            "body": "Ciao {name}!\n\nPrenditi un minuto per il check-in di oggi:\n✓ Come ti senti emotivamente?\n✓ Qual e il tuo livello di energia?\n✓ Cosa ti aiuterebbe oggi?\n\n=== Fai il check-in ===\n{url}\n\nAbbi cura di te,\nDoisense",
        },
        "es": {
            "subject": "💚 Check-in de hoy - como te sientes?",
            "body": "Hola {name}!\n\nToma un minuto para el check-in de hoy:\n✓ Como te sientes emocionalmente?\n✓ Cual es tu nivel de energia?\n✓ Que te ayudaria hoy?\n\n=== Hacer check-in ===\n{url}\n\nCuidate,\nDoisense",
        },
        "pl": {
            "subject": "💚 Dzisiejszy check-in - jak sie czujesz?",
            "body": "Czesc {name}!\n\nPoswiec minute na dzisiejszy check-in:\n✓ Jak sie czujesz emocjonalnie?\n✓ Jaki jest Twoj poziom energii?\n✓ Co pomogloby Ci dzisiaj?\n\n=== Zrob check-in ===\n{url}\n\nDbaj o siebie,\nDoisense",
        },
    },
    "upgrade_recommendation_journal_limit": {
        "ro": {
            "subject": "📊 Acceseaza mai multe intrebari cu PREMIUM",
            "body": "Salut {name}!\n\nTi-au placut intrebarile din jurnal? PREMIUM iti ofera:\n✓ Peste 50 de intrebari de reflectie\n✓ Integrare cu AI coach\n✓ Rapoarte de progres\n✓ Analize emotionale\n\n=== Upgrade acum ===\n{url}",
        },
        "en": {
            "subject": "📊 Unlock more journal prompts with PREMIUM",
            "body": "Hi {name}!\n\nEnjoyed the journal prompts? PREMIUM unlocks:\n✓ 50+ reflection questions\n✓ AI coach integration\n✓ Progress reports\n✓ Emotional insights\n\n=== Upgrade now ===\n{url}",
        },
        "de": {
            "subject": "📊 Mehr Journalfragen mit PREMIUM freischalten",
            "body": "Hallo {name}!\n\nDir gefallen die Journalfragen? Mit PREMIUM bekommst du:\n✓ 50+ Reflexionsfragen\n✓ KI-Coach-Integration\n✓ Fortschrittsberichte\n✓ Emotionale Einblicke\n\n=== Jetzt upgraden ===\n{url}",
        },
        "fr": {
            "subject": "📊 Debloquez plus de questions avec PREMIUM",
            "body": "Bonjour {name} !\n\nVous aimez les questions du journal ? PREMIUM vous donne acces a :\n✓ 50+ questions de reflexion\n✓ Integration avec le coach IA\n✓ Rapports de progression\n✓ Analyses emotionnelles\n\n=== Passer a PREMIUM ===\n{url}",
        },
        "it": {
            "subject": "📊 Sblocca piu domande con PREMIUM",
            "body": "Ciao {name}!\n\nTi sono piaciuti i prompt del diario? PREMIUM sblocca:\n✓ Oltre 50 domande di riflessione\n✓ Integrazione con AI coach\n✓ Report di progresso\n✓ Insight emotivi\n\n=== Passa a PREMIUM ===\n{url}",
        },
        "es": {
            "subject": "📊 Desbloquea mas preguntas con PREMIUM",
            "body": "Hola {name}!\n\nTe gustaron las preguntas del diario? PREMIUM desbloquea:\n✓ Mas de 50 preguntas de reflexion\n✓ Integracion con AI coach\n✓ Informes de progreso\n✓ Analisis emocionales\n\n=== Haz upgrade ahora ===\n{url}",
        },
        "pl": {
            "subject": "📊 Odblokuj wiecej pytan z PREMIUM",
            "body": "Czesc {name}!\n\nSpodobaly Ci sie pytania z dziennika? PREMIUM odblokowuje:\n✓ Ponad 50 pytan refleksyjnych\n✓ Integracje z AI coachem\n✓ Raporty postepu\n✓ Wglad emocjonalny\n\n=== Zmien plan teraz ===\n{url}",
        },
    },
    "upgrade_recommendation_report_limit": {
        "ro": {
            "subject": "📈 Deblocheaza rapoarte detaliate cu PREMIUM",
            "body": "Salut {name}!\n\nPREMIUM iti ofera:\n✓ Rapoarte zilnice\n✓ Analize saptamanale\n✓ Tipare comportamentale\n✓ Recomandari bazate pe AI\n\n=== Upgrade acum ===\n{url}",
        },
        "en": {
            "subject": "📈 Unlock detailed reports with PREMIUM",
            "body": "Hi {name}!\n\nPREMIUM gives you:\n✓ Daily reports\n✓ Weekly analysis\n✓ Behavioral patterns\n✓ AI-powered recommendations\n\n=== Upgrade now ===\n{url}",
        },
        "de": {
            "subject": "📈 Detaillierte Berichte mit PREMIUM freischalten",
            "body": "Hallo {name}!\n\nMit PREMIUM bekommst du:\n✓ Taegliche Berichte\n✓ Woechentliche Analysen\n✓ Verhaltensmuster\n✓ KI-basierte Empfehlungen\n\n=== Jetzt upgraden ===\n{url}",
        },
        "fr": {
            "subject": "📈 Debloquez des rapports detailles avec PREMIUM",
            "body": "Bonjour {name} !\n\nPREMIUM vous donne acces a :\n✓ Rapports quotidiens\n✓ Analyses hebdomadaires\n✓ Schemas comportementaux\n✓ Recommandations basees sur l'IA\n\n=== Passer a PREMIUM ===\n{url}",
        },
        "it": {
            "subject": "📈 Sblocca report dettagliati con PREMIUM",
            "body": "Ciao {name}!\n\nCon PREMIUM ottieni:\n✓ Report giornalieri\n✓ Analisi settimanali\n✓ Pattern comportamentali\n✓ Raccomandazioni basate sull'AI\n\n=== Passa a PREMIUM ===\n{url}",
        },
        "es": {
            "subject": "📈 Desbloquea informes detallados con PREMIUM",
            "body": "Hola {name}!\n\nCon PREMIUM obtienes:\n✓ Informes diarios\n✓ Analisis semanales\n✓ Patrones de comportamiento\n✓ Recomendaciones con IA\n\n=== Haz upgrade ahora ===\n{url}",
        },
        "pl": {
            "subject": "📈 Odblokuj szczegolowe raporty z PREMIUM",
            "body": "Czesc {name}!\n\nPREMIUM daje Ci:\n✓ Codzienne raporty\n✓ Tygodniowe analizy\n✓ Wzorce zachowan\n✓ Rekomendacje oparte na AI\n\n=== Zmien plan teraz ===\n{url}",
        },
    },
    "upgrade_recommendation_generic": {
        "ro": {
            "subject": "⭐ Descopera mai mult cu PREMIUM",
            "body": "Salut {name}!\n\nCu PREMIUM obtii:\n✓ Chat AI nelimitat\n✓ Rapoarte detaliate\n✓ Planuri personalizate\n✓ Prioritate in suport\n\n=== Upgrade acum ===\n{url}",
        },
        "en": {
            "subject": "⭐ Unlock more with PREMIUM",
            "body": "Hi {name}!\n\nWith PREMIUM you get:\n✓ Unlimited AI chat\n✓ Detailed reports\n✓ Personalized plans\n✓ Priority support\n\n=== Upgrade now ===\n{url}",
        },
        "de": {
            "subject": "⭐ Entdecke mehr mit PREMIUM",
            "body": "Hallo {name}!\n\nMit PREMIUM bekommst du:\n✓ Unbegrenzten KI-Chat\n✓ Detaillierte Berichte\n✓ Personalisierte Plaene\n✓ Priorisierten Support\n\n=== Jetzt upgraden ===\n{url}",
        },
        "fr": {
            "subject": "⭐ Decouvrez plus avec PREMIUM",
            "body": "Bonjour {name} !\n\nAvec PREMIUM, vous obtenez :\n✓ Chat IA illimite\n✓ Rapports detailles\n✓ Plans personnalises\n✓ Support prioritaire\n\n=== Passer a PREMIUM ===\n{url}",
        },
        "it": {
            "subject": "⭐ Scopri di piu con PREMIUM",
            "body": "Ciao {name}!\n\nCon PREMIUM ottieni:\n✓ Chat AI illimitata\n✓ Report dettagliati\n✓ Piani personalizzati\n✓ Supporto prioritario\n\n=== Passa a PREMIUM ===\n{url}",
        },
        "es": {
            "subject": "⭐ Descubre mas con PREMIUM",
            "body": "Hola {name}!\n\nCon PREMIUM obtienes:\n✓ Chat AI ilimitado\n✓ Informes detallados\n✓ Planes personalizados\n✓ Soporte prioritario\n\n=== Haz upgrade ahora ===\n{url}",
        },
        "pl": {
            "subject": "⭐ Odkryj wiecej z PREMIUM",
            "body": "Czesc {name}!\n\nZ PREMIUM otrzymujesz:\n✓ Nielimitowany chat AI\n✓ Szczegolowe raporty\n✓ Spersonalizowane plany\n✓ Priorytetowe wsparcie\n\n=== Zmien plan teraz ===\n{url}",
        },
    },
    "goal_reminder": {
        "ro": {
            "subject": "🎯 Revino la obiectivele tale cu un pas mic",
            "body": "Salut {name}!\n\nNu ai mai revenit la obiectivele tale de {days_since_focus} zile.\n\nObiective active:\n{goal_lines}\n\nUn check-in scurt te poate ajuta sa:\n✓ clarifici ce conteaza azi\n✓ alegi un pas realist\n✓ mentii ritmul fara presiune\n\n=== Revino la focus ===\n{url}\n\nCu rabdare,\nDoisense",
        },
        "en": {
            "subject": "🎯 Reconnect with your goals through one small step",
            "body": "Hi {name}!\n\nYou have not revisited your goals in {days_since_focus} days.\n\nActive goals:\n{goal_lines}\n\nA short check-in can help you:\n✓ clarify what matters today\n✓ choose one realistic next step\n✓ keep momentum without pressure\n\n=== Refocus now ===\n{url}\n\nWarmly,\nDoisense",
        },
        "de": {
            "subject": "🎯 Finde mit einem kleinen Schritt zu deinen Zielen zurueck",
            "body": "Hallo {name}!\n\nDu hast dich seit {days_since_focus} Tagen nicht mehr auf deine Ziele konzentriert.\n\nAktive Ziele:\n{goal_lines}\n\nEin kurzer Check-in kann dir helfen:\n✓ zu klaeren, was heute wichtig ist\n✓ einen realistischen naechsten Schritt zu waehlen\n✓ dran zu bleiben, ohne Druck\n\n=== Fokus wiederfinden ===\n{url}\n\nMit Geduld,\nDoisense",
        },
        "fr": {
            "subject": "🎯 Revenez a vos objectifs avec une petite action",
            "body": "Bonjour {name} !\n\nVous n'avez pas repris vos objectifs depuis {days_since_focus} jours.\n\nObjectifs actifs :\n{goal_lines}\n\nUn court check-in peut vous aider a :\n✓ clarifier ce qui compte aujourd'hui\n✓ choisir une prochaine etape realiste\n✓ garder le rythme sans pression\n\n=== Reprendre le focus ===\n{url}\n\nAvec bienveillance,\nDoisense",
        },
        "it": {
            "subject": "🎯 Torna ai tuoi obiettivi con un piccolo passo",
            "body": "Ciao {name}!\n\nNon torni sui tuoi obiettivi da {days_since_focus} giorni.\n\nObiettivi attivi:\n{goal_lines}\n\nUn breve check-in puo aiutarti a:\n✓ chiarire cosa conta oggi\n✓ scegliere un prossimo passo realistico\n✓ mantenere continuita senza pressione\n\n=== Ritrova il focus ===\n{url}\n\nCon calma,\nDoisense",
        },
        "es": {
            "subject": "🎯 Vuelve a tus objetivos con un pequeno paso",
            "body": "Hola {name}!\n\nNo has vuelto a tus objetivos desde hace {days_since_focus} dias.\n\nObjetivos activos:\n{goal_lines}\n\nUn breve check-in puede ayudarte a:\n✓ aclarar lo importante de hoy\n✓ elegir un siguiente paso realista\n✓ mantener la continuidad sin presion\n\n=== Recuperar el foco ===\n{url}\n\nCon calma,\nDoisense",
        },
        "pl": {
            "subject": "🎯 Wroc do swoich celow jednym malym krokiem",
            "body": "Czesc {name}!\n\nNie wracales do swoich celow od {days_since_focus} dni.\n\nAktywne cele:\n{goal_lines}\n\nKrotki check-in moze pomoc Ci:\n✓ ustalic, co jest dzis wazne\n✓ wybrac realistyczny kolejny krok\n✓ utrzymac rytm bez presji\n\n=== Wroc do fokus ===\n{url}\n\nZ cierpliwoscia,\nDoisense",
        },
    },
    "payment_failed_notification": {
        "ro": {
            "subject": "Problema la plata abonamentului",
            "body": "Salut {name}!\n\nNu am putut procesa ultima plata pentru abonamentul tau.\n\nTe rugam sa verifici metoda de plata si sa actualizezi datele din portalul de billing.\n\n=== Actualizeaza plata ===\n{url}\n\nDoisense",
        },
        "en": {
            "subject": "Subscription payment failed",
            "body": "Hi {name}!\n\nWe could not process your latest subscription payment.\n\nPlease review your payment method and update your billing details.\n\n=== Update payment method ===\n{url}\n\nDoisense",
        },
        "de": {
            "subject": "Zahlung fuer dein Abonnement fehlgeschlagen",
            "body": "Hallo {name}!\n\nWir konnten deine letzte Abonnementzahlung nicht verarbeiten.\n\nBitte pruefe deine Zahlungsmethode und aktualisiere die Zahlungsdaten.\n\n=== Zahlungsmethode aktualisieren ===\n{url}\n\nDoisense",
        },
        "fr": {
            "subject": "Echec du paiement de votre abonnement",
            "body": "Bonjour {name} !\n\nNous n'avons pas pu traiter votre dernier paiement d'abonnement.\n\nMerci de verifier votre moyen de paiement et de mettre a jour vos informations de facturation.\n\n=== Mettre a jour le paiement ===\n{url}\n\nDoisense",
        },
        "it": {
            "subject": "Pagamento dell'abbonamento non riuscito",
            "body": "Ciao {name}!\n\nNon siamo riusciti a elaborare l'ultimo pagamento del tuo abbonamento.\n\nControlla il metodo di pagamento e aggiorna i dati di fatturazione.\n\n=== Aggiorna il pagamento ===\n{url}\n\nDoisense",
        },
        "es": {
            "subject": "Fallo en el pago de tu suscripcion",
            "body": "Hola {name}!\n\nNo pudimos procesar el ultimo pago de tu suscripcion.\n\nRevisa tu metodo de pago y actualiza los datos de facturacion.\n\n=== Actualizar pago ===\n{url}\n\nDoisense",
        },
        "pl": {
            "subject": "Platnosc za subskrypcje nie powiodla sie",
            "body": "Czesc {name}!\n\nNie udalo sie przetworzyc ostatniej platnosci za subskrypcje.\n\nSprawdz metode platnosci i zaktualizuj dane rozliczeniowe.\n\n=== Zaktualizuj platnosc ===\n{url}\n\nDoisense",
        },
    },
    "payment_expiring_notification": {
        "ro": {
            "subject": "Abonamentul tau expira curand",
            "body": "Salut {name}!\n\nAbonamentul tau este programat sa expire la data de {end_label}.\n\nDaca vrei sa pastrezi accesul premium, verifica statusul abonamentului in cont.\n\n=== Vezi abonamentul ===\n{url}\n\nDoisense",
        },
        "en": {
            "subject": "Your subscription is expiring soon",
            "body": "Hi {name}!\n\nYour subscription is scheduled to end on {end_label}.\n\nIf you want to keep premium access, review your subscription status in your account.\n\n=== Review subscription ===\n{url}\n\nDoisense",
        },
        "de": {
            "subject": "Dein Abonnement endet bald",
            "body": "Hallo {name}!\n\nDein Abonnement endet voraussichtlich am {end_label}.\n\nWenn du den Premium-Zugang behalten moechtest, pruefe den Status in deinem Konto.\n\n=== Abonnement ansehen ===\n{url}\n\nDoisense",
        },
        "fr": {
            "subject": "Votre abonnement expire bientot",
            "body": "Bonjour {name} !\n\nVotre abonnement doit se terminer le {end_label}.\n\nSi vous souhaitez conserver l'acces premium, verifiez son statut dans votre compte.\n\n=== Voir l'abonnement ===\n{url}\n\nDoisense",
        },
        "it": {
            "subject": "Il tuo abbonamento sta per scadere",
            "body": "Ciao {name}!\n\nIl tuo abbonamento terminera il {end_label}.\n\nSe vuoi mantenere l'accesso premium, controlla lo stato nel tuo account.\n\n=== Vedi abbonamento ===\n{url}\n\nDoisense",
        },
        "es": {
            "subject": "Tu suscripcion vence pronto",
            "body": "Hola {name}!\n\nTu suscripcion esta programada para terminar el {end_label}.\n\nSi quieres mantener el acceso premium, revisa el estado en tu cuenta.\n\n=== Ver suscripcion ===\n{url}\n\nDoisense",
        },
        "pl": {
            "subject": "Twoja subskrypcja wkrótce wygasa",
            "body": "Czesc {name}!\n\nTwoja subskrypcja ma zakonczyc sie {end_label}.\n\nJesli chcesz zachowac dostep premium, sprawdz status subskrypcji w koncie.\n\n=== Zobacz subskrypcje ===\n{url}\n\nDoisense",
        },
    },
    "payment_invalid_method_notification": {
        "ro": {
            "subject": "Metoda ta de plata necesita actualizare",
            "body": "Salut {name}!\n\nMetoda de plata asociata abonamentului tau pare invalida sau aproape de expirare.\n\nAdauga o metoda valida pentru a evita intreruperea accesului premium.\n\n=== Actualizeaza metoda de plata ===\n{url}\n\nDoisense",
        },
        "en": {
            "subject": "Your payment method needs an update",
            "body": "Hi {name}!\n\nYour subscription payment method appears invalid or close to expiry.\n\nPlease add a valid payment method to avoid premium access interruption.\n\n=== Update payment method ===\n{url}\n\nDoisense",
        },
        "de": {
            "subject": "Deine Zahlungsmethode muss aktualisiert werden",
            "body": "Hallo {name}!\n\nDeine Zahlungsmethode fuer das Abonnement scheint ungueltig oder bald ablaufend zu sein.\n\nBitte hinterlege eine gueltige Zahlungsmethode, damit dein Premium-Zugang nicht unterbrochen wird.\n\n=== Zahlungsmethode aktualisieren ===\n{url}\n\nDoisense",
        },
        "fr": {
            "subject": "Votre moyen de paiement doit etre mis a jour",
            "body": "Bonjour {name} !\n\nLe moyen de paiement associe a votre abonnement semble invalide ou proche de l'expiration.\n\nAjoutez un moyen de paiement valide pour eviter une interruption de l'acces premium.\n\n=== Mettre a jour le paiement ===\n{url}\n\nDoisense",
        },
        "it": {
            "subject": "Il tuo metodo di pagamento deve essere aggiornato",
            "body": "Ciao {name}!\n\nIl metodo di pagamento associato al tuo abbonamento sembra non valido o vicino alla scadenza.\n\nAggiungi un metodo valido per evitare interruzioni dell'accesso premium.\n\n=== Aggiorna il pagamento ===\n{url}\n\nDoisense",
        },
        "es": {
            "subject": "Tu metodo de pago necesita una actualizacion",
            "body": "Hola {name}!\n\nEl metodo de pago de tu suscripcion parece invalido o cercano a su vencimiento.\n\nAgrega un metodo valido para evitar una interrupcion del acceso premium.\n\n=== Actualizar metodo de pago ===\n{url}\n\nDoisense",
        },
        "pl": {
            "subject": "Twoja metoda platnosci wymaga aktualizacji",
            "body": "Czesc {name}!\n\nMetoda platnosci przypisana do subskrypcji wydaje sie niewazna lub bliska wygasniecia.\n\nDodaj prawidlowa metode platnosci, aby uniknac przerwania dostepu premium.\n\n=== Zaktualizuj metode platnosci ===\n{url}\n\nDoisense",
        },
    },
}


def render_notification(kind: str, language: str, **kwargs) -> dict[str, str]:
    templates = translate(NOTIFICATION_TEMPLATES[kind], language)
    payload = dict(kwargs)
    payload.setdefault("name", kwargs.get("first_name") or translate(FALLBACK_NAMES, language))
    return {
        "subject": templates["subject"].format(**payload),
        "body": templates["body"].format(**payload),
    }