import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import base64
import math
from io import BytesIO
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="FITNESSFLIX ELITE",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Inject CSS Stylesheet
try:
    with open("style.css", "r", encoding="utf-8") as f:
        css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
except Exception as e:
    st.sidebar.error(f"Could not load style.css: {e}")

# 3. Canvas Confetti Component Helper
def trigger_confetti():
    import streamlit.components.v1 as components
    components.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            // Fire multiple bursts of confetti!
            var duration = 3 * 1000;
            var end = Date.now() + duration;

            (function frame() {
                confetti({
                    particleCount: 5,
                    angle: 60,
                    spread: 55,
                    origin: { x: 0 }
                });
                confetti({
                    particleCount: 5,
                    angle: 120,
                    spread: 55,
                    origin: { x: 1 }
                });

                if (Date.now() < end) {
                    requestAnimationFrame(frame);
                }
            }());
        </script>
        """,
        height=0,
        width=0,
    )

# --- SVG Custom Charts (Zero-Dependency Charting) ---
def draw_svg_gauge(score, color_hex):
    pct = score / 100.0
    offset = 502.6 * (1.0 - pct)
    svg = f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
    <svg width="220" height="220" viewBox="0 0 200 200" style="background:transparent;">
        <!-- Background track -->
        <circle cx="100" cy="100" r="80" stroke="rgba(255, 255, 255, 0.05)" stroke-width="14" fill="none"/>
        
        <!-- Active track -->
        <circle cx="100" cy="100" r="80" stroke="{color_hex}" stroke-width="14" 
                stroke-dasharray="502.6" stroke-dashoffset="{offset}" stroke-linecap="round" fill="none" 
                transform="rotate(-90 100 100)" style="filter: drop-shadow(0 0 8px {color_hex}); transition: stroke-dashoffset 0.5s ease;"/>
                
        <!-- Inner Details -->
        <text x="100" y="85" fill="#A1A1AA" font-size="10" font-family="'Poppins', sans-serif" font-weight="600" text-anchor="middle" letter-spacing="1">FITNESS SCORE</text>
        <text x="100" y="130" fill="#FFFFFF" font-size="42" font-family="'Poppins', sans-serif" font-weight="800" text-anchor="middle">{score}</text>
        <text x="100" y="150" fill="{color_hex}" font-size="11" font-family="'Poppins', sans-serif" font-weight="700" text-anchor="middle" letter-spacing="0.5">/ 100 PTS</text>
    </svg>
    </div>
    """
    return svg

def draw_activity_rings(mission):
    workout_pct = 1.0 if mission["workout"] else 0.1
    water_pct = min(1.0, mission["water"] / 3.0)
    sleep_pct = min(1.0, mission["sleep"] / 8.0)
    steps_pct = min(1.0, mission["steps"] / 10000)
    
    steps_offset = 502.6 * (1.0 - steps_pct)
    workout_offset = 408.4 * (1.0 - workout_pct)
    water_offset = 314.2 * (1.0 - water_pct)
    sleep_offset = 219.9 * (1.0 - sleep_pct)
    
    html = f"""
    <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; padding: 20px;">
        <svg width="220" height="220" viewBox="0 0 200 200" style="background:transparent;">
            <!-- Steps Ring (Green) -->
            <circle cx="100" cy="100" r="80" stroke="rgba(34, 197, 94, 0.08)" stroke-width="12" fill="none"/>
            <circle cx="100" cy="100" r="80" stroke="#22C55E" stroke-width="12" stroke-dasharray="502.6" stroke-dashoffset="{steps_offset}" stroke-linecap="round" fill="none" transform="rotate(-90 100 100)" style="filter: drop-shadow(0 0 4px #22C55E);"/>
            
            <!-- Workout Ring (Purple) -->
            <circle cx="100" cy="100" r="65" stroke="rgba(124, 58, 237, 0.08)" stroke-width="12" fill="none"/>
            <circle cx="100" cy="100" r="65" stroke="#7C3AED" stroke-width="12" stroke-dasharray="408.4" stroke-dashoffset="{workout_offset}" stroke-linecap="round" fill="none" transform="rotate(-90 100 100)" style="filter: drop-shadow(0 0 4px #7C3AED);"/>
            
            <!-- Hydration Ring (Cyan) -->
            <circle cx="100" cy="100" r="50" stroke="rgba(0, 212, 255, 0.08)" stroke-width="12" fill="none"/>
            <circle cx="100" cy="100" r="50" stroke="#00D4FF" stroke-width="12" stroke-dasharray="314.2" stroke-dashoffset="{water_offset}" stroke-linecap="round" fill="none" transform="rotate(-90 100 100)" style="filter: drop-shadow(0 0 4px #00D4FF);"/>
            
            <!-- Sleep Ring (Yellow) -->
            <circle cx="100" cy="100" r="35" stroke="rgba(234, 179, 8, 0.08)" stroke-width="12" fill="none"/>
            <circle cx="100" cy="100" r="35" stroke="#EAB308" stroke-width="12" stroke-dasharray="219.9" stroke-dashoffset="{sleep_offset}" stroke-linecap="round" fill="none" transform="rotate(-90 100 100)" style="filter: drop-shadow(0 0 4px #EAB308);"/>
        </svg>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px; justify-content: center; font-size: 11px;">
            <span style="color:#22C55E;">● Steps ({int(steps_pct*100)}%)</span>
            <span style="color:#7C3AED;">● Workout ({int(workout_pct*100)}%)</span>
            <span style="color:#00D4FF;">● Water ({int(water_pct*100)}%)</span>
            <span style="color:#EAB308;">● Sleep ({int(sleep_pct*100)}%)</span>
        </div>
    </div>
    """
    return html

def draw_svg_radar(values):
    labels = ["Workouts", "Hydration", "Calories", "Sleep", "Steps", "Consistency"]
    cx, cy = 100, 100
    r_max = 70
    
    grid_polygons = []
    for pct in [0.25, 0.50, 0.75, 1.0]:
        rg = r_max * pct
        g_pts = []
        for i in range(6):
            angle = i * (math.pi / 3) - (math.pi / 2)
            gx = cx + rg * math.cos(angle)
            gy = cy + rg * math.sin(angle)
            g_pts.append(f"{gx:.1f},{gy:.1f}")
        grid_polygons.append(f'<polygon points="{" ".join(g_pts)}" stroke="rgba(255,255,255,0.08)" fill="none" stroke-width="1"/>')
        
    active_pts = []
    label_elements = []
    for i in range(6):
        angle = i * (math.pi / 3) - (math.pi / 2)
        val = values[i]
        px = cx + (r_max * (val / 100.0)) * math.cos(angle)
        py = cy + (r_max * (val / 100.0)) * math.sin(angle)
        active_pts.append(f"{px:.1f},{py:.1f}")
        
        ax_end_x = cx + r_max * math.cos(angle)
        ax_end_y = cy + r_max * math.sin(angle)
        grid_polygons.append(f'<line x1="{cx}" y1="{cy}" x2="{ax_end_x:.1f}" y2="{ax_end_y:.1f}" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>')
        
        lbl_x = cx + (r_max + 18) * math.cos(angle)
        lbl_y = cy + (r_max + 10) * math.sin(angle)
        if abs(math.cos(angle)) < 0.1:
            anchor = "middle"
        elif math.cos(angle) > 0:
            anchor = "start"
        else:
            anchor = "end"
            
        label_elements.append(f'<text x="{lbl_x:.1f}" y="{lbl_y+4:.1f}" fill="#A1A1AA" font-size="9" font-family="Inter" font-weight="600" text-anchor="{anchor}">{labels[i]}</text>')
        
    active_poly = f'<polygon points="{" ".join(active_pts)}" fill="rgba(0, 212, 255, 0.15)" stroke="#00D4FF" stroke-width="2" style="filter: drop-shadow(0 0 3px rgba(0, 212, 255, 0.4));"/>'
    
    svg = f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
    <svg width="240" height="240" viewBox="0 0 200 200" style="background:transparent;">
        {"".join(grid_polygons)}
        {active_poly}
        {"".join(label_elements)}
    </svg>
    </div>
    """
    return svg

def draw_svg_heatmap(grid_values):
    colors = ["#3F3F46", "#7C3AED", "#00D4FF", "#22C55E"]
    labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    rects = []
    box_w = 20
    box_h = 20
    gap = 4
    
    headers = []
    for idx, day in enumerate(labels):
        x = idx * (box_w + gap) + 30
        headers.append(f'<text x="{x + box_w/2}" y="15" fill="#A1A1AA" font-size="8" font-family="Inter" text-anchor="middle" font-weight="600">{day}</text>')
        
    for r_idx in range(4):
        y = r_idx * (box_h + gap) + 25
        rects.append(f'<text x="5" y="{y + box_h/2 + 3}" fill="#A1A1AA" font-size="8" font-family="Inter" font-weight="600">W-{3-r_idx}</text>')
        for c_idx in range(7):
            val = grid_values[r_idx][c_idx]
            color = colors[val]
            x = c_idx * (box_w + gap) + 30
            rects.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="3" fill="{color}"><title>Status: {val}</title></rect>')
            
    svg = f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 20px;">
    <svg width="220" height="130" viewBox="0 0 200 130" style="background:transparent;">
        {"".join(headers)}
        {"".join(rects)}
    </svg>
    </div>
    """
    return svg

