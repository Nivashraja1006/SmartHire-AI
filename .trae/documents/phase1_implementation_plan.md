# SmartHire AI — Phase 1 Implementation Plan

## Repository Research
- **Current status:** Workspace is completely empty. No existing files, no git repository, no prior code.
- **Constraints confirmed:**
  - Only free & open-source technologies allowed (no paid APIs, no OpenAI/Gemini/Claude)
  - Stack: Flask, MySQL Community Edition, Scikit-learn, spaCy, NLTK, TF-IDF, Cosine Similarity, Flask-SocketIO
  - Phase 1 scope ONLY (no auth, no AI modules, no resume parsing, no DB models, no dashboard)
  - Professional landing page with modern AI SaaS style, responsive, lightweight animations

---

## Files and Modules to Create

| File / Directory | Purpose |
|---|---|
| `requirements.txt` | All Python dependencies (Flask, SQLAlchemy, Migrate, SocketIO, etc.) |
| `.env.example` | Environment variable template (MySQL creds, secret key, etc. — placeholders only) |
| `.gitignore` | Ignore venv, __pycache__, .env, uploads, etc. |
| `config.py` | Flask config classes (Development / Production) — reads `.env` |
| `run.py` | Application entry point — starts Flask + SocketIO server |
| `app/__init__.py` | Application factory: init Flask, SQLAlchemy, Migrate, SocketIO, register blueprints |
| `app/routes/__init__.py` | Blueprint package init |
| `app/routes/main.py` | Main blueprint — landing page route |
| `app/models/__init__.py` | Models package init (placeholder for Phase 2) |
| `app/services/__init__.py` | Services package init (placeholder) |
| `app/ai/__init__.py` | AI package init (placeholder for Phase 2+) |
| `app/utils/__init__.py` | Utils package init (placeholder) |
| `app/templates/base.html` | Base Jinja2 template with meta, CDN links (Chart.js, Font Awesome Free) |
| `app/templates/index.html` | Landing page extending base — hero, features, CTA |
| `app/static/css/style.css` | Custom CSS — modern AI SaaS theme, gradients, cards, responsive, animations |
| `app/static/js/main.js` | Lightweight JS — smooth scroll, scroll-triggered animations |
| `app/static/images/` | Empty image directory (placeholder) |
| `uploads/resumes/` | Empty directory for future resume uploads + `.gitkeep` |
| `uploads/job_descriptions/` | Empty directory for future job descriptions + `.gitkeep` |
| `tests/` | Empty test directory + `.gitkeep` |

---

## Implementation Steps (Dependency Order)

1. **Root-level config files**
   - Create `.gitignore`, `requirements.txt`, `.env.example`
   - Create `config.py` with `DevelopmentConfig` / `ProductionConfig` using `python-dotenv`

2. **Directory scaffold**
   - Create all package directories and `__init__.py` placeholders
   - Create `uploads/resumes`, `uploads/job_descriptions`, `tests`, `app/static/{css,js,images}`
   - Add `.gitkeep` files to empty uploads/tests dirs

3. **Flask application factory**
   - `app/__init__.py`: `create_app()` that loads config, inits SQLAlchemy/Migrate/SocketIO stubs, registers main blueprint
   - `app/routes/main.py`: Blueprint with single `GET /` route rendering `index.html`

4. **Entry point**
   - `run.py`: calls `create_app()`, runs via `socketio.run(app)` for future SocketIO compatibility

5. **Landing page templates**
   - `base.html`: Jinja2 base with blocks, meta tags, responsive viewport, CDN links for Chart.js and Font Awesome Free
   - `index.html`: Hero section (title + subtitle + desc + 2 CTA buttons), 4 feature cards (AI Resume Analysis, Smart Candidate Ranking, Skill Gap Detection, Real-Time Analytics), footer

6. **Styles and scripts**
   - `style.css`: CSS reset, modern AI SaaS palette (deep navy/indigo + teal accent + gradient bg), glass-morphism hero card, animated feature cards, hover states, media queries for mobile/tablet/desktop
   - `main.js`: Smooth-scroll for anchor links, IntersectionObserver reveal-on-scroll for feature cards

7. **Validation**
   - Create Python venv (if none active) and install requirements
   - Run `python run.py`
   - Open landing page in browser (http://localhost:5000) and confirm layout, responsiveness, no errors
   - Fix any import/runtime errors

---

## Dependencies and Considerations
- **Python version:** Target Python 3.10+ (widely available, compatible with all listed libs)
- **Virtual env:** Will create `venv/` inside project root (listed in `.gitignore`)
- **MySQL in Phase 1:** SQLAlchemy + Migrate configured but no models created; connection string sourced from `.env` (user fills in later); app will start even without MySQL running because no DB calls are made yet
- **SocketIO in Phase 1:** Initialized in factory, no event handlers yet; ensures app is SocketIO-ready from day 1
- **CDNs:** Chart.js + Font Awesome Free loaded from CDN (both free) to keep bundle light
- **No external premium assets:** All visuals via pure CSS gradients/shapes
- **Port:** Default 5000; configurable via `.env`

---

## Validation
1. `pip install -r requirements.txt` succeeds inside venv
2. `python run.py` starts the server without stack traces
3. HTTP GET `/` returns HTTP 200
4. Landing page renders: hero visible, buttons present, all 4 feature cards present, responsive at 375px/768px/1200px widths
5. No missing static asset 404s in browser dev tools
6. Console shows no JS errors

---

## Risks and Handling
| Risk | Handling |
|---|---|
| Python / pip not on PATH | Use `py -3` launcher on Windows; check and instruct user to install Python 3.10+ if missing |
| Port 5000 already in use | Allow `PORT` env override in config; `run.py` will read it |
| Missing VC++ build tools for some wheels on Windows | Pure-Wheel deps chosen wherever possible; `scikit-learn`/`spacy` are Phase 2+ so not installed yet (Phase 1 requirements are minimal) |
| Flask dev server on Windows + SocketIO warning | Use standard `eventlet`/`gevent` optional; Phase 1 works with Flask's built-in Werkzeug via `socketio.run(app, allow_unsafe_werkzeug=True)` for dev |
| Missing `.env` file on first run | Config defaults to sane DevelopmentConfig fallbacks so app starts even without `.env` |
