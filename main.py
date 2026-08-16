import os
import html
import time
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

# Configuration de l'URL API avec fallback propre
API_BASE_URL = os.environ.get("DOCMIND_API_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="DocMind AI — Douanes du Bénin",
    page_icon="images/Beninx-compressor-2-2.jpg",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Ajout du logo officiel en haut de la barre latérale
st.logo(
    "images/Beninx-compressor-2-2.jpg",
    size="medium",
)

# ------------------------------------------------------------------ #
# Chargement du style et de la Navbar
# ------------------------------------------------------------------ #
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Le fichier style.css est introuvable à la racine du projet.")

st.markdown("""
<div class="navbar">
    <div class="brand">
        Hɛnnu AI
    </div>
    <div class="nav-links">
        <span class="active">
            Assistant Douanier
        </span>
        <span>
            Audit & Contrôle
        </span>
        <span>
            Bibliothèque
        </span>
        <span>
            Documents
        </span>
    </div>
    <div class="nav-actions">
        <button>Se connecter</button>
        <button class="signup">S'inscrire</button>
    </div>
</div>
""", unsafe_allow_html=True)

# En-tête Principal

st.markdown(
    """
    <div class="docmind-header">
        <h1>Hɛnnu AI</h1>
        <p>Intelligence réglementaire douanière — La Douane Béninoise</p>
    </div>
    """,
    width='stretch',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ #
# Sidebar & Contrôles
# ------------------------------------------------------------------ #
with st.sidebar:
    st.header("Filtres de recherche")
    domain_filter = st.selectbox(
        "Domaine réglementaire",
        options=[None, "Douanes Benin", "CorridorCheck"],
        format_func=lambda v: "Tous les domaines" if v is None else v,
    )
    level_filter = st.segmented_control(
        "Niveau de précision",
        options=[None, "article", "section", "table"],
        format_func=lambda v: "Tous" if v is None else v.capitalize(),
        default=None,
    )

    st.space("medium")
    
    # Vérification du statut de l'API avec mise en cache courte
    @st.cache_data(ttl=30)
    def check_api_health(url: str) -> bool:
        try:
            r = requests.get(
                f"{url}/health",
                timeout=3)
            return r.status_code == 200 and r.json().get("status") == "ok"
        except requests.RequestException:
            return False

    api_ok = check_api_health(API_BASE_URL)
    if api_ok:
        st.markdown(":green-badge[API Connectée]")
    else:
        st.markdown(":red-badge[API Inaccessible]")

    st.space("small")

    if st.button("Effacer la conversation", icon=":material/delete:"):
        st.session_state.messages = []
        st.rerun()

## Fonctions de Service & Rendu
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, Any]] = []

if "chat_active" not in st.session_state:
    st.session_state.chat_active = False

def render_sources(sources: List[Dict[str, Any]]) -> None:
    """Affiche les cartes d'origine juridique avec échappement XSS."""
    if not sources:
        return
    
    stamps_list = []
    for s in sources:
        # Échappement HTML pour prévenir les failles XSS
        source_name = html.escape(str(s.get('source') or 'Source réglementaire'))
        article_num = s.get('article_number')
        
        art_str = f"Art. {html.escape(str(article_num))}" if article_num else ""
        
        stamps_list.append(
            f'<div class="stamp"><b>{source_name}</b>{art_str}</div>'
        )

    stamps_html = "".join(stamps_list)
    html_block = f"""
    <div class="stamp-container">
        <div class="stamp-label">Sources officielles citées :</div>
        <div class="stamp-row">{stamps_html}</div>
    </div>
    """
    st.markdown(html_block, unsafe_allow_html=True)

def ask_docmind(question: str, domain: Optional[str], level: Optional[str]) -> Dict[str, Any]:
    """Interroge le backend FastAPI de DocMind AI."""
    payload = {"query": question, "domain": domain, "level": level}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/query", 
            json=payload, 
            timeout=45
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Le serveur prend trop de temps à répondre. Réessayez votre question."}
    except requests.exceptions.ConnectionError:
        return {"error": "Impossible d'atteindre le serveur FastAPI. Vérifiez la connexion backend."}
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else "Inconnu"
        return {"error": f"Erreur serveur (Code HTTP {status}). Veuillez contacter l'administrateur."}
    except Exception as e:
        return {"error": f"Une erreur inattendue est survenue : {str(e)}"}

# ------------------------------------------------------------------ #
# Logique de Navigation & Affichage
# ------------------------------------------------------------------ #
def stream_text(text: str):
    """Simule un effet de machine à écrire pour la réponse."""
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

