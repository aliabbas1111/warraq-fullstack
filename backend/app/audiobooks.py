"""The library's audiobooks: public-domain recordings from LibriVox, whose audio files the Internet Archive keeps.

The list lives in app/data/content/audiobooks.json, written and reviewed apart from the code like the book texts:

    {"intro": {"ar": [paragraph, ...], "en": [...]},
     "books": [{"slug", "ia" (archive.org item), "lv" (LibriVox id), "title", "title_ar", "author", "author_ar",
                "lang", "genre", "readers": [...], "translator", "secs", "added", "cover", "zip", "zip_mb",
                "librivox", "gid" (the Gutenberg text read, or null), "tracks": [[title, file, secs], ...],
                "about": {"en": [...]}, "context": {"en": [...]}}, ...]}

Pages: /audiobooks (all of them, by kind) and /audiobooks/<slug> (a player for its chapters, each chapter and the
whole book to download, and the library's own words about it); the home page shows the newest above "most viewed".
No audio is stored here: the player streams every chapter from archive.org, and the downloads come from there too.
"""
from urllib.parse import quote

from . import content, pages, seo
from .pages import BRAND, T, UI_LANGS, esc, lang_name, lang_q, own_text

HUE = 274  # the audiobooks' colour on the home page's category cards
GENRES = ("arab", "wis", "lif", "kid", "adv", "mys", "sf", "nov", "poe")
GENRE = {
    "arab": {"ar": "من التراث العربي والشرقي", "en": "From the Arab and Eastern heritage", "zh": "阿拉伯与东方经典",
             "fr": "Patrimoine arabe et oriental", "es": "Del legado árabe y oriental", "pt": "Do legado árabe e oriental",
             "ja": "アラブと東洋の古典", "de": "Aus dem arabischen und östlichen Erbe"},
    "wis": {"ar": "فلسفة وحكمة", "en": "Philosophy and wisdom", "zh": "哲学与智慧", "fr": "Philosophie et sagesse",
            "es": "Filosofía y sabiduría", "pt": "Filosofia e sabedoria", "ja": "哲学と知恵", "de": "Philosophie und Weisheit"},
    "lif": {"ar": "علوم وتاريخ وسير", "en": "Science, history and lives", "zh": "科学、历史与传记",
            "fr": "Sciences, histoire et vies", "es": "Ciencia, historia y vidas", "pt": "Ciência, história e vidas",
            "ja": "科学・歴史・伝記", "de": "Wissenschaft, Geschichte und Lebensläufe"},
    "kid": {"ar": "أدب الأطفال والحكايات", "en": "Children's books and fairy tales", "zh": "儿童文学与童话",
            "fr": "Jeunesse et contes", "es": "Infantil y cuentos de hadas", "pt": "Infantis e contos de fadas",
            "ja": "児童文学と童話", "de": "Kinderbücher und Märchen"},
    "adv": {"ar": "مغامرات", "en": "Adventure", "zh": "冒险", "fr": "Aventure", "es": "Aventura", "pt": "Aventura",
            "ja": "冒険", "de": "Abenteuer"},
    "mys": {"ar": "جريمة وغموض", "en": "Crime and mystery", "zh": "犯罪与悬疑", "fr": "Policier et mystère",
            "es": "Crimen y misterio", "pt": "Crime e mistério", "ja": "犯罪とミステリー", "de": "Krimi und Rätsel"},
    "sf": {"ar": "خيال علمي وقصص رعب", "en": "Science fiction and gothic tales", "zh": "科幻与哥特故事",
           "fr": "Science-fiction et récits gothiques", "es": "Ciencia ficción y relatos góticos",
           "pt": "Ficção científica e contos góticos", "ja": "SFとゴシック", "de": "Science-Fiction und Schauergeschichten"},
    "nov": {"ar": "روايات كلاسيكية", "en": "Classic novels", "zh": "经典小说", "fr": "Romans classiques",
            "es": "Novelas clásicas", "pt": "Romances clássicos", "ja": "古典小説", "de": "Klassische Romane"},
    "poe": {"ar": "شعر ومسرح وملاحم", "en": "Poetry, drama and epics", "zh": "诗歌、戏剧与史诗",
            "fr": "Poésie, théâtre et épopées", "es": "Poesía, teatro y epopeyas", "pt": "Poesia, teatro e epopeias",
            "ja": "詩・戯曲・叙事詩", "de": "Lyrik, Drama und Epen"},
}

