from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import re

app = FastAPI(title="WeeFizz Chatbot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── FAQ bilingue ──────────────────────────────────────────────────────────────
FAQ = [
    {
        "keywords_fr": ["weefizz", "c'est quoi", "qu'est-ce", "application", "présenter"],
        "keywords_en": ["what is", "weefizz", "about", "application"],
        "answer_fr": (
            "WeeFizz est une application qui analyse votre morphologie pour vous recommander "
            "la taille idéale dans les vêtements.\n\n"
            "Elle utilise vos mensurations (taille, poids, âge, silhouette) pour calculer "
            "vos tailles avec précision et réduire les erreurs de commande."
        ),
        "answer_en": (
            "WeeFizz is an app that analyzes your body shape to recommend your ideal clothing size.\n\n"
            "It uses your measurements (height, weight, age, silhouette) to accurately calculate "
            "your sizes and reduce ordering mistakes."
        ),
    },
    {
        "keywords_fr": ["démarrer", "commencer", "comment ça marche", "étapes", "début", "premier"],
        "keywords_en": ["start", "begin", "how does it work", "steps", "first", "getting started"],
        "answer_fr": (
            "Pour démarrer sur WeeFizz :\n\n"
            "1. Acceptez la politique de confidentialité (CGU)\n"
            "2. Entrez votre prénom et nom\n"
            "3. Choisissez la méthode : saisie manuelle ou photo\n"
            "4. Remplissez votre profil morphologique\n"
            "5. Obtenez vos recommandations de taille !"
        ),
        "answer_en": (
            "To get started on WeeFizz:\n\n"
            "1. Accept the privacy policy (Terms of Use)\n"
            "2. Enter your first and last name\n"
            "3. Choose your method: manual input or photo\n"
            "4. Fill in your body profile\n"
            "5. Get your size recommendations!"
        ),
    },
    {
        "keywords_fr": ["taille", "hauteur", "mesurer ma taille", "cm", "centimètre", "inch", "pouce"],
        "keywords_en": ["height", "tall", "measure height", "cm", "centimeter", "inch"],
        "answer_fr": (
            "Votre taille doit être mesurée debout, sans chaussures, dos contre un mur.\n\n"
            "Sur WeeFizz, déplacez le curseur jusqu'à votre valeur. "
            "Vous pouvez choisir entre centimètres (Cm) et pouces (In).\n\n"
            "Une approximation à ±2 cm est suffisante."
        ),
        "answer_en": (
            "Your height should be measured standing straight, without shoes, back against a wall.\n\n"
            "On WeeFizz, slide the ruler to your value. "
            "You can choose between centimeters (Cm) or inches (In).\n\n"
            "An approximation within ±2 cm is fine."
        ),
    },
    {
        "keywords_fr": ["poids", "peser", "kg", "kilo", "lb", "livre", "masse"],
        "keywords_en": ["weight", "kg", "kilo", "lb", "pound", "mass"],
        "answer_fr": (
            "Votre poids peut être entré en kilogrammes (Kg) ou en livres (Lb).\n\n"
            "Choisissez l'unité que vous utilisez habituellement — WeeFizz s'adapte automatiquement."
        ),
        "answer_en": (
            "Your weight can be entered in kilograms (Kg) or pounds (Lb).\n\n"
            "Choose the unit you normally use — WeeFizz adapts automatically."
        ),
    },
    {
        "keywords_fr": ["âge", "ans", "vieux", "jeune", "pourquoi âge"],
        "keywords_en": ["age", "years", "old", "young", "why age"],
        "answer_fr": (
            "L'âge influence les recommandations de taille car la morphologie du corps "
            "évolue avec le temps.\n\n"
            "WeeFizz utilise l'âge pour affiner le calcul. "
            "Cette donnée reste strictement confidentielle."
        ),
        "answer_en": (
            "Age influences size recommendations because body shape changes over time.\n\n"
            "WeeFizz uses your age to fine-tune the calculation. "
            "This data remains strictly confidential."
        ),
    },
    {
        "keywords_fr": ["silhouette", "hanche", "épaule", "abdomen", "morphologie", "forme du corps"],
        "keywords_en": ["silhouette", "hip", "shoulder", "abdomen", "body shape", "morphology"],
        "answer_fr": (
            "La silhouette décrit la forme de votre corps en deux parties :\n\n"
            "Hanches (par rapport à vos épaules) :\n"
            "  • Plus étroites que vos épaules\n"
            "  • De la même largeur\n"
            "  • Plus larges que vos épaules\n\n"
            "Abdomen (vu de profil) :\n"
            "  • Rentre légèrement vers l'intérieur\n"
            "  • Aligné avec la poitrine\n"
            "  • Plus large que vos hanches\n\n"
            "Regardez-vous de face et de côté dans un miroir pour choisir."
        ),
        "answer_en": (
            "Silhouette describes your body shape in two parts:\n\n"
            "Hips (compared to your shoulders):\n"
            "  • Narrower than your shoulders\n"
            "  • Same width as your shoulders\n"
            "  • Wider than your shoulders\n\n"
            "Abdomen (viewed from the side):\n"
            "  • Slightly tucked inward\n"
            "  • Aligned with your chest\n"
            "  • Wider than your hips\n\n"
            "Look at yourself in a mirror from the front and side to choose."
        ),
    },
    {
        "keywords_fr": ["photo", "caméra", "selfie", "différence", "méthode", "manuelle", "manuel"],
        "keywords_en": ["photo", "camera", "picture", "selfie", "difference", "method", "manual"],
        "answer_fr": (
            "WeeFizz propose deux méthodes :\n\n"
            "Saisie manuelle — vous entrez vos mensurations directement. Rapide, sans équipement.\n\n"
            "Avec photo — WeeFizz extrait automatiquement certaines données morphologiques. "
            "Utile si vous avez du mal à estimer votre silhouette.\n\n"
            "Les deux méthodes donnent des résultats fiables."
        ),
        "answer_en": (
            "WeeFizz offers two methods:\n\n"
            "Manual input — you enter your measurements directly. Fast, no equipment needed.\n\n"
            "With photo — WeeFizz automatically extracts body data from your photo. "
            "Useful if you're unsure about your silhouette.\n\n"
            "Both methods give reliable results."
        ),
    },
    {
        "keywords_fr": ["données", "sécurité", "confidentialité", "privé", "gdpr", "stocké", "partagé"],
        "keywords_en": ["data", "security", "privacy", "private", "gdpr", "stored", "shared", "secure"],
        "answer_fr": (
            "WeeFizz prend la protection des données très au sérieux :\n\n"
            "  • Données chiffrées de bout en bout\n"
            "  • Sécurisées par SSL\n"
            "  • Jamais partagées avec des tiers\n\n"
            "En acceptant les CGU, vous consentez à cette utilisation limitée de vos données."
        ),
        "answer_en": (
            "WeeFizz takes data protection very seriously:\n\n"
            "  • All data is end-to-end encrypted\n"
            "  • Secured by SSL\n"
            "  • Never shared with third parties\n\n"
            "By accepting the terms, you consent to this limited use of your body data."
        ),
    },
    {
        "keywords_fr": ["résultat", "recommandation", "taille recommandée", "affiche", "attendre"],
        "keywords_en": ["result", "recommendation", "recommended size", "output", "display", "wait"],
        "answer_fr": (
            "Une fois votre profil soumis, WeeFizz affiche vos recommandations "
            "de taille pour chaque produit disponible. Par exemple :\n\n"
            "  • Veste FEMME → 44/63.9\n"
            "  • Gilet FEMME → 46\n"
            "  • Pantalon FEMME → 40/80\n\n"
            "Le calcul prend quelques secondes."
        ),
        "answer_en": (
            "Once your profile is submitted, WeeFizz displays size recommendations "
            "for each available product. For example:\n\n"
            "  • Women's Jacket → 44/63.9\n"
            "  • Women's Vest → 46\n"
            "  • Women's Pants → 40/80\n\n"
            "The calculation takes just a few seconds."
        ),
    },
    {
        "keywords_fr": ["erreur", "bug", "marche pas", "problème", "bloqué", "javascript", "page blanche"],
        "keywords_en": ["error", "bug", "not working", "problem", "stuck", "javascript", "blank page"],
        "answer_fr": (
            "Si vous rencontrez un problème sur le formulaire WeeFizz :\n\n"
            "  • Vérifiez que JavaScript est activé dans votre navigateur\n"
            "  • Rafraîchissez la page (F5)\n"
            "  • Assurez-vous d'avoir accepté les CGU avant de cliquer sur 'Commencer'\n\n"
            "Si le problème persiste, envoyez-nous un message via le bouton ci-dessous."
        ),
        "answer_en": (
            "If you encounter a problem on the WeeFizz form:\n\n"
            "  • Make sure JavaScript is enabled in your browser\n"
            "  • Try refreshing the page (F5)\n"
            "  • Make sure you accepted the terms before clicking 'Start'\n\n"
            "If the problem persists, send us a message using the button below."
        ),
    },
    {
        "keywords_fr": ["cgu", "conditions", "politique", "accepter", "checkbox", "case à cocher"],
        "keywords_en": ["terms", "conditions", "policy", "accept", "checkbox", "tick"],
        "answer_fr": (
            "Sur la page d'accueil de WeeFizz, cochez la case en bas pour accepter "
            "la Politique de Confidentialité et les CGU.\n\n"
            "Le bouton 'Commencer' s'activera ensuite. "
            "Vous devez accepter les CGU pour démarrer le formulaire."
        ),
        "answer_en": (
            "On the WeeFizz home page, check the box at the bottom to accept "
            "the Privacy Policy and Terms of Use.\n\n"
            "The 'Start' button will then become active. "
            "You must accept the terms to start the form."
        ),
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────
def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9àâäéèêëîïôùûüç' ]", "", text.lower().strip())

def faq_match(message: str, lang: str):
    msg = normalize(message)
    key = f"keywords_{lang}"
    ans = f"answer_{lang}"
    for item in FAQ:
        if any(kw in msg for kw in item[key]):
            return item[ans]
    return None

# ── Schémas ───────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    message: str
    lang: str = "fr"

class ChatResponse(BaseModel):
    answer: str
    source: str        # "faq" | "unknown"
    email: str | None = None

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatMessage):
    lang = payload.lang if payload.lang in ("fr", "en") else "fr"
    answer = faq_match(payload.message, lang)

    if answer:
        return ChatResponse(answer=answer, source="faq")

    fallback_fr = (
        "Je n'ai pas de réponse à cette question pour l'instant.\n\n"
        "Cliquez sur le bouton ci-dessous pour nous envoyer votre question "
        "par e-mail — nous vous répondrons rapidement."
    )
    fallback_en = (
        "I don't have an answer to this question yet.\n\n"
        "Click the button below to send your question by email — "
        "we'll get back to you as soon as possible."
    )
    return ChatResponse(
        answer=fallback_fr if lang == "fr" else fallback_en,
        source="unknown",
        email="mayssafezai01@gmail.com",
    )

@app.get("/health")
async def health():
    return {"status": "ok"}