# 4. Initialize Session State
def init_state():
    if "initialized" not in st.session_state:
        # User profile state
        st.session_state.user_profile = {
            "name": "Alex Mercer",
            "level": 14,
            "xp": 8400,
            "next_level_xp": 10000,
            "streak": 42,
            "longest_streak": 42,
            "fitness_score": 87,
            "global_rank": 1420,
            "country_rank": 312,
            "friend_rank": 1,
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200",
            "today_mission": {
                "workout": False,
                "water": 1.8,  # Liters (Target 3.0)
                "nutrition": 1800,  # kcal (Target 2200)
                "sleep": 7.5,  # Hours (Target 8.0)
                "steps": 8420  # Steps (Target 10000)
            }
        }
        
        # Elite Membership status
        st.session_state.elite_unlocked = False
        st.session_state.current_page = "Home"
        st.session_state.active_coach = "Nova"
        st.session_state.wrapped_slide = 0

        # Generate 30 days of historical data for analytics
        np.random.seed(42)
        dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(29, -1, -1)]
        
        # Create a plausible training history dataset
        scores = []
        base_score = 45
        for i in range(30):
            # General improvement over time with variance
            base_score += np.random.uniform(-3, 6)
            base_score = max(30, min(95, base_score))
            scores.append(round(base_score))
            
        steps = np.random.randint(6000, 13000, size=30)
        water = np.random.uniform(1.5, 3.5, size=30)
        sleep = np.random.uniform(5.5, 8.5, size=30)
        calories = np.random.randint(1600, 2600, size=30)
        active_mins = np.random.randint(20, 80, size=30)
        weight = [85.0 - (i * 0.13) + np.random.uniform(-0.3, 0.3) for i in range(30)]
        muscle_mass = [32.0 + (i * 0.07) + np.random.uniform(-0.15, 0.15) for i in range(30)]
        
        st.session_state.history_df = pd.DataFrame({
            "Date": dates,
            "Fitness Score": scores,
            "Steps": steps,
            "Water": np.round(water, 1),
            "Sleep": np.round(sleep, 1),
            "Calories": calories,
            "Active Mins": active_mins,
            "Weight": np.round(weight, 1),
            "Muscle Mass": np.round(muscle_mass, 1)
        })

        # Community Posts
        st.session_state.posts = [
            {
                "id": 1,
                "author": "Sophia Chen",
                "avatar": "https://images.unsplash.com/photo-1548690312-e3b507d8c110?auto=format&fit=crop&q=80&w=150",
                "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=600",
                "caption": "Before and After: Day 1 vs Day 100 of FitnessFlix! Down 8kg of fat, gained pure muscle and explosive energy. Trust the process and log your daily missions! 👑💪",
                "stats": "🏃‍♀️ 100-Day Legend | Streak: 100 Days | Level 24",
                "likes": 142,
                "flames": 98,
                "respect": 120,
                "cheers": ["Inspirational progress!", "You are a beast, Sophia!", "Absolute legend 👑"],
                "elite_votes": 12
            },
            {
                "id": 2,
                "author": "Marcus Aurelius",
                "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150",
                "image": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&q=80&w=600",
                "caption": "Sunday morning 15K run. Heavy fog, cold wind, zero excuses. The arena waits for no one. Active minutes: 78 min, avg heart rate: 152 bpm. Let's conquer the week! 🐺🏃‍♂️",
                "stats": "⚡ Elite Performer | Streak: 72 Days | Level 19",
                "likes": 87,
                "flames": 114,
                "respect": 95,
                "cheers": ["Outstanding pace!", "Consistency pays off.", "Let's run together next week!"],
                "elite_votes": 8
            },
            {
                "id": 3,
                "author": "Emma Stone",
                "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150",
                "image": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?auto=format&fit=crop&q=80&w=600",
                "caption": "PR ALERT! Hit 100kg on my back squat today! 🏋️‍♀️ Coaching Nova helped me refine my bracing and sleep schedule to hit peak recovery. Highly recommend checking out the AI coach pro analytics!",
                "stats": "🏆 Consistency King | Streak: 38 Days | Level 16",
                "likes": 95,
                "flames": 82,
                "respect": 108,
                "cheers": ["Whoa, huge squat!", "Nova is the best coach.", "Form is impeccable"],
                "elite_votes": 5
            }
        ]

        # Joined Challenges
        st.session_state.joined_challenges = ["100-Day Elite Challenge"]
        
        # Available Challenges DB
        st.session_state.challenges_db = [
            {"id": "c1", "name": "100-Day Elite Challenge", "duration": "100 Days", "difficulty": "Elite", "xp": 5000, "meta": "Master your lifestyle", "image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=400"},
            {"id": "c2", "name": "Summer Shred 2026", "duration": "30 Days", "difficulty": "Hard", "xp": 2500, "meta": "Fat loss & core definition", "image": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&q=80&w=400"},
            {"id": "c3", "name": "Beast Mode Strength", "duration": "45 Days", "difficulty": "Extreme", "xp": 3500, "meta": "Heavy compound lifts focus", "image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&q=80&w=400"},
            {"id": "c4", "name": "10K Steps Daily", "duration": "7 Days", "difficulty": "Medium", "xp": 500, "meta": "Cardiovascular baseline", "image": "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&q=80&w=400"},
            {"id": "c5", "name": "Sleep Master", "duration": "14 Days", "difficulty": "Easy", "xp": 1000, "meta": "Deep sleep optimization", "image": "https://images.unsplash.com/photo-1511295742364-92767fa62d9f?auto=format&fit=crop&q=80&w=400"},
            {"id": "c6", "name": "Hydration Hero", "duration": "7 Days", "difficulty": "Easy", "xp": 500, "meta": "Optimal fluid replacement", "image": "https://images.unsplash.com/photo-1523362628745-0c100150b504?auto=format&fit=crop&q=80&w=400"}
        ]

        # Arena Private Rooms
        st.session_state.arena_rooms = [
            {
                "id": "r1",
                "name": "Office Steps War",
                "metric": "Steps",
                "duration": "7 Days",
                "leader": "Alex Mercer",
                "members": [
                    {"name": "Alex Mercer (You)", "score": 64820, "rank": 1},
                    {"name": "Sophia Chen", "score": 59200, "rank": 2},
                    {"name": "Marcus Aurelius", "score": 52100, "rank": 3},
                    {"name": "Emma Stone", "score": 48000, "rank": 4}
                ]
            },
            {
                "id": "r2",
                "name": "Weekend Burnout Club",
                "metric": "Active Mins",
                "duration": "30 Days",
                "leader": "Sophia Chen",
                "members": [
                    {"name": "Sophia Chen", "score": 420, "rank": 1},
                    {"name": "Marcus Aurelius", "score": 380, "rank": 2},
                    {"name": "Alex Mercer (You)", "score": 350, "rank": 3}
                ]
            }
        ]

        # AI Coach Conversation Records
        st.session_state.coach_messages = {
            "Nova": [
                {"role": "coach", "content": "Hello Alex. I am Nova, your analytical performance advisor. I evaluate your sleep cycles, caloric ratios, and muscle load data to provide clinical feedback. How can I optimize your metrics today?"}
            ],
            "Atlas": [
                {"role": "coach", "content": "Hey Alex! Atlas here. No matter what happened yesterday, today is a fresh opportunity to move, grow, and feel amazing. Tell me, how are you feeling mentally and physically today?"}
            ],
            "Titan": [
                {"role": "coach", "content": "SOLDIER! I don't care if it's cold, raining, or if you're tired. Success belongs to those who show up. Have you completed your mission yet? Speak up!"}
            ],
            "Apex": [
                {"role": "coach", "content": "Welcome Mercer. I focus on athletic mastery, endurance efficiency, and high-performance recovery. What structural goal or pacing strategy are we analyzing today?"}
            ]
        }
        
        # User Custom Success Stories list
        st.session_state.user_stories = []

        st.session_state.initialized = True

init_state()

# 5. Dynamic Calculations: Live Fitness Score
def calculate_fitness_score():
    mission = st.session_state.user_profile["today_mission"]
    
    # Workout: 30 pts
    workout_pts = 30 if mission["workout"] else 0
    
    # Water: max 20 pts (target 3.0L)
    water_pts = min(20.0, (mission["water"] / 3.0) * 20.0)
    
    # Nutrition: max 15 pts (close to 2200 kcal)
    diff_pct = abs(mission["nutrition"] - 2200) / 2200
    nutrition_pts = max(0.0, 15.0 - (diff_pct * 15.0))
    
    # Sleep: max 15 pts (target 8.0 hrs)
    sleep_pts = min(15.0, (mission["sleep"] / 8.0) * 15.0)
    
    # Steps: max 20 pts (target 10000 steps)
    steps_pts = min(20.0, (mission["steps"] / 10000.0) * 20.0)
    
    total = round(workout_pts + water_pts + nutrition_pts + sleep_pts + steps_pts)
    
    # Save to user profile
    st.session_state.user_profile["fitness_score"] = total
    return total

current_score = calculate_fitness_score()

# 6. Global Top Navigation Header (Netflix Look)
def render_nav_bar():
    # Render layout using custom div inside markdown
    st.markdown(
        """
        <div class="netflix-navbar">
            <a href="#" class="netflix-logo">FITNESSFLIX ELITE</a>
            <div style="color: #A1A1AA; font-size: 13px; font-weight: 600;">
                🎬 NETFLIX OF FITNESS • 👑 STATUS: <span class="elite-glowing-text">ELITE UNLOCKED</span>
            </div>
        </div>
        """ if st.session_state.elite_unlocked else 
        """
        <div class="netflix-navbar">
            <a href="#" class="netflix-logo">FITNESSFLIX ELITE</a>
            <div style="color: #A1A1AA; font-size: 13px; font-weight: 600;">
                🎬 NETFLIX OF FITNESS • 🔓 STATUS: STANDARD VISITOR
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # We use Streamlit columns to render interactive buttons acting as tabs, matching our styled class overrides
    cols = st.columns(11)
    pages = [
        ("Home", "🏠 Home"),
        ("My Journey", "🏃 My Journey"),
        ("Challenges", "⚔️ Challenges"),
        ("Arena", "🏟️ Arena"),
        ("Community", "👥 Community"),
        ("Leaderboard", "🏆 Leaderboard"),
        ("AI Coach", "🤖 AI Coach"),
        ("Profile", "👤 Profile"),
        ("Elite Badge", "👑 Elite Badge"),
        ("Wrapped", "🎁 Wrapped"),
        ("Settings", "⚙️ Settings")
    ]
    
    for idx, (page_key, page_label) in enumerate(pages):
        with cols[idx]:
            is_active = (st.session_state.current_page == page_key)
            # Apply active class wrapper if selected
            if is_active:
                st.markdown('<div class="nav-active-btn">', unsafe_allow_html=True)
            if st.button(page_label, key=f"nav_btn_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
            if is_active:
                st.markdown('</div>', unsafe_allow_html=True)

render_nav_bar()
st.markdown("---")

# 7. Helper to render Netflix Movie Posters
def render_poster_html(title, subtitle, meta, badge_text="", badge_type="purple", image_url=""):
    badge_class = "poster-badge"
    if badge_type == "orange":
        badge_class += " poster-badge-orange"
    elif badge_type == "cyan":
        badge_class += " poster-badge-cyan"
    elif badge_type == "gold":
        badge_class += " poster-badge-gold"
        
    badge_html = f'<div class="{badge_class}">{badge_text}</div>' if badge_text else ''
    
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=400"
        
    return f"""
    <div class="netflix-poster">
        {badge_html}
        <img src="{image_url}" class="poster-image" />
        <div class="poster-overlay">
            <div class="poster-title">{title}</div>
            <div class="poster-subtitle">{subtitle}</div>
            <div class="poster-meta">{meta}</div>
        </div>
    </div>
    """

# 8. SUB-PAGE 1: HOME (Netflix Homepage style)
def show_home():
    st.markdown('<div class="cinematic-title">NOW PLAYING</div>', unsafe_allow_html=True)
    
    # Continue Your Journey Row
    st.markdown('<div class="section-header">Continue Your Journey <span>→</span></div>', unsafe_allow_html=True)
    cols_journey = st.columns(5)
    
    journey_items = [
        ("Day 42 Mission", "Active", "🔥 87 Fitness Score", "TODAY", "cyan", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=400", "My Journey"),
        ("Upper Body HIIT", "Workout", "⏱️ 45 Mins • 500 XP", "ACTIVE", "purple", "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?auto=format&fit=crop&q=80&w=400", "My Journey"),
        ("Foam Rolling Plan", "Recovery", "⚡ Restore Muscle", "PLAN", "orange", "https://images.unsplash.com/photo-1607962837359-5e7e89f866ad?auto=format&fit=crop&q=80&w=400", "My Journey"),
        ("Weekly Sunday Review", "AI Coach", "📝 Outlines & Advice", "NEW", "gold", "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=400", "AI Coach"),
        ("Hydration Micro", "AI Challenge", "💧 Drink 3.5L today", "100 XP", "cyan", "https://images.unsplash.com/photo-1523362628745-0c100150b504?auto=format&fit=crop&q=80&w=400", "Challenges")
    ]
    
    for i, (title, subtitle, meta, badge, btype, img, target) in enumerate(journey_items):
        with cols_journey[i]:
            st.markdown(render_poster_html(title, subtitle, meta, badge, btype, img), unsafe_allow_html=True)
            if st.button(f"Play: {title.split()[0]}", key=f"home_play_j_{i}", use_container_width=True):
                st.session_state.current_page = target
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Trending Challenges Row
    st.markdown('<div class="section-header">Trending Fitness Challenges <span>→</span></div>', unsafe_allow_html=True)
    cols_challenges = st.columns(5)
    
    challenge_items = [
        ("Summer Shred 2026", "30 Days HIIT", "🏆 2500 XP", "POPULAR", "orange", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&q=80&w=400"),
        ("Beast Mode Strength", "45 Days lifting", "⚡ 3500 XP", "HARDCORE", "purple", "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&q=80&w=400"),
        ("10K Steps Daily", "7 Days Consistency", "🏃 500 XP", "ACTIVE", "cyan", "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&q=80&w=400"),
        ("Sleep Master Hygiene", "14 Days Rest", "😴 1000 XP", "WELLNESS", "cyan", "https://images.unsplash.com/photo-1511295742364-92767fa62d9f?auto=format&fit=crop&q=80&w=400"),
        ("Hydration Hero Elite", "7 Days Water", "💧 500 XP", "HYDRATE", "cyan", "https://images.unsplash.com/photo-1523362628745-0c100150b504?auto=format&fit=crop&q=80&w=400")
    ]
    
    for i, (title, subtitle, meta, badge, btype, img) in enumerate(challenge_items):
        with cols_challenges[i]:
            st.markdown(render_poster_html(title, subtitle, meta, badge, btype, img), unsafe_allow_html=True)
            if st.button("Details", key=f"home_play_c_{i}", use_container_width=True):
                st.session_state.current_page = "Challenges"
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
                
    # Top Athletes & Social Verification Row
    st.markdown('<div class="section-header">Top Athletes This Week <span>→</span></div>', unsafe_allow_html=True)
    cols_athletes = st.columns(5)
    
    athletes_items = [
        ("Sophia Chen", "Level 24 Athlete", "👑 12.4K XP this week", "RANK 1", "gold", "https://images.unsplash.com/photo-1548690312-e3b507d8c110?auto=format&fit=crop&q=80&w=400"),
        ("Marcus Aurelius", "Level 19 Coach", "🔥 10.8K XP this week", "RANK 2", "orange", "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=400"),
        ("Emma Stone", "Level 16 Weightlifter", "💪 9.9K XP this week", "RANK 3", "purple", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=400"),
        ("Alex Mercer", "Level 14 Athlete (You)", "⚡ 8.4K XP this week", "RANK 4", "cyan", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=400"),
        ("John Doe", "Level 12 Sprinter", "🏃 7.2K XP this week", "RANK 5", "cyan", "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?auto=format&fit=crop&q=80&w=400")
    ]
    
    for i, (title, subtitle, meta, badge, btype, img) in enumerate(athletes_items):
        with cols_athletes[i]:
            st.markdown(render_poster_html(title, subtitle, meta, badge, btype, img), unsafe_allow_html=True)
            if st.button("Inspect Profile", key=f"home_play_a_{i}", use_container_width=True):
                st.session_state.current_page = "Leaderboard" if title != "Alex Mercer" else "Profile"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Success Stories Row
    st.markdown('<div class="section-header">Member Success Stories <span>→</span></div>', unsafe_allow_html=True)
    cols_stories = st.columns(4)
    
    success_items = [
        ("Fat Loss Transformation", "Sophia Chen", "🔥 Down 12kg fat in 100 days", "TRANSFORMED", "gold", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&q=80&w=400"),
        ("Cardio Endurance Growth", "Marcus Aurelius", "🏃 Hit 15k runs effortlessly", "ENDURANCE", "orange", "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?auto=format&fit=crop&q=80&w=400"),
        ("Strength Building Wins", "Emma Stone", "🏋️ Squatted 100kg PR today", "STRENGTH", "purple", "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&q=80&w=400"),
        ("Consistency Habits Lock", "Alex Mercer (You)", "⚡ Met target goals for 42 days", "RECOVERY", "cyan", "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=400")
    ]
    
    for i, (title, subtitle, meta, badge, btype, img) in enumerate(success_items):
        with cols_stories[i]:
            st.markdown(render_poster_html(title, subtitle, meta, badge, btype, img), unsafe_allow_html=True)
            if st.button("Read Story", key=f"home_play_s_{i}", use_container_width=True):
                st.session_state.current_page = "Community"
                st.rerun()


# 9. SUB-PAGE 2: MY JOURNEY (Today's Mission & Fitness Score recalculations)
def show_my_journey():
    st.markdown('<div class="cinematic-title">TODAY\'S EPISODE</div>', unsafe_allow_html=True)
    
    p = st.session_state.user_profile
    mission = p["today_mission"]
    
    col1, col2 = st.columns([1, 1.1])
    
    with col1:
        # Glassmorphic display of status
        st.markdown(
            f"""
            <div class="glass-card">
                <h2 style="margin: 0; font-size: 2.2rem; color: #FFFFFF;">Day {p['streak']} <span style="color: #A1A1AA; font-size:1.1rem; font-weight:400;">of 100 Challenge</span></h2>
                <div style="display: flex; gap: 15px; margin: 15px 0;">
                    <div style="background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 16px; border-radius: 8px; text-align: center;">
                        <span style="color: #00D4FF; font-weight: 800; font-size: 1.1rem;">{p['streak']} Days</span><br>
                        <span style="font-size: 10px; color: #A1A1AA; text-transform: uppercase;">Current Streak</span>
                    </div>
                    <div style="background: rgba(124, 58, 237, 0.1); border: 1px solid rgba(124, 58, 237, 0.2); padding: 8px 16px; border-radius: 8px; text-align: center;">
                        <span style="color: #7C3AED; font-weight: 800; font-size: 1.1rem;">Level {p['level']}</span><br>
                        <span style="font-size: 10px; color: #A1A1AA; text-transform: uppercase;">XP: {p['xp']}/{p['next_level_xp']}</span>
                    </div>
                    <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.2); padding: 8px 16px; border-radius: 8px; text-align: center;">
                        <span style="color: #22C55E; font-weight: 800; font-size: 1.1rem;">Rank #{p['global_rank']}</span><br>
                        <span style="font-size: 10px; color: #A1A1AA; text-transform: uppercase;">Global Standing</span>
                    </div>
                </div>
                <div style="margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; color: #A1A1AA;">
                        <span>XP Progress</span>
                        <span>{int(p['xp']/p['next_level_xp']*100)}%</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.progress(p["xp"] / p["next_level_xp"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # TODAY'S MISSION FORM (Auto-saving inputs directly to session state)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3>🎯 Today's Mission</h3>", unsafe_allow_html=True)
        
        # 1. Workout Toggle
        workout_check = st.checkbox("💪 Upper Body Shred Completed (45 mins)", value=mission["workout"])
        if workout_check != mission["workout"]:
            mission["workout"] = workout_check
            if workout_check:
                p["xp"] += 300
                st.toast("Workout Logged! +300 XP 🔥")
                trigger_confetti()
            else:
                p["xp"] = max(0, p["xp"] - 300)
            st.rerun()
            
        # 2. Water Tracker
        st.markdown(f"**💧 Hydration Tracker**: {mission['water']:.1f} L / 3.0 L")
        w_cols = st.columns(2)
        with w_cols[0]:
            if st.button("➕ Add 0.5 Liters", key="add_water", use_container_width=True):
                mission["water"] = round(min(5.0, mission["water"] + 0.5), 1)
                p["xp"] += 50
                st.toast("Water tracked! +50 XP 💧")
                st.rerun()
        with w_cols[1]:
            if st.button("➖ Subtract 0.5 Liters", key="sub_water", use_container_width=True):
                mission["water"] = round(max(0.0, mission["water"] - 0.5), 1)
                st.rerun()
        st.progress(min(1.0, mission["water"] / 3.0))

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Nutrition (Calorie Slider)
        st.markdown("**🍎 Calories Consumed** (Target: 2200 kcal)")
        calories_input = st.slider("Energy Intake (kcal)", min_value=1000, max_value=4000, value=mission["nutrition"], step=50)
        if calories_input != mission["nutrition"]:
            mission["nutrition"] = calories_input
            st.rerun()

        # 4. Sleep (Slider)
        st.markdown("**😴 Sleep Logged** (Target: 8.0 hrs)")
        sleep_input = st.slider("Sleep Duration (Hours)", min_value=4.0, max_value=12.0, value=mission["sleep"], step=0.5)
        if sleep_input != mission["sleep"]:
            mission["sleep"] = sleep_input
            st.rerun()

        # 5. Steps (Number Input)
        st.markdown("**🏃 Daily Steps count** (Target: 10000 steps)")
        steps_input = st.number_input("Steps Tracked", min_value=0, max_value=50000, value=mission["steps"], step=500)
        if steps_input != mission["steps"]:
            mission["steps"] = steps_input
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        # Display the big Fitness Score metric (0-100 meter)
        f_score = st.session_state.user_profile["fitness_score"]
        
        # Color boundaries
        score_color = "#EF4444" # red
        if f_score >= 85:
            score_color = "#22C55E" # green
        elif f_score >= 65:
            score_color = "#00D4FF" # cyan
        elif f_score >= 50:
            score_color = "#EAB308" # yellow
            
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        # Draw a beautiful radial / gauge chart using SVG
        gauge_svg = draw_svg_gauge(f_score, score_color)
        st.markdown(gauge_svg, unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 10px;">
                <h4 style="margin: 0; color: {score_color}; font-size: 1.4rem;">{f_score}/100 • {'EXCELLENT' if f_score >= 85 else 'GOOD' if f_score >= 65 else 'ACCURATE' if f_score >= 50 else 'NEEDS FOCUS'}</h4>
                <p style="font-size: 12px; color: #A1A1AA; max-width: 450px; margin: 8px auto;">
                    This score is re-calculated in real time using your logged activities, steps volume, hydration ratios, sleep consistency, and target caloric deficits. Keep consistency above 85% to stay Elite.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Shortcut to Analytics
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("💡 <i>AI Suggestion: You're close to a Perfect Hydration Score. Adding 1.2L of water will raise your Fitness Score to 91!</i>", unsafe_allow_html=True)
        if st.button("📊 Open Advanced Analytics Dashboard", use_container_width=True):
            st.session_state.current_page = "Settings" # temporary jump or reroute
            st.session_state.current_page = "Profile" # Let's redirect to Settings for wrapped or similar
            # Wait, let's just make it jump directly to Analytics:
            st.session_state.current_page = "Settings" # Wait, the tab name is not in navigation, let's check:
            # The tabs are: Home, My Journey, Challenges, Arena, Community, Leaderboard, AI Coach, Profile, Elite Badge, Wrapped, Settings.
            # Ah, the user didn't ask for a separate tab for Analytics, but says "Create a dedicated analytics experience. Must include:..."
            # Wait, let's check: in the list of tabs, is there "Analytics"?
            # Let's check user navigation list: "Logo, FITNESSFLIX ELITE, Home, My Journey, Challenges, Arena, Community, Leaderboard, AI Coach, Profile, Elite Badge, Settings"
            # It has no separate "Analytics" tab, but it says "Create a dedicated analytics experience. Must include...".
            # Where should this go?
            # It could either be a sub-section inside "My Journey", or we can add it directly to "My Journey" (which is perfect, or we can make a dedicated tab/sub-section or add an "Analytics" tab!).
            # Adding it as a clean Sub-Tab inside "My Journey" (e.g. using st.tabs(["Daily Mission", "Advanced Analytics"])) is extremely professional and matches Apple Fitness/Strava layout perfectly!
            # Let's do exactly that. The user can switch between "Daily Mission" and "Advanced Analytics" tabs right inside "My Journey"!
            # That is an elegant design decision that maintains the top-level navigation requested exactly, while providing the dedicated analytics experience.
            # Let's implement that sub-tab router below!
            pass
        st.markdown("</div>", unsafe_allow_html=True)


# 10. ADVANCED ANALYTICS (Zero-Dependency Custom Native & SVG Dashboard)
def show_analytics():
    st.markdown('<div class="cinematic-title">ATHLETE ANALYTICS</div>', unsafe_allow_html=True)
    
    df = st.session_state.history_df
    chart_df = df.copy().set_index("Date")
    
    # Free users see the first 4 charts, remainder are hidden behind the Elite Lock
    anal_tab1, anal_tab2 = st.tabs(["📈 General Analytics", "🔒 Elite Pro Analytics"])
    
    with anal_tab1:
        st.markdown("### Base Performance Analysis")
        col_c1, col_c2 = st.columns(2)
        
        # Chart 1: Fitness Progress Trend (Line Chart)
        with col_c1:
            st.markdown("#### 1. Fitness Score Evolution")
            st.area_chart(chart_df["Fitness Score"])
            
        # Chart 2: Weekly Workout Bar Chart
        with col_c2:
            st.markdown("#### 2. Weekly Activity Minutes")
            weekly_df = df.tail(7).copy()
            weekly_df["Day"] = [d.strftime("%a") for d in weekly_df["Date"]]
            st.bar_chart(weekly_df.set_index("Day")[["Active Mins", "Calories"]])
            
        col_c3, col_c4 = st.columns(2)
        
        # Chart 3: Goal Completion Donut Chart (Apple Concentric Circles)
        with col_c3:
            st.markdown("#### 3. Today's Target Allocations")
            mission = st.session_state.user_profile["today_mission"]
            st.markdown(draw_activity_rings(mission), unsafe_allow_html=True)
            
        # Chart 4: Monthly Active Minutes Area Chart
        with col_c4:
            st.markdown("#### 4. Cumulative Active Minutes")
            df["Cumulative Active Mins"] = df["Active Mins"].cumsum()
            st.area_chart(df.copy().set_index("Date")["Cumulative Active Mins"])
            
    with anal_tab2:
        # Check Elite Access
        if not st.session_state.elite_unlocked:
            st.markdown(
                """
                <div class="glass-card elite-card" style="text-align: center; padding: 60px 40px; margin-top: 20px;">
                    <span style="font-size: 3.5rem;">👑</span>
                    <h2 class="elite-glowing-text" style="font-size:2rem; margin:15px 0;">PREMIUM ELITE ANALYTICS LOCKED</h2>
                    <p style="color: #A1A1AA; max-width: 650px; margin: 0 auto 25px auto; font-size:14px; line-height:1.6;">
                        Unlock the full Strava-inspired analytics dashboard including radar balance metrics, 
                        weight projections, consistency box plots, 28-day habit heatmaps, and streak score forecasting.
                    </p>
                    <div style="background: rgba(255,255,255,0.03); display:inline-block; padding: 12px 30px; border-radius: 8px; border: 1px solid rgba(255,215,0,0.2);">
                        <b>PRO TIP:</b> Go to the <b>Elite Badge</b> navigation page and enter coupon code <span style="color:#FFD700; font-family:monospace; font-size:16px; font-weight:800;">REFRESH2026</span> to unlock instantly!
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown("<h3 class='elite-glowing-text'>👑 ELITE ANALYTICS PANEL</h3>", unsafe_allow_html=True)
            col_e1, col_e2 = st.columns(2)
            
            # Chart 5: Radar Chart (Dimension Balance)
            with col_e1:
                st.markdown("#### 5. Radar Dimension Balance")
                recent = df.tail(7)
                radar_vals = [
                    90,  # Workouts
                    int(min(100, (recent["Water"].mean() / 3.0) * 100)),
                    int(min(100, (1.0 - abs(recent["Calories"].mean() - 2200)/2200)*100)),
                    int(min(100, (recent["Sleep"].mean() / 8.0) * 100)),
                    int(min(100, (recent["Steps"].mean() / 10000) * 100)),
                    87  # Consistency index
                ]
                st.markdown(draw_svg_radar(radar_vals), unsafe_allow_html=True)
                
            # Chart 6: Habit Heatmap
            with col_e2:
                st.markdown("#### 6. 28-Day Habit Heatmap")
                grid_vals = [
                    [3, 2, 3, 0, 1, 2, 3],
                    [2, 3, 2, 3, 1, 0, 2],
                    [3, 3, 2, 2, 3, 2, 3],
                    [3, 2, 3, 2, 1, 2, 3]
                ]
                st.markdown(draw_svg_heatmap(grid_vals), unsafe_allow_html=True)
                
            col_e3, col_e4 = st.columns(2)
            
            # Chart 7: Streak Forecast
            with col_e3:
                st.markdown("#### 7. Streak Forecast Simulator")
                future_dates = [datetime.date.today() + datetime.timedelta(days=i) for i in range(1, 15)]
                curr_score = st.session_state.user_profile["fitness_score"]
                perf_prog = [min(100, curr_score + (i * 0.9)) for i in range(1, 15)]
                mod_prog = [max(40, min(100, curr_score + math.sin(i*0.5)*3)) for i in range(1, 15)]
                rel_prog = [max(30, curr_score - (i * 1.5)) for i in range(1, 15)]
                
                forecast_df = pd.DataFrame({
                    "Perfect Streak": perf_prog,
                    "Standard Pacing": mod_prog,
                    "Missed Sessions": rel_prog
                }, index=future_dates)
                st.line_chart(forecast_df)
                
            # Chart 8: AI weight/muscle prediction chart
            with col_e4:
                st.markdown("#### 8. AI Body Composition Projection")
                weight_hist = df["Weight"].tolist()
                slope = -0.13
                weight_proj = [weight_hist[-1] + slope * i for i in range(1, 8)]
                
                body_df = pd.DataFrame({
                    "Weight History (kg)": [weight_hist[i] if i < 30 else None for i in range(37)],
                    "AI Forecast": [None]*30 + weight_proj
                }, index=[f"Day {i}" for i in range(37)])
                st.line_chart(body_df)
                
            col_e5, col_e6 = st.columns(2)
            
            # Chart 9: Fitness Score Evolution comparison
            with col_e5:
                st.markdown("#### 9. Score Comparative Percentiles")
                cohort_df = pd.DataFrame({
                    "Alex Mercer (You)": df["Fitness Score"].tolist(),
                    "Global Average": [68]*30,
                    "Top 5% Threshold": [90]*30
                }, index=df["Date"])
                st.line_chart(cohort_df)
                
            # Chart 10: Workout Consistency Over Time
            with col_e6:
                st.markdown("#### 10. Workout Consistency Over Time")
                st.bar_chart(chart_df["Active Mins"])


# 11. SUB-PAGE 3: CHALLENGES & AI GENERATOR
def show_challenges():
    st.markdown('<div class="cinematic-title">CHALLENGES LIST</div>', unsafe_allow_html=True)
    
    st.markdown("### Active Challenges")
    for ch_name in st.session_state.joined_challenges:
        ch_info = next((c for c in st.session_state.challenges_db if c["name"] == ch_name), None)
        if ch_info:
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #00D4FF;">{ch_info['name']}</h4>
                            <p style="margin: 5px 0 0 0; font-size:12px; color: #A1A1AA;">{ch_info['meta']} • Difficulty: <b>{ch_info['difficulty']}</b></p>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 14px; font-weight:700; color:#22C55E;">+{ch_info['xp']} XP Reward</span><br>
                            <span style="font-size: 11px; color: #A1A1AA;">Duration: {ch_info['duration']}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    st.markdown("---")
    
    # 3. AI CHALLENGE GENERATOR
    st.markdown("### 🤖 AI Micro-Challenge Generator")
    st.markdown("Let the AI engine curate a custom daily challenge for you based on current weak points and training volume.")
    
    focus = st.selectbox("Focus Focus Area", ["HIIT Fat Loss", "Sleep Cleanliness", "Hydration Baseline", "Hypertrophy Push", "Core Shred", "Mobility Rehab"])
    diff = st.select_slider("Target Difficulty Level", options=["Novice", "Expert", "Elite Athlete"])
    
    if st.button("CURATE AI MICRO CHALLENGE", use_container_width=True):
        st.toast("AI Coach Nova compiling health logs...")
        time.sleep(1)
        
        # Determine values dynamically
        xp = 500 if diff == "Novice" else 1200 if diff == "Expert" else 2500
        success_rate = 94 if diff == "Novice" else 78 if diff == "Expert" else 52
        
        st.markdown(
            f"""
            <div class="glass-card elite-card" style="margin-top: 15px;">
                <span style="background: rgba(255, 215, 0, 0.2); color:#FFD700; font-size: 10px; font-weight: 700; padding: 2px 8px; border-radius: 20px; text-transform: uppercase;">GENERATED PLAN</span>
                <h3 style="margin: 10px 0 5px 0; color:#FFFFFF;">AI {focus} Challenge ({diff})</h3>
                <p style="margin: 0 0 10px 0; font-size:13px; color:#A1A1AA;">
                    Perform targeted physical workloads. Consistently log metrics. Nova projects this will optimize your cardiovascular recoverability by +4.2%.
                </p>
                <div style="display:flex; gap: 20px; font-size: 12px; color:#00D4FF;">
                    <span><b>Duration:</b> 24 Hours</span>
                    <span><b>Success Probability:</b> {success_rate}%</span>
                    <span><b>Reward:</b> +{xp} XP</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("ACCEPT AND ADD CHALLENGE", key="accept_ai_ch"):
            st.session_state.joined_challenges.append(f"AI {focus} Challenge")
            st.session_state.user_profile["xp"] += 100
            st.toast("Challenge Activated! +100 XP baseline")
            trigger_confetti()
            st.rerun()

    st.markdown("---")

    # Browse Available Row
    st.markdown("### Browse Netflix-Style Challenge Rows")
    cols_ch = st.columns(3)
    for idx, ch in enumerate(st.session_state.challenges_db[1:4]):
        with cols_ch[idx]:
            st.markdown(render_poster_html(ch["name"], ch["duration"], f"🏆 {ch['xp']} XP", ch["difficulty"], "orange", ch["image"]), unsafe_allow_html=True)
            if ch["name"] in st.session_state.joined_challenges:
                st.button("Already Joined", key=f"join_ch_btn_{idx}", disabled=True, use_container_width=True)
            else:
                if st.button(f"Join Challenge", key=f"join_ch_btn_{idx}", use_container_width=True):
                    st.session_state.joined_challenges.append(ch["name"])
                    st.toast(f"Joined {ch['name']}! Get ready to crush it!")
                    trigger_confetti()
                    st.rerun()


# 12. SUB-PAGE 4: ARENA (Head-to-head Friend challenges)
def show_arena():
    st.markdown('<div class="cinematic-title">CHALLENGE ARENA</div>', unsafe_allow_html=True)
    st.markdown("Compete directly with colleagues and friends in private fitness rooms. Live standings, streaks, and motivation tools.")
    
    col1, col2 = st.columns([1.1, 1])
    
    with col1:
        st.markdown("### Active Arena Competitions")
        for room in st.session_state.arena_rooms:
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom: 8px; margin-bottom:12px;">
                        <h4 style="margin:0; color:#7C3AED;">🏟️ {room['name']}</h4>
                        <span style="font-size:11px; background:rgba(0,212,255,0.1); color:#00D4FF; padding: 2px 8px; border-radius:12px;">Metric: {room['metric']} ({room['duration']})</span>
                    </div>
                """,
                unsafe_allow_html=True
            )
            
            # Leaderboard inside card
            for mem in room["members"]:
                prefix = "🥇" if mem["rank"] == 1 else "🥈" if mem["rank"] == 2 else "🥉" if mem["rank"] == 3 else "🏃"
                font_weight = "bold" if "You" in mem["name"] else "normal"
                color = "#FFD700" if mem["rank"] == 1 else "#FFFFFF"
                
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; padding: 6px 0; font-weight:{font_weight}; color:{color};">
                        <span>{prefix} {mem['name']}</span>
                        <span>{mem['score']:,} {room['metric']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            # Quick motivational triggers
            st.markdown("<div style='margin-top: 10px; display:flex; gap:10px;'>", unsafe_allow_html=True)
            sub_col1, sub_col2, sub_col3 = st.columns(3)
            with sub_col1:
                if st.button("🔥 Send Spark", key=f"spark_{room['id']}", use_container_width=True):
                    st.toast("Motivation sparks fired to all room members!")
            with sub_col2:
                if st.button("👏 Applaud All", key=f"clap_{room['id']}", use_container_width=True):
                    st.toast("Applaud notifications sent!")
            with sub_col3:
                if st.button("💪 Send Flex", key=f"flex_{room['id']}", use_container_width=True):
                    st.toast("Gym flexing emoji sent!")
            
            st.markdown("</div></div>", unsafe_allow_html=True)
            
    with col2:
        st.markdown("### Create Private Competition Arena")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        room_name = st.text_input("Competition Name", value="Summer Body War")
        metric = st.selectbox("Tracked Metric", ["Workout Streak", "Steps count", "Active Minutes", "XP Gained"])
        duration = st.selectbox("Competition Duration", ["7 Days", "14 Days", "30 Days"])
        friend_input = st.text_area("Invite Friends (comma-separated usernames)", value="sophia_chen, marcus_aurelius, emma_stone")
        
        if st.button("LAUNCH PRIVATE ARENA", use_container_width=True):
            members_list = [{"name": "Alex Mercer (You)", "score": 0, "rank": 1}]
            # Add invited users
            invited = [f.strip() for f in friend_input.split(",") if f.strip()]
            for idx, friend in enumerate(invited):
                members_list.append({"name": friend, "score": 0, "rank": idx+2})
                
            new_room = {
                "id": f"r{len(st.session_state.arena_rooms)+1}",
                "name": room_name,
                "metric": metric,
                "duration": duration,
                "leader": "Alex Mercer",
                "members": members_list
            }
            st.session_state.arena_rooms.append(new_room)
            st.toast(f"Private Arena '{room_name}' Curated!")
            trigger_confetti()
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)


# 13. SUB-PAGE 5: COMMUNITY PLATFORM (Instagram style)
def show_community():
    st.markdown('<div class="cinematic-title">ATHLETE FEED</div>', unsafe_allow_html=True)
    st.markdown("Instagram-style social community dashboard. Share proof of your workouts, milestones, and transformation stories.")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Masonry Feed
        for idx, post in enumerate(st.session_state.posts):
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 25px; padding: 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div style="display:flex; align-items:center; gap: 10px;">
                            <img src="{post['avatar']}" style="width:40px; height:40px; border-radius:50%; border:2px solid #00D4FF; object-fit:cover;" />
                            <div>
                                <h4 style="margin:0; font-size:15px; color:#FFFFFF;">{post['author']}</h4>
                                <span style="font-size:10px; color:#A1A1AA;">{post['stats']}</span>
                            </div>
                        </div>
                        <span style="font-size:11px; color:#A1A1AA;">Just Now</span>
                    </div>
                    <div style="width:100%; border-radius:8px; overflow:hidden; margin-bottom:12px; border:1px solid rgba(255,255,255,0.05);">
                        <img src="{post['image']}" style="width:100%; max-height:400px; object-fit:cover;" />
                    </div>
                    <p style="font-size:13px; color:#FFFFFF; margin-bottom:15px; line-height:1.5;">{post['caption']}</p>
                """,
                unsafe_allow_html=True
            )
            
            # IG Interaction system: Like, Flames, Respect, Elite Vote
            rxn_cols = st.columns(4)
            
            with rxn_cols[0]:
                if st.button(f"❤️ {post['likes']} Likes", key=f"like_{post['id']}_{idx}", use_container_width=True):
                    post["likes"] += 1
                    st.toast("Liked post!")
                    st.rerun()
            with rxn_cols[1]:
                if st.button(f"🔥 {post['flames']} Heat", key=f"flame_{post['id']}_{idx}", use_container_width=True):
                    post["flames"] += 1
                    st.toast("Motivations sent! 🔥")
                    st.rerun()
            with rxn_cols[2]:
                if st.button(f"💪 {post['respect']} Respect", key=f"respect_{post['id']}_{idx}", use_container_width=True):
                    post["respect"] += 1
                    st.toast("Respected!")
                    st.rerun()
            with rxn_cols[3]:
                # Elite Vote only available if membership is unlocked
                if st.session_state.elite_unlocked:
                    if st.button(f"⭐ {post['elite_votes']} Elite", key=f"elite_{post['id']}_{idx}", use_container_width=True):
                        post["elite_votes"] += 1
                        st.toast("Elite validation recorded!")
                        st.rerun()
                else:
                    st.button("⭐ Locked", key=f"elite_locked_{post['id']}_{idx}", disabled=True, help="Upgrade to Elite to submit Elite Rating Votes!", use_container_width=True)
            
            # Cheers Comments
            st.markdown("<div style='margin-top:15px; border-top:1px solid rgba(255,255,255,0.05); padding-top:10px;'>", unsafe_allow_html=True)
            for c in post["cheers"]:
                st.markdown(f"<p style='font-size:12px; margin: 3px 0;'><b style='color:#00D4FF;'>Cheer:</b> {c}</p>", unsafe_allow_html=True)
                
            cheer_inp = st.text_input("Add encouragement cheer...", key=f"cheer_in_{post['id']}_{idx}", placeholder="Keep crushing it!")
            if cheer_inp:
                post["cheers"].append(cheer_inp)
                st.toast("Cheer posted!")
                st.rerun()
                
            st.markdown("</div></div>", unsafe_allow_html=True)
            
    with col2:
        st.markdown("### Share Your Fitness Proof")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        # File uploader
        up_file = st.file_uploader("Upload Progress or Workout Photo", type=["png", "jpg", "jpeg"])
        post_caption = st.text_area("Write details / caption...", placeholder="Just hit my step goal for today! Level 14 in full swing...")
        metric_meta = st.text_input("Logged Stat (e.g. 500 kcal, 45 min HIIT)", value="🏃 10K Steps Completed")
        
        if st.button("BROADCAST TO FITNESSFLIX FEED", use_container_width=True):
            img_url = "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&q=80&w=600" # fallback
            
            if up_file is not None:
                try:
                    # Parse image as base64 string
                    bytes_data = up_file.getvalue()
                    base64_img = base64.b64encode(bytes_data).decode("utf-8")
                    img_url = f"data:image/png;base64,{base64_img}"
                except Exception as e:
                    st.error(f"Image compression issue: {e}")
                    
            new_post = {
                "id": len(st.session_state.posts) + 1,
                "author": "Alex Mercer (You)",
                "avatar": st.session_state.user_profile["avatar"],
                "image": img_url,
                "caption": post_caption,
                "stats": f"{metric_meta} | Streak: {st.session_state.user_profile['streak']} Days | Level {st.session_state.user_profile['level']}",
                "likes": 0,
                "flames": 0,
                "respect": 0,
                "cheers": [],
                "elite_votes": 0
            }
            st.session_state.posts.insert(0, new_post)
            st.toast("Success! Moment shared on community feed.")
            trigger_confetti()
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)


# 14. SUB-PAGE 6: GLOBAL LEADERBOARD (Rankings & Medals)
def show_leaderboard():
    st.markdown('<div class="cinematic-title">GLOBAL LEADERBOARD</div>', unsafe_allow_html=True)
    st.markdown("Worldwide ranks. Earn points by logging workouts, maintaining streaks, and helping community athletes stay accountable.")
    
    # Leaderboard categories
    l_tab1, l_tab2 = st.tabs(["🏆 Global Rankings", "⚔️ Active Challenge Rankings"])
    
    with l_tab1:
        # Predefined rankings
        rankings = [
            {"rank": 1, "name": "Marcus Aurelius", "score": 98, "streak": 72, "level": 19, "badge": "🔥 Momentum King", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150"},
            {"rank": 2, "name": "Sophia Chen", "score": 94, "streak": 100, "level": 24, "badge": "👑 100-Day Legend", "avatar": "https://images.unsplash.com/photo-1548690312-e3b507d8c110?auto=format&fit=crop&q=80&w=150"},
            {"rank": 3, "name": "Emma Stone", "score": 91, "streak": 38, "level": 16, "badge": "💪 Power Lifter", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150"},
            {"rank": 4, "name": "Alex Mercer (You)", "score": st.session_state.user_profile["fitness_score"], "streak": st.session_state.user_profile["streak"], "level": st.session_state.user_profile["level"], "badge": "⚡ Elite Performer", "avatar": st.session_state.user_profile["avatar"]},
            {"rank": 5, "name": "Bruce Wayne", "score": 85, "streak": 29, "level": 18, "badge": "🦇 Stealth Cardio", "avatar": "https://images.unsplash.com/photo-1526506118085-60ce8714f8c5?auto=format&fit=crop&q=80&w=150"},
            {"rank": 6, "name": "Clara Oswald", "score": 82, "streak": 15, "level": 11, "badge": "🏃 Steps Hero", "avatar": "https://images.unsplash.com/photo-1548690312-e3b507d8c110?auto=format&fit=crop&q=80&w=150"},
            {"rank": 7, "name": "Tony Stark", "score": 79, "streak": 22, "level": 15, "badge": "🤖 Tech Fitness", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&q=80&w=150"}
        ]
        
        # Sort just in case score changed
        rankings = sorted(rankings, key=lambda x: x["score"], reverse=True)
        for i, r in enumerate(rankings):
            r["rank"] = i + 1
            
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:grid; grid-template-columns: 80px 80px 1.5fr 1fr 1fr 1fr; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px; font-weight:700; color:#A1A1AA; font-size:12px; text-transform:uppercase;">
                <span>Rank</span>
                <span>Avatar</span>
                <span>Athlete Name</span>
                <span>Fitness Score</span>
                <span>Streak</span>
                <span>Title Badge</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        for r in rankings:
            medal = "🥇" if r["rank"] == 1 else "🥈" if r["rank"] == 2 else "🥉" if r["rank"] == 3 else f"#{r['rank']}"
            color = "#FFD700" if r["rank"] == 1 else "#C0C0C0" if r["rank"] == 2 else "#CD7F32" if r["rank"] == 3 else "#FFFFFF"
            is_me = "You" in r["name"]
            bg_style = "background: rgba(0, 212, 255, 0.05); border-radius:8px;" if is_me else ""
            
            st.markdown(
                f"""
                <div style="display:grid; grid-template-columns: 80px 80px 1.5fr 1fr 1fr 1fr; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.05); {bg_style} color:{color};">
                    <span style="font-size:1.1rem; font-weight:800; padding-left:10px;">{medal}</span>
                    <img src="{r['avatar']}" style="width:36px; height:36px; border-radius:50%; object-fit:cover; border: 1px solid rgba(255,255,255,0.15);" />
                    <span style="font-weight:700;">{r['name']} <span style="font-size:10px; color:#A1A1AA; font-weight:normal;">Lvl {r['level']}</span></span>
                    <span style="font-weight:800; color:#00D4FF;">{r['score']} pts</span>
                    <span>🔥 {r['streak']} days</span>
                    <span style="font-size:11px; background:rgba(124,58,237,0.1); color:#7C3AED; padding:2px 8px; border-radius:12px; width:fit-content; border:1px solid rgba(124,58,237,0.2);">{r['badge']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    with l_tab2:
        st.markdown("#### Challenge: 100-Day Elite Challenge Room Leaderboard")
        st.markdown("Room: #15 (Active participants)")
        st.write("Current Ranking updates occur live based on XP accumulation.")


# 15. SUB-PAGE 7: AI COACH HUB (Selectable coaches & Weekly reviews)
def show_ai_coach():
    st.markdown('<div class="cinematic-title">AI COACH PRO</div>', unsafe_allow_html=True)
    st.markdown("Select a training coach matching your personality preferences. Coaches remember goals and daily mission compliance.")
    
    col1, col2 = st.columns([1, 2.2])
    
    with col1:
        st.markdown("### Choose Your Coach")
        coaches = [
            ("Nova", "🔬 Coach Nova", "Analytical performance data analyst. Focuses on metrics, sleep patterns, and macro tracking."),
            ("Atlas", "🤝 Coach Atlas", "Empathetic, motivational support specialist. Focuses on mental strength and positive habits."),
            ("Titan", "🔥 Coach Titan", "Drill sergeant. High energy, zero excuses, maximum pushing, loud encouragement."),
            ("Apex", "🏆 Coach Apex", "Sports performance advisor. Emphasizes workout efficiency, structural endurance, and recovery ratios.")
        ]
        
        for key, name, desc in coaches:
            is_active = (st.session_state.active_coach == key)
            border_style = "border: 2px solid #00D4FF; background: rgba(0,212,255,0.05);" if is_active else "border: 1px solid rgba(255,255,255,0.05); background: rgba(255,255,255,0.01);"
            
            st.markdown(
                f"""
                <div style="padding: 16px; border-radius: 12px; margin-bottom: 12px; {border_style}">
                    <h4 style="margin: 0; color:#00D4FF;">{name}</h4>
                    <p style="margin: 5px 0 0 0; font-size:12px; color:#A1A1AA;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            if not is_active:
                if st.button(f"Activate {key}", key=f"act_{key}", use_container_width=True):
                    st.session_state.active_coach = key
                    st.toast(f"{key} is now your active AI coach!")
                    st.rerun()
                    
        st.markdown("---")
        
        # AI Weekly Sunday Review Summary
        st.markdown("### 📝 AI Weekly Performance Review")
        if st.button("GENERATE SUNDAY PERFORMANCE REVIEW", use_container_width=True):
            st.toast("Reading logs and database values...")
            time.sleep(1)
            st.markdown(
                """
                <div class="glass-card" style="margin-top: 10px;">
                    <h4 style="margin:0 0 10px 0; color:#FFD700;">Nova's Weekly Evaluation (Week 6)</h4>
                    <p style="font-size:12px; line-height:1.5; color:#A1A1AA;">
                        <b>Performance Summary:</b> Average daily steps increased by +12%, and workout compliance was 6/7 days. 
                        Hydration target of 3.0L was achieved on 5 days.<br><br>
                        <b>Best Habit:</b> Step consistency (avg 9,840 steps/day).<br>
                        <b>Weakest Habit:</b> Sleep durations (avg 6.8 hrs/night, target 8.0).<br>
                        <b>Action Step:</b> Shift bedtime to 10:30 PM. Complete hydration targets prior to 7 PM to improve sleep cycles.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
    with col2:
        st.markdown(f"### Chatting with Coach {st.session_state.active_coach}")
        
        # Accountability notification
        workout_logged = st.session_state.user_profile["today_mission"]["workout"]
        if not workout_logged:
            st.warning("⚠️ **Coach Warning:** You haven't completed today's workout target yet! Let's check in.")
        else:
            st.success("✅ **Coach Note:** Excellent work completing your Upper Body Shred mission today!")
            
        # Chat container
        chat_history = st.session_state.coach_messages[st.session_state.active_coach]
        for msg in chat_history:
            role_class = "chat-bubble-coach" if msg["role"] == "coach" else "chat-bubble-user"
            align_style = "text-align: left;" if msg["role"] == "coach" else "text-align: right;"
            st.markdown(
                f"""
                <div class="{role_class}">
                    <div style="font-size: 10px; font-weight: bold; color: #A1A1AA; margin-bottom: 4px;">{st.session_state.active_coach if msg['role']=='coach' else 'You'}</div>
                    <div style="font-size: 13px; line-height: 1.4; color: #FFFFFF;">{msg['content']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        chat_input = st.text_input("Consult your coach...", key="coach_chat_input", placeholder="Nova, review my sleep patterns this week...")
        if chat_input:
            # Add user message
            chat_history.append({"role": "user", "content": chat_input})
            
            # Simple AI responsive generator mock
            coach_reply = ""
            active = st.session_state.active_coach
            if active == "Nova":
                coach_reply = f"Alex, analyzing your input: '{chat_input}'. Your weekly steps log shows standard deviation is narrow. However, calorie targets vary. I suggest keeping intake within a 5% margin to prevent muscle catabolism."
            elif active == "Atlas":
                coach_reply = f"I hear you, Alex! The query '{chat_input}' shows you're thinking deeply about progress. Remember, progress is a journey, not a sprint. Celebrate small wins, like hit your hydration goals today!"
            elif active == "Titan":
                coach_reply = f"ALEX! NO MORE COMPLAINING ABOUT '{chat_input}'. Drop and give me 20 pushups! The only bad workout is the one you didn't do! Get back to the daily mission!"
            else: # Apex
                coach_reply = f"Mercer, referencing '{chat_input}': Athletic recovery requires structural synchronization. Ensure your glycogen levels are replenished within 30 minutes post-workout for optimal cell recovery."
                
            chat_history.append({"role": "coach", "content": coach_reply})
            st.rerun()


# 16. SUB-PAGE 8: PROFILE & TROPHY ROOM
def show_profile():
    st.markdown('<div class="cinematic-title">ATHLETE PROFILE</div>', unsafe_allow_html=True)
    
    p = st.session_state.user_profile
    
    # Render premium athlete banner and photo
    st.markdown(
        f"""
        <div style="position:relative; width:100%; height:260px; border-radius:16px; overflow:hidden; border:1px solid rgba(255,255,255,0.05); margin-bottom: 25px;">
            <img src="app_banner.png" style="width:100%; height:100%; object-fit:cover; filter: brightness(0.65);" />
            <div style="position:absolute; bottom:20px; left:25px; display:flex; align-items:center; gap:20px;">
                <img src="{p['avatar']}" style="width:90px; height:90px; border-radius:50%; border:3px solid #00D4FF; object-fit:cover; box-shadow:0 0 15px rgba(0,212,255,0.4);" />
                <div>
                    <h2 style="margin:0; font-size:1.8rem; color:#FFFFFF; font-family:'Poppins',sans-serif;">{p['name']}</h2>
                    <p style="margin:2px 0 0 0; font-size:12px; color:#00D4FF; font-weight:700;">🛡️ Elite Level {p['level']} Athlete • Rank #{p['global_rank']}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### Profile Summary & Activity Stats")
        st.markdown(
            f"""
            <div class="glass-card">
                <p style="font-size:13px; color:#A1A1AA; line-height:1.5; margin-bottom:20px;">
                    “I am Alex, focused on hitting peak physique markers and tracking consistency. 
                    Training using Coach Nova analytics to optimize sleep indices and daily step baselines.”
                </p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; text-align:center;">
                    <div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                        <span style="font-size:20px; font-weight:800; color:#00D4FF;">42 Days</span><br>
                        <span style="font-size:10px; color:#A1A1AA;">STREAK</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                        <span style="font-size:20px; font-weight:800; color:#7C3AED;">8,400 XP</span><br>
                        <span style="font-size:10px; color:#A1A1AA;">TOTAL POINTS</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                        <span style="font-size:20px; font-weight:800; color:#22C55E;">87/100</span><br>
                        <span style="font-size:10px; color:#A1A1AA;">FITNESS SCORE</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.05);">
                        <span style="font-size:20px; font-weight:800; color:#FFD700;">Rank #1</span><br>
                        <span style="font-size:10px; color:#A1A1AA;">AMONG FRIENDS</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # User Success Story uploader
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📝 Share Your Success Story")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        story_title = st.text_input("Story Title", value="How I locked consistency")
        story_body = st.text_area("Details", placeholder="Write down weight achievements or mental wins...")
        if st.button("PUBLISH SUCCESS STORY", use_container_width=True):
            st.session_state.user_stories.append({"title": story_title, "content": story_body})
            st.toast("Success Story Published! Added to profile story wall.")
            trigger_confetti()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        # Netflix Trophy Room (Achievements Gallery)
        st.markdown("### 🏆 Netflix Trophy Room")
        st.markdown(
            """
            <div class="glass-card">
                <p style="font-size: 12px; color: #A1A1AA; margin-bottom: 15px;">Hover and view milestone medals earned throughout the 100-Day Challenge.</p>
                <div class="trophy-grid">
                    <div class="trophy-item" title="Maintain a 30-day streak of daily missions. Status: UNLOCKED">
                        <div class="trophy-icon">🏆</div>
                        <div class="trophy-name">Consistency King</div>
                        <div class="trophy-desc">30-Day Streak Met</div>
                    </div>
                    <div class="trophy-item" title="Maintain a 10-day streak of daily missions. Status: UNLOCKED">
                        <div class="trophy-icon">🔥</div>
                        <div class="trophy-name">Momentum Builder</div>
                        <div class="trophy-desc">10-Day Streak Met</div>
                    </div>
                    <div class="trophy-item" title="Achieve a Master Fitness Score above 85. Status: UNLOCKED">
                        <div class="trophy-icon">⚡</div>
                        <div class="trophy-name">Elite Performer</div>
                        <div class="trophy-desc">Fitness Score > 85</div>
                    </div>
                    <div class="trophy-item" title="Complete 50 daily workouts. Status: UNLOCKED">
                        <div class="trophy-icon">💪</div>
                        <div class="trophy-name">Fitness Warrior</div>
                        <div class="trophy-desc">50 Workouts logged</div>
                    </div>
                    <div class="trophy-item locked" title="Complete the entire 100-Day Challenge. Status: LOCKED">
                        <div class="trophy-icon">👑</div>
                        <div class="trophy-name" style="color:#A1A1AA;">100-Day Legend</div>
                        <div class="trophy-desc" style="color:#A1A1AA;">Complete challenge</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # User stories listing
        if st.session_state.user_stories:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Your Success Stories")
            for story in st.session_state.user_stories:
                st.markdown(
                    f"""
                    <div class="glass-card" style="margin-bottom:10px;">
                        <h4 style="margin:0; color:#00D4FF;">{story['title']}</h4>
                        <p style="margin:5px 0 0 0; font-size:12px; color:#A1A1AA; line-height:1.4;">{story['content']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# 17. SUB-PAGE 9: ELITE MEMBERSHIP (Coupon REFRESH2026 activations)
def show_elite():
    st.markdown('<div class="cinematic-title">👑 ELITE UPGRADE</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### Unlock FitnessFlix Elite")
        st.markdown(
            """
            Upgrade to premium Elite Membership to access all visual models, expert diagnostics, and friend comparison features.
            <ul style="color: #A1A1AA; font-size:13px; line-height:1.8;">
                <li>✓ Full 10 Plotly Predictive Analytics charts (Streak forecasts, radar balances, body weight projections)</li>
                <li>✓ Active 1-on-1 coach queries with Nova, Atlas, Titan and Apex</li>
                <li>✓ Unlimited friend competition Arena rooms</li>
                <li>✓ Premium UI theme variations</li>
                <li>✓ CSV workout history data downloads</li>
                <li>✓ Elite verification badge next to your feed posts</li>
            </ul>
            """,
            unsafe_allow_html=True
        )
        
        if st.session_state.elite_unlocked:
            st.markdown(
                """
                <div class="glass-card elite-card" style="text-align: center; padding: 25px; margin-top:20px;">
                    <h3 class="elite-glowing-text">👑 ELITE MEMBERSHIP ACTIVATED</h3>
                    <p style="font-size:12px; color:#A1A1AA; margin-bottom:0;">Lifetime access is unlocked. Check out the Elite Analytics tab inside the Analytics module!</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            coupon = st.text_input("Enter Elite Access Code", placeholder="REFRESH2026")
            if st.button("ACTIVATE ELITE STATUS", use_container_width=True):
                if coupon.strip() == "REFRESH2026":
                    st.session_state.elite_unlocked = True
                    st.toast("Elite Access Unlocked successfully! Welcome to the Arena 👑")
                    trigger_confetti()
                    st.rerun()
                else:
                    st.error("Invalid Promo Coupon Code. Please verify.")
                    
    with col2:
        # Load and render generated image
        st.markdown("### Elite Access Premium Emblem")
        try:
            st.image("elite_badge.png", caption="FITNESSFLIX ELITE MEMBERSHIP ACCREDITATION", use_container_width=True)
        except Exception as e:
            st.warning("EMBLEM LOADING PENDING...")


# 18. SUB-PAGE 10: FITNESS WRAPPED (Spotify Wrapped Simulator)
def show_wrapped():
    st.markdown('<div class="cinematic-title">FITNESS WRAPPED</div>', unsafe_allow_html=True)
    st.markdown("Inspired by Spotify Wrapped. Review your cumulative progress milestones for this challenge session.")
    
    # Wrapped slideshow
    slides = [
        {
            "num": 1,
            "title": "Welcome to Your Wrapped",
            "stat": "EPISODE 2026",
            "desc": "A visual recap of the grit, consistency, and metrics logged over the past 42 days."
        },
        {
            "num": 2,
            "title": "Workouts Completed",
            "stat": "42 SESSIONS",
            "desc": "You completed 100% of scheduled workout modules. Caloric burn estimates exceed 18,900 kcal!"
        },
        {
            "num": 3,
            "title": "Unbreakable Consistency",
            "stat": "42 DAYS",
            "desc": "A perfect daily streak score! You belong to the top 2% of international FitnessFlix members."
        },
        {
            "num": 4,
            "title": "Fitness Score Growth",
            "stat": "+93% EVOLUTION",
            "desc": "Your index grew from 45/100 baseline up to 87/100 peak performance score. Peak health optimization achieved."
        },
        {
            "num": 5,
            "title": "Your Primary Advisor",
            "stat": "COACH NOVA",
            "desc": "You queried Coach Nova the most this week for analytical calculations and macro alignments."
        },
        {
            "num": 6,
            "title": "Unlocked Athlete Rank",
            "stat": "⚡ ELITE PERFORMER",
            "desc": "Share your card with other athletes on the Community feed. Keep crushing your limits!"
        }
    ]
    
    curr_slide = st.session_state.wrapped_slide
    slide_data = slides[curr_slide]
    
    # Render slide card using the wrapped-container styling
    st.markdown(
        f"""
        <div class="wrapped-container">
            <span style="font-size:12px; background:rgba(255,255,255,0.15); padding: 3px 12px; border-radius:20px; font-weight:700;">SLIDE {slide_data['num']} / {len(slides)}</span>
            <h2 style="margin:15px 0 5px 0; font-size:2.2rem; font-family:'Poppins',sans-serif; text-transform:uppercase;">{slide_data['title']}</h2>
            <div class="wrapped-stat-box">
                <span class="wrapped-big-number">{slide_data['stat']}</span>
            </div>
            <p style="color:#E2E8F0; font-size:14px; max-width:480px; margin: 0 auto; line-height:1.5;">{slide_data['desc']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Slide controllers
    ctrl_cols = st.columns([1, 1, 1])
    with ctrl_cols[0]:
        if st.button("⬅️ PREVIOUS SLIDE", disabled=(curr_slide == 0), use_container_width=True):
            st.session_state.wrapped_slide -= 1
            st.rerun()
    with ctrl_cols[1]:
        if st.button("🎁 EXPLODE PARTY", use_container_width=True):
            trigger_confetti()
    with ctrl_cols[2]:
        if st.button("NEXT SLIDE ➡️", disabled=(curr_slide == len(slides) - 1), use_container_width=True):
            st.session_state.wrapped_slide += 1
            st.rerun()
            
    # Reset button if on last slide
    if curr_slide == len(slides) - 1:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("REPLAY WRAPPED SUMMARY JOURNEY", use_container_width=True):
            st.session_state.wrapped_slide = 0
            st.rerun()


# 19. SUB-PAGE 11: SETTINGS & EXPORT DATA
def show_settings():
    st.markdown('<div class="cinematic-title">SYSTEM SETTINGS</div>', unsafe_allow_html=True)
    st.markdown("Configure target thresholds, UI parameter themes, and database operations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Profile Settings")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        user_name = st.text_input("Change Profile Name", value=st.session_state.user_profile["name"])
        if user_name != st.session_state.user_profile["name"]:
            st.session_state.user_profile["name"] = user_name
            st.toast("Profile Name updated!")
            st.rerun()
            
        st.markdown("<br><b>Target Goals Configuration:</b>", unsafe_allow_html=True)
        target_calories = st.number_input("Target Calorie Intake (kcal)", min_value=1200, max_value=5000, value=2200, step=100)
        target_steps = st.number_input("Target Daily Steps (steps)", min_value=4000, max_value=30000, value=10000, step=500)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("### Themes & Data Operations")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        theme_sel = st.selectbox("Application Visual Theme", ["Stealth Black (Default)", "Luxury Gold", "Neon Nebula (Purple)", "Cyber Cyberpunk"])
        st.info(f"Visual Theme applied: {theme_sel}")
        
        # Export Data to CSV
        st.markdown("<br><b>Data Operations:</b>", unsafe_allow_html=True)
        history_df = st.session_state.history_df
        csv_data = history_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📤 EXPORT WORKOUT HISTORY AS CSV",
            data=csv_data,
            file_name="fitnessflix_history_export.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)


# 20. PAGE NAVIGATION ROUTER
page = st.session_state.current_page
if page == "Home":
    show_home()
elif page == "My Journey":
    # Let's render Daily Mission checklist and Advanced Analytics together using subtabs
    subtab1, subtab2 = st.tabs(["🎯 Today's Mission Episodes", "📊 Advanced Analytics Dashboard"])
    with subtab1:
        show_my_journey()
    with subtab2:
        show_analytics()
elif page == "Challenges":
    show_challenges()
elif page == "Arena":
    show_arena()
elif page == "Community":
    show_community()
elif page == "Leaderboard":
    show_leaderboard()
elif page == "AI Coach":
    show_ai_coach()
elif page == "Profile":
    show_profile()
elif page == "Elite Badge":
    show_elite()
elif page == "Wrapped":
    show_wrapped()
elif page == "Settings":
    show_settings()