S = {
    "ar": {
        "name": "كتب صوتية", "h1": "كتب صوتية مجانية", "n": "{n} كتاب صوتي",  # the counts are in the hundreds: كتاب, not كتاباً
        "t_list": "كتب صوتية مجانية: استمع أو حمّل {n} كتاب صوتي", "kinds": "أنواع الكتب الصوتية",
        "d_list": "{n} كتاب صوتي مجاني في الملك العام: حكايات وروايات وفلسفة وشعر، تستمع إليها في مكتبة الوراق أو تحمّلها كاملة.",
        "t_book": "{t} لـ{a}: كتاب صوتي مجاني", "t_book_na": "{t}: كتاب صوتي مجاني",
        "listen": "استمع الآن", "resume": "تابع من حيث توقفت", "dl_all": "حمّل الكتاب كاملاً (ZIP)", "dl_one": "تحميل",
        "mb": "{n} م.ب", "read_text": "اقرأ نص الكتاب", "chapters": "الفصول", "now": "يُشغَّل الآن", "speed": "السرعة",
        "facts": "معلومات التسجيل", "author": "المؤلف", "reader": "القراءة", "translator": "الترجمة", "length": "المدة",
        "parts": "الأجزاء", "lang": "اللغة", "src": "المصدر", "others": "{a} و{n} قرّاء آخرون", "volunteers": "متطوعو LibriVox",
        "about": "عن الكتاب", "context": "سياق الكتاب وأهميته", "more": "كتب صوتية أخرى",
        "rights": "هذا تسجيل من مشروع LibriVox، يقرؤه متطوعون ويهبونه للملك العام، وملفاته الصوتية محفوظة في أرشيف الإنترنت، ومنه يُشغَّل هنا ويُحمَّل. ووضع الملك العام يختلف من بلد إلى آخر، فتحقّق من قانون بلدك قبل إعادة نشره.",
        "strip_tag": "جديد", "strip_h": "كتب صوتية مجانية في المكتبة",
        "strip_p": "استمع إلى {n} كتاب صوتي من الملك العام وأنت في المكتبة، أو حمّل الكتاب كاملاً: من «كليلة ودمنة» إلى «مغامرات شيرلوك هولمز».",
        "strip_all": "كل الكتب الصوتية", "dur_hm": "{h} س {m} د", "dur_m": "{m} د",
        "share_txt": "استمع إلى «{t}» مجاناً في مكتبة الوراق", "listen_book": "استمع إليه كتاباً صوتياً",
    },
    "en": {
        "name": "Audiobooks", "h1": "Free audiobooks", "n": "{n} audiobooks",
        "t_list": "Free audiobooks: listen to or download {n} audiobooks", "kinds": "Kinds of audiobooks",
        "d_list": "{n} free public-domain audiobooks: fairy tales, novels, philosophy and poetry, to listen to at Al-Warraq Library or download whole.",
        "t_book": "{t} by {a}: free audiobook", "t_book_na": "{t}: free audiobook",
        "listen": "Listen now", "resume": "Resume where you stopped", "dl_all": "Download the whole book (ZIP)", "dl_one": "Download",
        "mb": "{n} MB", "read_text": "Read the text", "chapters": "Chapters", "now": "Now playing", "speed": "Speed",
        "facts": "About the recording", "author": "Author", "reader": "Read by", "translator": "Translation", "length": "Length",
        "parts": "Parts", "lang": "Language", "src": "Source", "others": "{a} and {n} other readers", "volunteers": "LibriVox volunteers",
        "about": "About this book", "context": "Context and significance", "more": "More audiobooks",
        "rights": "This is a LibriVox recording, read by volunteers and dedicated to the public domain; its audio files are kept by the Internet Archive, which plays and serves them here. Public-domain status differs from country to country, so check the law where you live before republishing it.",
        "strip_tag": "New", "strip_h": "Free audiobooks at the library",
        "strip_p": "Listen to {n} public-domain audiobooks right here, or download a whole book: from Kalila and Dimna to The Adventures of Sherlock Holmes.",
        "strip_all": "All audiobooks", "dur_hm": "{h} h {m} min", "dur_m": "{m} min",
        "share_txt": "Listen to “{t}” free at Al-Warraq Library", "listen_book": "Listen to the audiobook",
    },
    "zh": {"name": "有声书", "h1": "免费有声书", "n": "{n} 部有声书", "listen": "立即收听", "dl_all": "下载整本书（ZIP）",
           "dl_one": "下载", "read_text": "阅读原文", "chapters": "章节", "now": "正在播放", "speed": "语速", "facts": "录音信息",
           "author": "作者", "reader": "朗读", "translator": "译者", "length": "时长", "parts": "分段", "lang": "语言", "src": "来源",
           "about": "关于本书", "context": "背景与意义", "more": "更多有声书", "strip_tag": "新", "strip_h": "图书馆里的免费有声书",
           "strip_all": "全部有声书", "dur_hm": "{h}小时{m}分钟", "dur_m": "{m}分钟", "listen_book": "收听有声书"},
    "fr": {"name": "Livres audio", "h1": "Livres audio gratuits", "n": "{n} livres audio", "listen": "Écouter",
           "dl_all": "Télécharger le livre entier (ZIP)", "dl_one": "Télécharger", "read_text": "Lire le texte", "chapters": "Chapitres",
           "now": "En cours", "speed": "Vitesse", "facts": "L’enregistrement", "author": "Auteur", "reader": "Lu par",
           "translator": "Traduction", "length": "Durée", "parts": "Parties", "lang": "Langue", "src": "Source",
           "about": "À propos du livre", "context": "Contexte et portée", "more": "Autres livres audio", "strip_tag": "Nouveau",
           "strip_h": "Des livres audio gratuits à la bibliothèque", "strip_all": "Tous les livres audio", "dur_hm": "{h} h {m} min",
           "dur_m": "{m} min", "listen_book": "Écouter le livre audio"},
    "es": {"name": "Audiolibros", "h1": "Audiolibros gratis", "n": "{n} audiolibros", "listen": "Escuchar",
           "dl_all": "Descargar el libro completo (ZIP)", "dl_one": "Descargar", "read_text": "Leer el texto", "chapters": "Capítulos",
           "now": "Sonando", "speed": "Velocidad", "facts": "La grabación", "author": "Autor", "reader": "Lectura",
           "translator": "Traducción", "length": "Duración", "parts": "Partes", "lang": "Idioma", "src": "Fuente",
           "about": "Sobre el libro", "context": "Contexto e importancia", "more": "Más audiolibros", "strip_tag": "Nuevo",
           "strip_h": "Audiolibros gratis en la biblioteca", "strip_all": "Todos los audiolibros", "dur_hm": "{h} h {m} min",
           "dur_m": "{m} min", "listen_book": "Escuchar el audiolibro"},
    "pt": {"name": "Audiolivros", "h1": "Audiolivros grátis", "n": "{n} audiolivros", "listen": "Ouvir",
           "dl_all": "Baixar o livro inteiro (ZIP)", "dl_one": "Baixar", "read_text": "Ler o texto", "chapters": "Capítulos",
           "now": "Tocando", "speed": "Velocidade", "facts": "A gravação", "author": "Autor", "reader": "Leitura",
           "translator": "Tradução", "length": "Duração", "parts": "Partes", "lang": "Idioma", "src": "Fonte",
           "about": "Sobre o livro", "context": "Contexto e importância", "more": "Mais audiolivros", "strip_tag": "Novo",
           "strip_h": "Audiolivros grátis na biblioteca", "strip_all": "Todos os audiolivros", "dur_hm": "{h} h {m} min",
           "dur_m": "{m} min", "listen_book": "Ouvir o audiolivro"},
    "ja": {"name": "オーディオブック", "h1": "無料オーディオブック", "n": "{n} 冊のオーディオブック", "listen": "今すぐ聴く",
           "dl_all": "本全体をダウンロード（ZIP）", "dl_one": "ダウンロード", "read_text": "本文を読む", "chapters": "章",
           "now": "再生中", "speed": "速度", "facts": "録音について", "author": "著者", "reader": "朗読", "translator": "翻訳",
           "length": "時間", "parts": "パート", "lang": "言語", "src": "出典", "about": "この本について", "context": "背景と意義",
           "more": "ほかのオーディオブック", "strip_tag": "新着", "strip_h": "図書館の無料オーディオブック",
           "strip_all": "すべてのオーディオブック", "dur_hm": "{h}時間{m}分", "dur_m": "{m}分", "listen_book": "オーディオブックで聴く"},
    "de": {"name": "Hörbücher", "h1": "Kostenlose Hörbücher", "n": "{n} Hörbücher", "listen": "Jetzt anhören",
           "dl_all": "Ganzes Buch herunterladen (ZIP)", "dl_one": "Herunterladen", "read_text": "Den Text lesen", "chapters": "Kapitel",
           "now": "Läuft gerade", "speed": "Tempo", "facts": "Zur Aufnahme", "author": "Autor", "reader": "Gelesen von",
           "translator": "Übersetzung", "length": "Dauer", "parts": "Teile", "lang": "Sprache", "src": "Quelle",
           "about": "Über das Buch", "context": "Hintergrund und Bedeutung", "more": "Weitere Hörbücher", "strip_tag": "Neu",
           "strip_h": "Kostenlose Hörbücher in der Bibliothek", "strip_all": "Alle Hörbücher", "dur_hm": "{h} Std. {m} Min.",
           "dur_m": "{m} Min.", "listen_book": "Als Hörbuch anhören"},
}
for _ui in UI_LANGS:  # a word a language lacks is shown in English
    S[_ui] = dict(S["en"], **S.get(_ui, {}))

