import base64
import io
import os
import time
import urllib.parse
from PIL import Image
from pydantic import BaseModel, Field
import requests
import streamlit as st

# Safe import for dotenv: works both locally and on Streamlit Cloud
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from google import genai

# 1. Page Configuration
st.set_page_config(
    page_title="Tavern Forge | Sylvan Compendium",
    page_icon="🌿",
    layout="wide",
)


# 2. Sylvan Forest Canopy & Parchment Manuscript Theme
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


bg_encoded = get_base64_image("forest_bg.png")
parchment_encoded = get_base64_image("parchment.png")

if bg_encoded:
    bg_image_css = f'url("data:image/png;base64,{bg_encoded}")'
else:
    bg_image_css = 'url("https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=2000&q=80")'

if parchment_encoded:
    card_bg_css = f'url("data:image/png;base64,{parchment_encoded}") no-repeat center center'
else:
    card_bg_css = 'radial-gradient(ellipse at center, #f5ebd0 0%, #decb9f 70%, #c4ab7c 100%)'

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&display=swap');

    /* Forest Background across all view containers */
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: linear-gradient(rgba(10, 25, 16, 0.55), rgba(4, 14, 8, 0.85)),
                    {bg_image_css} no-repeat center center fixed !important;
        background-size: cover !important;
        color: #f2f7ec !important;
        font-family: 'Cormorant Garamond', serif !important;
    }}

    header[data-testid="stHeader"], [data-testid="stToolbar"], .main {{
        background: transparent !important;
    }}

    /* Global Headings */
    h1, h2, h3, h4, h5 {{
        font-family: 'Cinzel', serif !important;
        color: #f7e2a9 !important;
        letter-spacing: 0.05em;
        text-shadow: 0 2px 14px rgba(0, 0, 0, 0.9), 0 0 10px rgba(110, 168, 120, 0.4);
    }}
    
    p, span, label, div {{
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.15rem;
    }}

    /* Sidebar: Frosted Forest Leather & Moss */
    section[data-testid="stSidebar"] {{
        background: rgba(14, 24, 16, 0.78) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1.5px solid rgba(223, 194, 130, 0.25) !important;
    }}
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h5 {{
        color: #f7e2a9 !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.05em;
    }}
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {{
        color: #dbead4 !important;
        font-size: 1.05rem !important;
        font-style: italic !important;
        opacity: 0.95 !important;
    }}
    section[data-testid="stSidebar"] label p {{
        color: #f7e2a9 !important;
        font-family: 'Cinzel', serif !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.03em;
    }}

    /* Sidebar Runic Preset Buttons */
    section[data-testid="stSidebar"] button[kind="secondary"] {{
        background: rgba(28, 20, 14, 0.65) !important;
        border: 1px solid rgba(212, 178, 111, 0.4) !important;
        border-radius: 12px !important;
        color: #f3ecd8 !important;
        font-family: 'Cinzel', serif !important;
        font-size: 0.95rem !important;
        padding: 8px 10px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        transition: all 0.25s ease !important;
    }}
    section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
        background: rgba(55, 36, 20, 0.85) !important;
        border-color: #f7e2a9 !important;
        color: #ffffff !important;
        transform: translateY(-1px) !important;
    }}

    /* Text Area */
    section[data-testid="stSidebar"] textarea {{
        background: rgba(8, 18, 12, 0.85) !important;
        border: 1.5px solid rgba(212, 178, 111, 0.45) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.2rem !important;
        padding: 12px 14px !important;
    }}
    section[data-testid="stSidebar"] textarea::placeholder {{
        color: #b0ccb3 !important;
        font-style: italic !important;
    }}

    /* Primary Awaken Button */
    button[kind="primary"] {{
        background: linear-gradient(180deg, #3d7d4e 0%, #1a4227 100%) !important;
        border: 1.5px solid #d4b26f !important;
        border-radius: 20px !important;
        color: #fff9e6 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        font-size: 1.0rem !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 12px 24px !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.7), inset 0 1px 2px rgba(255,255,255,0.2) !important;
        transition: all 0.3s ease;
    }}
    button[kind="primary"]:hover {{
        background: linear-gradient(180deg, #4d9962 0%, #225734 100%) !important;
        border-color: #f7e2a9 !important;
        box-shadow: 0 10px 24px rgba(0,0,0,0.8), 0 0 20px rgba(212, 178, 111, 0.4) !important;
        transform: translateY(-2px);
    }}

    /* Parchment Card Container */
    .parchment-card {{
        background: {card_bg_css} !important;
        background-size: cover !important;
        border: 2.5px solid rgba(85, 45, 18, 0.65) !important;
        border-radius: 20px !important;
        padding: 32px 36px !important;
        box-shadow: 0 22px 55px rgba(0, 0, 0, 0.85), inset 0 0 45px rgba(60, 30, 10, 0.28) !important;
        margin-bottom: 24px !important;
    }}

    /* Dark Typography Sitting on Parchment */
    .parchment-card h1, 
    .parchment-card h2, 
    .parchment-card h3 {{
        color: #2b1406 !important;
        text-shadow: none !important;
        font-family: 'Cinzel', serif !important;
    }}
    .parchment-card p, 
    .parchment-card span {{
        color: #351a08 !important;
        text-shadow: none !important;
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.25rem !important;
        line-height: 1.6 !important;
    }}

    /* Stat Medallions (Engraved Wood / Leather on Parchment) */
    .stat-badge {{
        background: rgba(58, 30, 12, 0.12) !important;
        border: 1.5px solid rgba(94, 52, 23, 0.4) !important;
        border-radius: 14px !important;
        padding: 10px 4px !important;
        text-align: center !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1) !important;
    }}
    .stat-badge .label {{
        font-family: 'Cinzel', serif !important;
        font-size: 0.75rem !important;
        color: #5a3418 !important;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .stat-badge .mod {{
        font-family: 'Cinzel', serif !important;
        font-size: 1.85rem !important;
        font-weight: 700 !important;
        color: #241103 !important;
        margin: 1px 0;
    }}
    .stat-badge .score {{
        font-size: 0.9rem !important;
        color: #6a3e1e !important;
        font-weight: 600;
    }}

    /* Vital Badges */
    .vital-badge {{
        background: rgba(58, 30, 12, 0.15) !important;
        border: 1.5px solid rgba(94, 52, 23, 0.45) !important;
        border-radius: 12px !important;
        padding: 8px 4px !important;
        text-align: center !important;
    }}
    .vital-badge .title {{
        font-size: 0.72rem !important;
        color: #5a3418 !important;
        font-family: 'Cinzel', serif !important;
        letter-spacing: 0.06em;
    }}
    .vital-badge .val {{
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: #241103 !important;
        font-family: 'Cinzel', serif !important;
    }}

    /* Tab Headers */
    button[data-baseweb="tab"] p {{
        font-family: 'Cinzel', serif !important;
        font-size: 1.1rem !important;
        color: #3b1d09 !important;
    }}

    /* Portrait Frame */
    [data-testid="stImage"] img {{
        border: 2px solid rgba(85, 45, 18, 0.6) !important;
        border-radius: 16px !important;
        box-shadow: 0 10px 24px rgba(0,0,0,0.5) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Retrieve API Key
api_key = None
try:
    api_key = st.secrets.get("GEMINI_API_KEY")
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error(
        "🔑 GEMINI_API_KEY not found. Please add it to your .env file or"
        " Streamlit secrets."
    )
    st.stop()

# Initialize Gemini client
client = genai.Client(api_key=api_key)


# 4. Data Models
class AbilityScores(BaseModel):
    strength: int = Field(description="Score between 3 and 18")
    dexterity: int = Field(description="Score between 3 and 18")
    constitution: int = Field(description="Score between 3 and 18")
    intelligence: int = Field(description="Score between 3 and 18")
    wisdom: int = Field(description="Score between 3 and 18")
    charisma: int = Field(description="Score between 3 and 18")

    def get_mod(self, score: int) -> str:
        return f"{(score - 10) // 2:+d}"

    @property
    def str_mod(self) -> str:
        return self.get_mod(self.strength)

    @property
    def dex_mod(self) -> str:
        return self.get_mod(self.dexterity)

    @property
    def con_mod(self) -> str:
        return self.get_mod(self.constitution)

    @property
    def int_mod(self) -> str:
        return self.get_mod(self.intelligence)

    @property
    def wis_mod(self) -> str:
        return self.get_mod(self.wisdom)

    @property
    def cha_mod(self) -> str:
        return self.get_mod(self.charisma)


class DndCharacter(BaseModel):
    name: str = Field(description="Full character name")
    title: str = Field(
        description="An evocative title or epithet, e.g. 'The Silent Whisper'"
    )
    race: str = Field(description="D&D race")
    character_class: str = Field(description="D&D class")
    level: int = Field(default=1)
    stats: AbilityScores
    armor_class: int = Field(
        description="Sensible Level 1 AC based on class and dexterity"
    )
    max_hp: int = Field(
        description="Sensible Level 1 Max HP based on hit die and constitution"
    )
    equipment: list[str] = Field(
        description="List of starting equipment and signature items"
    )
    secret_or_flaw: str = Field(
        description="A memorable character flaw, quirk, or dangerous secret"
    )
    backstory_summary: str = Field(
        description="2-3 sentence atmospheric origin story"
    )
    visual_description: str = Field(
        description="Detailed physical portrait description for an artist"
    )


# 5. Sidebar
with st.sidebar:
    st.markdown("## ᛟ ANCIENT GROVE")
    st.caption("Structured 5e Character Engine")

    st.markdown("##### ᚱ RUNIC WHISPERS")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("ᛉ Spore Druid", use_container_width=True):
            st.session_state["prompt_input"] = (
                "A quiet firbolg circle of spores druid who cultivates rare"
                " glowing mushrooms in his moss-woven coat."
            )
        if st.button("ᚲ Rogue", use_container_width=True):
            st.session_state["prompt_input"] = (
                "An arcane trickster rogue obsessed with mechanical lockpicks"
                " and winding puzzle boxes."
            )
    with col_b:
        if st.button("ᛏ Paladin", use_container_width=True):
            st.session_state["prompt_input"] = (
                "An oath of vengeance paladin whose ancestral blade whispers"
                " warnings about the party's allies."
            )
        if st.button("ᚺ Sorcerer", use_container_width=True):
            st.session_state["prompt_input"] = (
                "A wild magic sorcerer tavern-cook whose spells accidentally"
                " trigger whenever dishes clatter."
            )

    current_prompt = st.session_state.get("prompt_input", "")

    user_concept = st.text_area(
        "Breathe life into your concept:",
        value=current_prompt,
        placeholder="e.g. A paranoid warlock with a penchant for butter who believes his patron lives in the churn.",
        height=120,
    )
    generate_btn = st.button(
        "ᛗ AWAKEN ADVENTURER", type="primary", use_container_width=True
    )

# 6. Generation Engine
if generate_btn:
    if not user_concept.strip():
        st.warning("Please breathe a concept into the grove first!")
    else:
        with st.status(
            "Conjuring adventurer from the weave...", expanded=True
        ) as status:
            st.write("🌿 Aligning celestial ability scores and destiny...")

            text_response = None
            models_to_try = ["gemini-3.8-flash", "gemini-3.1-pro-preview"]
            last_err = None

            for model_name in models_to_try:
                for attempt in range(2):
                    try:
                        text_response = client.models.generate_content(
                            model=model_name,
                            contents=(
                                "Create a rich, flavorful level 1 D&D character"
                                f" based on this prompt: {user_concept}"
                            ),
                            config={
                                "response_mime_type": "application/json",
                                "response_schema": DndCharacter,
                            },
                        )
                        if text_response and text_response.text:
                            break
                    except Exception as e:
                        last_err = e
                        time.sleep(1.5)
                if text_response and text_response.text:
                    break

            if not text_response or not text_response.text:
                st.error(
                    "ᛈ The Oracle was momentarily unreachable. Please try"
                    f" awakening your adventurer once more. ({last_err})"
                )
                st.stop()

            char: DndCharacter = text_response.parsed
            st.session_state["current_char"] = char

            st.write("🎨 Painting soul portrait...")
            raw_prompt = (
                f"fantasy D&D portrait of {char.name}, {char.race}"
                f" {char.character_class}, {char.visual_description}, highly"
                " detailed digital oil painting, dark fantasy, sylvan forest"
            )
            encoded_prompt = urllib.parse.quote(raw_prompt)
            image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&nologo=true&seed=42"

            try:
                img_res = requests.get(image_url, timeout=30)
                if img_res.status_code == 200:
                    st.session_state["current_image"] = Image.open(
                        io.BytesIO(img_res.content)
                    )
                else:
                    st.session_state["current_image"] = None
            except Exception:
                st.session_state["current_image"] = None

            status.update(
                label="The adventurer steps into the clearing!",
                state="complete",
                expanded=False,
            )

# 7. Main Dossier Layout
if "current_char" in st.session_state:
    char: DndCharacter = st.session_state["current_char"]

    # The Manuscript Scroll Container
    st.markdown(
        f"""
        <div class="parchment-card" style="padding: 24px 30px; margin-bottom: 20px;">
            <div style="border-bottom: 1.5px solid rgba(94, 52, 23, 0.3); padding-bottom: 14px; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 2.4rem; letter-spacing: 0.04em;">{char.name}</h1>
                <p style="margin: 4px 0 0 0; color: #573318; font-size: 1.3rem; font-style: italic; font-weight: 600;">
                    "{char.title}" &nbsp;•&nbsp; Level {char.level} {char.race} {char.character_class}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2-Column Split: Portrait & Vitals (Left) | Stats & Lore (Right)
    col_left, col_right = st.columns([4, 6], gap="large")

    with col_left:
        if st.session_state.get("current_image"):
            st.image(st.session_state["current_image"], use_container_width=True)
        else:
            st.info("Portrait shrouded in forest mist.")

        st.markdown(
            "<div style='height: 12px;'></div>", unsafe_allow_html=True
        )
        v1, v2, v3, v4 = st.columns(4)
        with v1:
            st.markdown(
                "<div class='vital-badge'><div class='title'>ARMOR</div><div"
                f" class='val'>{char.armor_class}</div></div>",
                unsafe_allow_html=True,
            )
        with v2:
            st.markdown(
                "<div class='vital-badge'><div class='title'>MAX HP</div><div"
                f" class='val' style='color:#8b1e1e;'>{char.max_hp}</div></div>",
                unsafe_allow_html=True,
            )
        with v3:
            st.markdown(
                "<div class='vital-badge'><div"
                " class='title'>INITIATIVE</div><div"
                f" class='val'>{char.stats.dex_mod}</div></div>",
                unsafe_allow_html=True,
            )
        with v4:
            st.markdown(
                "<div class='vital-badge'><div class='title'>SPEED</div><div"
                " class='val'>30ft</div></div>",
                unsafe_allow_html=True,
            )

    with col_right:
        st.markdown(
            "<h3 style='margin-top:0; font-size: 1.4rem;'>Ability"
            " Attributes</h3>",
            unsafe_allow_html=True,
        )

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(
                "<div class='stat-badge'><div"
                " class='label'>Strength</div><div"
                f" class='mod'>{char.stats.str_mod}</div><div"
                f" class='score'>Score: {char.stats.strength}</div></div>",
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                "<div class='stat-badge'><div"
                " class='label'>Dexterity</div><div"
                f" class='mod'>{char.stats.dex_mod}</div><div"
                f" class='score'>Score: {char.stats.dexterity}</div></div>",
                unsafe_allow_html=True,
            )
        with s3:
            st.markdown(
                "<div class='stat-badge'><div"
                " class='label'>Constitution</div><div"
                f" class='mod'>{char.stats.con_mod}</div><div"
                f" class='score'>Score: {char.stats.constitution}</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        s4, s5, s6 = st.columns(3)
        with s4:
            st.markdown(
                "<div class='stat-badge'><div"
                " class='label'>Intelligence</div><div"
                f" class='mod'>{char.stats.int_mod}</div><div"
                f" class='score'>Score: {char.stats.intelligence}</div></div>",
                unsafe_allow_html=True,
            )
        with s5:
            st.markdown(
                "<div class='stat-badge'><div class='label'>Wisdom</div><div"
                f" class='mod'>{char.stats.wis_mod}</div><div"
                f" class='score'>Score: {char.stats.wisdom}</div></div>",
                unsafe_allow_html=True,
            )
        with s6:
            st.markdown(
                "<div class='stat-badge'><div"
                " class='label'>Charisma</div><div"
                f" class='mod'>{char.stats.cha_mod}</div><div"
                f" class='score'>Score: {char.stats.charisma}</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='height: 16px;'></div>", unsafe_allow_html=True
        )
        tab_lore, tab_flaw, tab_gear = st.tabs([
            "ᚨ Chronicled Lore",
            "ᛈ Secret & Flaw",
            "ᚠ Traveling Gear",
        ])

        with tab_lore:
            st.markdown(
                "<div style='background: rgba(60, 32, 14, 0.08); border: 1px"
                " solid rgba(94, 52, 23, 0.25); border-radius: 12px; padding:"
                " 16px 20px; color: #2e1708; font-size: 1.25rem; line-height:"
                f" 1.6;'>{char.backstory_summary}</div>",
                unsafe_allow_html=True,
            )

        with tab_flaw:
            st.markdown(
                "<div style='background: rgba(140, 28, 28, 0.12); border: 1px"
                " solid rgba(160, 40, 40, 0.35); border-radius: 12px; padding:"
                " 16px 20px; color: #5a1414; font-size: 1.25rem; line-height:"
                f" 1.6;'>{char.secret_or_flaw}</div>",
                unsafe_allow_html=True,
            )

        with tab_gear:
            gear_html = "".join([
                f"<li style='margin-bottom: 6px;'><b>{item}</b></li>"
                for item in char.equipment
            ])
            st.markdown(
                "<div style='background: rgba(60, 32, 14, 0.08); border: 1px"
                " solid rgba(94, 52, 23, 0.25); border-radius: 12px; padding:"
                " 16px 20px; color: #2e1708; font-size: 1.2rem;'><ul"
                f" style='margin: 0; padding-left: 20px;'>{gear_html}</ul></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='height: 14px;'></div>", unsafe_allow_html=True
        )
        st.download_button(
            label="📥 Export Dossier (.json)",
            data=char.model_dump_json(indent=2),
            file_name=f"{char.name.lower().replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )

else:
    # Empty State: The Unwritten Manuscript
    st.markdown(
        """
        <div class="parchment-card" style="text-align: center; max-width: 680px; margin: 40px auto; padding: 42px 32px;">
            <div style="font-size: 1.8rem; color: #5a3418; margin-bottom: 8px; letter-spacing: 0.35em;">ᛟ ᛉ ᛏ ᛈ ᚠ</div>
            <h2 style="font-size: 2.2rem; margin-bottom: 12px; font-weight: 700; color: #2b1406;">The Grove Awaits</h2>
            <p style="font-size: 1.3rem; max-width: 500px; margin: 0 auto; line-height: 1.6; font-style: italic; color: #573318;">
                No hero or scoundrel has answered the call yet. Breathe a concept into the ancient archives on the left to forge your adventurer.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