if not st.session_state.chat_active:
    # ------------------------------------------------------------------ #
    # Portail d'Accueil (Empty State façon AIVOKA)
    # ------------------------------------------------------------------ #
    st.markdown("<h2 style='text-align: center; color: var(--green-deep); margin-bottom: 0.5rem;'>Comment pouvons-nous vous aider ?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--ink-muted); margin-bottom: 3rem;'>Choisissez l'assistant adapté à votre besoin</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("<div style='height: 3px; background: #ECA400; margin: -1rem -1rem 1rem -1rem; border-radius: 8px 8px 0 0;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; font-size:3.5rem; margin-bottom: 0.5rem;'>⚖️</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; margin: 0; color: #1E3A8A;'>Assistant Douanier</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; font-size:0.9rem; color: gray; height: 3.5rem;'>Questions sur la réglementation, les procédures douanières et le Tarif Extérieur Commun, les lois et codes qui régit la douane au Bénin</p>", unsafe_allow_html=True)
            
            st.markdown("<div style='text-align:center; font-size:0.75rem; font-weight:bold; color: gray; letter-spacing: 1px; margin-top: 1rem; margin-bottom: 0.5rem;'>EXEMPLES DE QUESTIONS</div>", unsafe_allow_html=True)
            
            selected_q = st.pills(
                "Exemples IA",
                ["Régimes suspensifs", "Dédouanement d'un véhicule", "Qualification des marchandises", "Prélèvement Communautaire de Solidarité(PCS)"],
                label_visibility="collapsed",
                key="pills_ia"
            )
            
            if st.button("Ouvrir l'Assistant IA →", type="primary", use_container_width=True):
                st.session_state.chat_active = True
                if selected_q:
                    st.session_state.user_prompt = selected_q
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("<div style='height: 3px; background: #2563EB; margin: -1rem -1rem 1rem -1rem; border-radius: 8px 8px 0 0;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center; font-size:3.5rem; margin-bottom: 0.5rem;'>📋</div>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; margin: 0; color: #1E3A8A;'>Audit & Controle</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; font-size:0.9rem; color: gray; height: 3.5rem;'>Analysez intelligemment les incohérences dans vos déclarations et verification de la conformité des déclarations.</p>", unsafe_allow_html=True)
            
            st.markdown("<div style='text-align:center; font-size:0.75rem; font-weight:bold; color: gray; letter-spacing: 1px; margin-top: 1rem; margin-bottom: 0.5rem;'>FONCTIONNALITÉS</div>", unsafe_allow_html=True)
            
            st.pills(
                "Exemples Audit",
                ["Détection d'anomalies", "Vérification de valeur", "Identifier les incohérences dans les déclarations", "Pré-Audit & Controle"],
                label_visibility="collapsed",
                disabled=True,
                key="pills_audit"
            )
            
            st.button("Bientôt disponible", disabled=True, use_container_width=True)

else:
    # ------------------------------------------------------------------ #
    # Fil de Discussion (Mode Chat)
    # ------------------------------------------------------------------ #
    
    # Bouton retour si on veut quitter le chat
    if st.button("← Retour à l'accueil", key="btn_back_home"):
        st.session_state.chat_active = False
        st.rerun()
        
    st.space("small")

    # Récupération de l'input (chat_input classique ou pré-rempli depuis l'accueil)
    prompt = st.chat_input("Posez votre question réglementaire...")
    if "user_prompt" in st.session_state:
        prompt = st.session_state.user_prompt
        del st.session_state.user_prompt

    # Helper pour personnaliser les avatars
    def get_avatar(role: str) -> str:
        return ":material/person:" if role == "user" else ":material/policy:"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=get_avatar(msg["role"])):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                render_sources(msg["sources"])

    # Zone de Saisie et Traitement
    if prompt:
        # Enregistrement du message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=get_avatar("user")):
            st.markdown(prompt)

        # Réponse de l'assistant
        with st.chat_message("assistant", avatar=get_avatar("assistant")):
            with st.status("Analyse du Code des Douanes...", expanded=True) as status:
                st.write("Recherche des articles pertinents...")
                res = ask_docmind(prompt, domain_filter, level_filter)
                
                if "error" in res:
                    status.update(label="Erreur lors de l'analyse", state="error", expanded=False)
                    answer = f":material/warning: **Erreur** : {res['error']}"
                    sources = []
                    st.markdown(answer)
                else:
                    status.update(label="Analyse terminée", state="complete", expanded=False)
                    answer = res.get("answer", "Aucune réponse trouvée dans les documents.")
                    sources = res.get("sources", [])
                    
                    # Effet machine à écrire pour la fluidité
                    st.write_stream(stream_text(answer))
                    
                    if sources:
                        render_sources(sources)

        # Sauvegarde dans la session
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer, 
            "sources": sources
        })