ARCHIVE = "https://archive.org"


def _data() -> dict:
    return content._load("audiobooks.json", {})


def books() -> list:
    """Every audiobook, newest first (one day's in the file's order)."""
    items = _data().get("books", [])
    return sorted(items, key=lambda b: b.get("added", ""), reverse=True)


def book(slug: str):
    return next((b for b in _data().get("books", []) if b["slug"] == slug), None)


def by_gid(gid):
    """The audiobook reading this Gutenberg text, if the library has one (its book page links to it)."""
    return next((b for b in _data().get("books", []) if gid and b.get("gid") == gid), None) if gid else None


def texts(conn) -> dict:
    """{Gutenberg number: book row} for the texts the audiobooks read (an audiobook's page links to its text's page).
    books.gid has no index, so it is one pass over the catalogue for all of them, made when the server starts
    (main.lifespan) and kept a day."""
    path_ = next((r[2] for r in conn.execute("PRAGMA database_list") if r[1] == "main"), "")

    def find():
        gids = sorted({b["gid"] for b in _data().get("books", []) if b.get("gid")})
        if not gids:
            return {}
        rows = conn.execute("SELECT * FROM books WHERE gid IN (%s) ORDER BY id DESC" % ",".join("?" * len(gids)), gids)
        return {r["gid"]: r for r in rows}  # the lowest id wins where two rows share a number
    return pages._cached(("audiobook-texts", path_), 86400, find)


def default_ui(b) -> str:
    return "ar" if b.get("lang") == "ar" else "en"


def path(b) -> str:
    return "/audiobooks/" + b["slug"]


def audio_url(b, name: str) -> str:
    return "%s/download/%s/%s" % (ARCHIVE, b["ia"], quote(name))


def thumb_url(b) -> str:
    return "%s/services/img/%s" % (ARCHIVE, b["ia"])  # the item's small square picture


def title(b, ui: str) -> str:
    return (b.get("title_ar") or b["title"]) if ui == "ar" else b["title"]


def author(b, ui: str) -> str:
    return (b.get("author_ar") or b.get("author", "")) if ui == "ar" else b.get("author", "")


def duration(secs: int, ui: str) -> str:
    s = S[ui]
    h, m = divmod(round((secs or 0) / 60), 60)
    return s["dur_hm"].format(h=h, m=m) if h else s["dur_m"].format(m=max(m, 1))


def _clock(secs: int) -> str:
    h, rest = divmod(int(secs or 0), 3600)
    return ("%d:%02d:%02d" % (h, rest // 60, rest % 60)) if h else "%d:%02d" % (rest // 60, rest % 60)


def _iso(secs: int) -> str:
    h, rest = divmod(int(secs or 0), 3600)
    return "PT%dH%dM%dS" % (h, rest // 60, rest % 60)


def text(b, key: str, ui: str) -> content.Text:
    return content.Text(*content._pick(b.get(key, {}), ui))


def readers(b, ui: str) -> str:
    names = b.get("readers") or []
    if not names:
        return S[ui]["volunteers"]
    if len(names) <= 4:
        return "، ".join(names) if ui == "ar" else ", ".join(names)
    return S[ui]["others"].format(a=("، " if ui == "ar" else ", ").join(names[:3]), n=len(names) - 3)


def _card(b, ui: str, q: str) -> str:
    t, a = title(b, ui), author(b, ui)
    return ('<a class="ab-card" href="%s%s"><span class="ab-cv"><img src="%s" alt="" loading="lazy" decoding="async" '
            'referrerpolicy="no-referrer"></span><b%s>%s</b><small>%s</small><span class="ab-d">%s · %s</span></a>'
            % (esc(path(b)), q, esc(thumb_url(b)), ' lang="ar"' if b.get("lang") == "ar" and ui != "ar" else "", esc(t),
               esc(a), esc(duration(b.get("secs"), ui)), esc(lang_name(b.get("lang"), ui))))


AB_CSS = """
.ab-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px;margin:10px 0 6px}
.ab-card{display:flex;flex-direction:column;gap:4px;padding:10px;background:var(--card);border:1px solid var(--line);border-radius:16px;text-decoration:none;color:var(--ink);transition:transform .25s cubic-bezier(.34,1.56,.64,1),border-color .2s}
.ab-card:hover{transform:translateY(-3px);border-color:var(--brand-2)}
.ab-cv{display:block;aspect-ratio:1;border-radius:12px;overflow:hidden;background:linear-gradient(150deg,hsl(274 40% 30%),hsl(274 46% 18%));margin-bottom:4px}
.ab-cv img{width:100%;height:100%;object-fit:cover;display:block}
.ab-card b{font-size:.95rem;line-height:1.4}.ab-card small,.ab-d{color:var(--muted);font-size:.82rem;line-height:1.5}
.ab-g h2 small{color:var(--muted);font-weight:500;font-size:.85rem}
.ab .cover{aspect-ratio:1;background:linear-gradient(150deg,hsl(274 40% 30%),hsl(274 46% 18%))}.ab .cover img{opacity:1}
.book.ab>.cover{width:240px;max-width:100%}
.ab-player{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:16px 18px;margin:6px 0 18px;box-shadow:var(--shadow)}
.ab-now{display:flex;align-items:center;gap:12px;margin:0 0 10px}.ab-now small{display:block;color:var(--muted);font-size:.8rem}.ab-now b{font-size:1.02rem}
.ab-eq{display:inline-flex;align-items:flex-end;gap:3px;height:22px;flex:none}.ab-eq i{width:4px;height:30%;border-radius:2px;background:var(--brand-2)}
.ab-player.playing .ab-eq i{animation:abq .9s ease-in-out infinite}.ab-eq i:nth-child(2){animation-delay:-.3s}.ab-eq i:nth-child(3){animation-delay:-.6s}.ab-eq i:nth-child(4){animation-delay:-.15s}
@keyframes abq{0%,100%{height:25%}50%{height:100%}}
@media (prefers-reduced-motion:reduce){.ab-player.playing .ab-eq i{animation:none;height:70%}}
.ab-player audio{width:100%;display:block}
.ab-tools{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:10px 0 0;color:var(--muted);font-size:.88rem}
.ab-tools button{font:inherit;padding:3px 11px;border-radius:10px;border:1.5px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
.ab-tools button[aria-pressed="true"]{border-color:var(--brand-2);color:var(--brand);font-weight:600}
.ab-tools .ab-res{margin-inline-start:auto;border-color:var(--brand-2);color:var(--brand)}
.ab-player h2{font-size:1rem;margin:16px 0 8px}.ab-player h2 small{color:var(--muted);font-weight:500}
ol.ab-trk{list-style:none;margin:0;padding:0;max-height:440px;overflow:auto;border-top:1px solid var(--line)}
ol.ab-trk li{display:flex;align-items:center;gap:6px;border-bottom:1px solid var(--line)}
.trk{flex:1 1 auto;min-width:0;display:flex;align-items:center;gap:10px;padding:9px 6px;border:0;background:none;color:var(--ink);font:inherit;text-align:start;cursor:pointer}
.trk:hover{color:var(--brand)}.trk .n{flex:none;min-width:2.2em;color:var(--muted);font-size:.85rem}.trk .tt{flex:1 1 auto;min-width:0}
.trk .d{flex:none;color:var(--muted);font-size:.85rem;font-variant-numeric:tabular-nums}
.trk[aria-current="true"]{color:var(--brand);font-weight:600}.trk[aria-current="true"] .n{color:var(--brand)}
.ab-dl{flex:none;display:grid;place-items:center;width:34px;height:34px;border-radius:10px;color:var(--muted)}.ab-dl:hover{background:var(--soft);color:var(--brand)}
.ab-dl.busy{opacity:.5;pointer-events:none}
"""

DL_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11 M7 10l5 5 5-5 M5 20h14"/></svg>')

# The player: a chapter's button plays it, the next follows by itself, the place reached is kept in this browser for
# next time, and a chapter's download link saves the file (archive.org lets pages fetch it) instead of opening it.
PLAYER_JS = r"""<script>(function(){var a=document.getElementById('abAudio');if(!a)return;var box=document.getElementById('player'),now=document.getElementById('abNow'),
list=[].slice.call(document.querySelectorAll('.trk')),key='warraq-ab:'+a.dataset.slug,cur=0,saved=null,last=0;
function pick(i,play,at){var b=list[i];if(!b)return;cur=i;list.forEach(function(x,j){x.setAttribute('aria-current',j===i?'true':'false');});
if(a.getAttribute('src')!==b.dataset.src)a.setAttribute('src',b.dataset.src);now.textContent=b.dataset.t;
if(at){a.addEventListener('loadedmetadata',function f(){a.removeEventListener('loadedmetadata',f);try{a.currentTime=at;}catch(e){}});a.load();}
if(play){var p=a.play();if(p&&p.catch)p.catch(function(){});}}
list.forEach(function(b,i){b.addEventListener('click',function(){pick(i,true);});});
a.addEventListener('ended',function(){if(cur+1<list.length)pick(cur+1,true);});
a.addEventListener('play',function(){box.classList.add('playing');});a.addEventListener('pause',function(){box.classList.remove('playing');});
a.addEventListener('timeupdate',function(){var t=Date.now();if(t-last<4000)return;last=t;try{localStorage.setItem(key,JSON.stringify([cur,Math.floor(a.currentTime)]));}catch(e){}});
try{saved=JSON.parse(localStorage.getItem(key)||'null');}catch(e){}
var res=document.getElementById('abResume');if(saved&&list[saved[0]]&&(saved[0]>0||saved[1]>20)&&res){res.hidden=false;res.addEventListener('click',function(){res.hidden=true;pick(saved[0],true,saved[1]);});}
var go=document.getElementById('abPlay');if(go)go.addEventListener('click',function(e){e.preventDefault();box.scrollIntoView({behavior:'smooth',block:'start'});if(a.paused)pick(cur,true);});
[].forEach.call(document.querySelectorAll('.ab-tools [data-r]'),function(b){b.addEventListener('click',function(){a.playbackRate=+b.dataset.r;
[].forEach.call(document.querySelectorAll('.ab-tools [data-r]'),function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});});});
[].forEach.call(document.querySelectorAll('.ab-dl'),function(l){l.addEventListener('click',function(e){if(!window.fetch||!window.URL||!URL.createObjectURL)return;e.preventDefault();l.classList.add('busy');
fetch(l.href).then(function(r){if(!r.ok)throw 0;return r.blob();}).then(function(bl){var u=URL.createObjectURL(bl),x=document.createElement('a');x.href=u;x.download=l.dataset.name;document.body.appendChild(x);x.click();x.remove();setTimeout(function(){URL.revokeObjectURL(u);},4000);})
.catch(function(){window.open(l.href,'_blank','noopener');}).then(function(){l.classList.remove('busy');});});});
var im=document.getElementById('abCover');if(im){if(im.complete&&!im.naturalWidth)im.remove();else im.addEventListener('error',function(){im.remove();});}})();</script>"""


def listing_page(base: str, ui: str, nonce: str = "") -> str:
    s, q, items = S[ui], lang_q(ui), books()
    n = len(items)
    groups = [(g, [b for b in items if b.get("genre") == g]) for g in GENRES]
    groups = [(g, bs) for g, bs in groups if bs]
    chips = "".join('<a href="#%s">%s</a>' % (g, esc(GENRE[g][ui])) for g, _ in groups)
    sections = "".join('<section class="ab-g" id="%s"><h2>%s <small>(%d)</small></h2><div class="ab-grid">%s</div></section>'
                       % (g, esc(GENRE[g][ui]), len(bs), "".join(_card(b, ui, q) for b in bs)) for g, bs in groups)
    intro = content.Text(*content._pick(_data().get("intro", {}), ui))
    desc = s["d_list"].format(n=n)
    body = ('<p class="crumbs"><a href="/%s">%s</a> / %s</p><h1>%s</h1><p class="desc">%s</p>%s'
            '<nav class="chips" aria-label="%s">%s</nav>%s'
            % (q, esc(T[ui]["home"]), esc(s["name"]), esc(s["h1"]), esc(desc),
               ('<section class="intro">%s</section>' % own_text(intro, ui)) if intro else "", esc(s["kinds"]), chips, sections))
    ld = seo._ld({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": s["t_list"].format(n=n), "description": desc, "url": base + "/audiobooks",
         "inLanguage": ui, "isPartOf": {"@id": base + "/#site"},
         "mainEntity": {"@type": "ItemList", "numberOfItems": n, "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": base + path(b), "name": b["title"]} for i, b in enumerate(items)]}},
        seo._breadcrumbs(base, ui, s["name"], "/audiobooks")]})
    return seo.with_nonce(seo._shell(ui, base, "/audiobooks", s["t_list"].format(n=n) + " | " + BRAND[ui], desc, body, ld,
                                     nonce=nonce, extra_css=seo.ARTICLE_CSS + AB_CSS), nonce)


def _related(b) -> list:
    others = [o for o in books() if o["slug"] != b["slug"]]
    same = [o for o in others if o.get("author") == b.get("author")]
    kind = [o for o in others if o.get("genre") == b.get("genre") and o not in same]
    return (same + kind)[:8]


def book_page(conn, b, base: str, ui: str, nonce: str = "", ads: bool = True) -> str:
    s, t, q = S[ui], T[ui], lang_q(ui)
    name, by = title(b, ui), author(b, ui)
    url = base + path(b)
    about, ctx = text(b, "about", ui), text(b, "context", ui)
    desc = pages._cut(pages._plain(about[0])) if about else s["d_list"].format(n=len(books()))
    page_title = (s["t_book"].format(t=name, a=by) if by else s["t_book_na"].format(t=name)) + " | " + BRAND[ui]
    tracks = b.get("tracks") or []
    first = audio_url(b, tracks[0][1]) if tracks else ""

    read = ""
    row = texts(conn).get(b.get("gid"))
    if row:
        read = '<a class="btn alt" href="%s%s">%s</a>' % (esc(pages.canonical_path(row)), q, esc(s["read_text"]))
    size = (" · " + s["mb"].format(n=b["zip_mb"])) if b.get("zip_mb") else ""
    btns = ('<a class="btn" id="abPlay" href="#player">%s</a><a class="btn alt" href="%s" rel="nofollow">%s%s</a>%s'
            % (esc(s["listen"]), esc(b["zip"]), esc(s["dl_all"]), esc(size), read))
    tags = ('<a class="tag" href="/audiobooks%s">%s</a><span class="tag">%s</span><span class="tag">%s</span>'
            % (q, esc(s["name"]), esc(lang_name(b.get("lang"), ui)), esc(duration(b.get("secs"), ui))))
    facts = ""
    if by:
        facts += "<dt>%s</dt><dd>%s</dd>" % (esc(s["author"]), esc(by))
    facts += "<dt>%s</dt><dd>%s</dd>" % (esc(s["reader"]), esc(readers(b, ui)))
    if b.get("translator"):
        facts += "<dt>%s</dt><dd>%s</dd>" % (esc(s["translator"]), esc(b["translator"]))
    facts += "<dt>%s</dt><dd>%s</dd><dt>%s</dt><dd>%d</dd><dt>%s</dt><dd>%s</dd>" % (
        esc(s["length"]), esc(_clock(b.get("secs"))), esc(s["parts"]), len(tracks), esc(s["lang"]), esc(lang_name(b.get("lang"), ui)))
    facts += '<dt>%s</dt><dd><a href="%s" target="_blank" rel="noopener nofollow">LibriVox</a> · <a href="%s/details/%s" target="_blank" rel="noopener nofollow">Internet Archive</a></dd>' % (
        esc(s["src"]), esc(b.get("librivox") or "https://librivox.org/"), ARCHIVE, esc(b["ia"]))

    rows = "".join(
        '<li><button type="button" class="trk" data-src="%s" data-t="%s" aria-current="%s"><span class="n">%d</span>'
        '<span class="tt">%s</span><span class="d">%s</span></button><a class="ab-dl" href="%s" data-name="%s" target="_blank" '
        'rel="nofollow noopener" aria-label="%s: %s">%s</a></li>'
        % (esc(audio_url(b, f)), esc(tt), "true" if i == 0 else "false", i + 1, esc(tt), esc(_clock(sec)), esc(audio_url(b, f)),
           esc(f), esc(s["dl_one"]), esc(tt), DL_ICON) for i, (tt, f, sec) in enumerate(tracks))
    speeds = "".join('<button type="button" data-r="%s" aria-pressed="%s">%s×</button>' % (r, "true" if r == "1" else "false", r)
                     for r in ("0.75", "1", "1.25", "1.5", "2"))
    player = ('<section class="ab-player" id="player" aria-label="%s"><div class="ab-now"><span class="ab-eq" aria-hidden="true">'
              '<i></i><i></i><i></i><i></i></span><div><small>%s</small><b id="abNow">%s</b></div></div>'
              '<audio id="abAudio" controls preload="none" src="%s" data-slug="%s"></audio>'
              '<div class="ab-tools"><span>%s</span>%s<button type="button" class="ab-res" id="abResume" hidden>%s</button></div>'
              '<h2>%s <small>(%d)</small></h2><ol class="ab-trk">%s</ol></section>'
              % (esc(s["chapters"]), esc(s["now"]), esc(tracks[0][0] if tracks else ""), esc(first), esc(b["slug"]), esc(s["speed"]),
                 speeds, esc(s["resume"]), esc(s["chapters"]), len(tracks), rows))
    about_html = ""
    if about:
        about_html += '<section class="about"><h2>%s</h2>%s</section>' % (esc(s["about"]), own_text(about, ui))
    if ctx:
        about_html += '<section class="about"><h2>%s</h2>%s</section>' % (esc(s["context"]), own_text(ctx, ui))
    takedown = '<a href="/takedown?%su=%s">%s</a>' % (esc(lang_q(ui, amp=True)), quote(path(b), safe=""), esc(t["takedown_a"]))
    rights = '<p class="rights pd">%s %s %s</p>' % (esc(s["rights"]), esc(t["takedown_q"]), takedown)
    rel = _related(b)
    rel_html = ('<h2>%s</h2><div class="ab-grid">%s</div>' % (esc(s["more"]), "".join(_card(o, ui, q) for o in rel))) if rel else ""
    msg = s["share_txt"].format(t=name)
    share = ('<div class="share"><span>%s</span><a class="sh wa" href="https://wa.me/?text=%s" target="_blank" rel="noopener nofollow">%s%s</a>'
             '<a class="sh tg" href="https://t.me/share/url?url=%s&amp;text=%s" target="_blank" rel="noopener nofollow">%s%s</a>'
             '<a class="sh fb" href="https://www.facebook.com/sharer/sharer.php?u=%s" target="_blank" rel="noopener nofollow">%s%s</a>'
             '<button type="button" class="sh cp" id="copyBtn" data-url="%s" data-done="%s">%s<span>%s</span></button></div>'
             % (esc(t["share"]), quote(msg + " " + url, safe=""), pages.SHARE_ICONS["wa"], esc(t["wa"]), quote(url, safe=""),
                quote(msg, safe=""), pages.SHARE_ICONS["tg"], esc(t["tg"]), quote(url, safe=""), pages.SHARE_ICONS["fb"], esc(t["fb"]),
                esc(url), esc(t["copied"]), pages.SHARE_ICONS["link"], esc(t["copy"])))
    text_lang = ' lang="%s"' % b["lang"] if b.get("lang") in ("ar", "en") and b["lang"] != ui else ""
    body = ('<p class="crumbs"><a href="/%s">%s</a> / <a href="/audiobooks%s">%s</a> / <span>%s</span></p>'
            '<article class="book ab"><div class="cover"><img id="abCover" src="%s" alt="%s" decoding="async" referrerpolicy="no-referrer"></div>'
            '<div><h1%s>%s</h1>%s<div class="tags">%s</div><div class="btns">%s</div>%s<p class="desc">%s</p>'
            '<h2 class="facts-h">%s</h2><dl>%s</dl></div></article>%s%s%s%s'
            % (q, esc(t["home"]), q, esc(s["name"]), esc(name), esc(b.get("cover") or thumb_url(b)), esc(name),
               text_lang if ui != "ar" else "", esc(name), ('<p class="by">%s</p>' % esc(by)) if by else "", tags, btns, share,
               esc(desc), esc(s["facts"]), facts, player, about_html, rights, rel_html)) + PLAYER_JS + pages.SHARE_JS

    work = {"@type": "Audiobook", "@id": url + "#audiobook", "name": b["title"], "url": url, "description": desc,
            "inLanguage": b.get("lang"), "duration": _iso(b.get("secs")), "isAccessibleForFree": True,
            "bookFormat": "https://schema.org/AudiobookFormat", "genre": GENRE.get(b.get("genre"), GENRE["nov"])[ui],
            "image": b.get("cover") or thumb_url(b), "publisher": {"@type": "Organization", "name": "LibriVox", "url": "https://librivox.org/"},
            "license": "https://creativecommons.org/publicdomain/mark/1.0/", "sameAs": b.get("librivox") or (ARCHIVE + "/details/" + b["ia"]),
            "potentialAction": {"@type": "ListenAction", "target": url + "#player"}}
    if b.get("title_ar") and b["title_ar"] != b["title"]:
        work["alternateName"] = b["title_ar"]
    if b.get("author"):
        work["author"] = {"@type": "Person", "name": b["author"]}
    if b.get("readers"):
        work["readBy"] = [{"@type": "Person", "name": r} for r in b["readers"][:10]]
    if b.get("translator"):
        work["translator"] = {"@type": "Person", "name": b["translator"]}
    ld = seo._ld({"@context": "https://schema.org", "@graph": [
        {"@type": "ItemPage", "@id": url, "url": url, "name": page_title, "inLanguage": ui, "isPartOf": {"@id": base + "/#site"},
         "mainEntity": {"@id": url + "#audiobook"}}, work,
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t["home"], "item": base + "/"},
            {"@type": "ListItem", "position": 2, "name": s["name"], "item": base + "/audiobooks"},
            {"@type": "ListItem", "position": 3, "name": name, "item": url}]}]})
    return seo.with_nonce(seo._shell(ui, base, path(b), page_title, desc, body, ld, nonce=nonce, extra_css=AB_CSS, canonical=url,
                                     alternates=False, ads=ads), nonce)


def home_strip(ui: str, n_show: int = 12) -> str:
    """The home page's banner above "most viewed": the newest audiobooks and the way to all of them."""
    items = books()
    if not items:
        return ""
    s, q = S[ui], lang_q(ui)
    row = "".join(
        '<a class="abs-it" href="%s%s"><span class="abs-cv"><img src="%s" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">'
        '</span><b%s>%s</b><small>%s</small></a>'
        % (esc(path(b)), q, esc(thumb_url(b)), ' lang="ar"' if b.get("lang") == "ar" and ui != "ar" else "", esc(title(b, ui)),
           esc(duration(b.get("secs"), ui))) for b in items[:n_show])
    return ('<section class="abs-sec" id="audio" aria-labelledby="absH"><div class="wrap"><div class="abs-band">'
            '<div class="abs-head"><div class="abs-top"><span class="abs-new">%s</span><span class="abs-wave" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span></div>'
            '<h2 id="absH">%s</h2><p>%s</p><a class="abs-cta" href="/audiobooks%s">%s <span aria-hidden="true">%s</span></a></div>'
            '<div class="abs-row">%s</div></div></div></section>'
            % (esc(s["strip_tag"]), esc(s["strip_h"]), esc(s["strip_p"].format(n=len(items))), q, esc(s["strip_all"]),
               "←" if T[ui]["dir"] == "rtl" else "→", row))


def main_urls(base: str) -> list:
    """The audiobook pages for the sitemap: the list in every interface language, each book at its own address."""
    if not books():
        return []
    return [base + "/audiobooks" + lang_q(ui) for ui in UI_LANGS] + [base + path(b) for b in books()]


def meta_count() -> int:
    return len(_data().get("books", []))
