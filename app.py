import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import textwrap

def render_html(html_str):
    if hasattr(st, "html"):
        st.html(html_str)
    else:
        st.markdown(textwrap.dedent(html_str).strip(), unsafe_allow_html=True)

# 페이지 기본 설정
st.set_page_config(
    page_title="Brothers Capital (브라더스 캐피탈) — 올인원 자산 대시보드",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (세련된 뮤트 톤 로즈 레드 / 로열 블루 팔레트 & 모바일 최적화)
st.markdown("""
<style>
    /* 데스크톱 & 공통 스타일 */
    .macro-ticker-scroll {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        gap: 8px;
        padding: 4px 2px 8px 2px;
        margin-bottom: 6px;
        scrollbar-width: thin;
    }
    .macro-ticker-scroll::-webkit-scrollbar {
        height: 4px;
    }
    .macro-ticker-scroll::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 4px;
    }
    .macro-ticker-item {
        flex: 0 0 auto;
        min-width: 110px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px 10px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .macro-title {
        font-size: 0.76rem;
        color: #64748b;
        margin-bottom: 2px;
        font-weight: 500;
        white-space: nowrap;
    }
    .macro-val {
        font-size: 1.0rem;
        font-weight: 700;
        color: #0f172a;
    }
    .macro-chg-up {
        font-size: 0.78rem;
        color: #e11d48;
        font-weight: 700;
        background: #ffe4e6;
        padding: 1px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 2px;
    }
    .macro-chg-down {
        font-size: 0.78rem;
        color: #2563eb;
        font-weight: 700;
        background: #dbeafe;
        padding: 1px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 2px;
    }
    .mobile-stock-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.1s ease;
    }
    .mobile-stock-card:hover {
        border-color: #cbd5e1;
    }
    .macro-4card-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 12px;
    }
    .card-buy {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    .card-sell {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    .card-hold {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    .card-belief {
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    .card-empty {
        background: #f8fafc;
        color: #64748b;
        padding: 10px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px dashed #cbd5e1;
        font-size: 0.88rem;
    }
    .theme-header {
        background: #f8fafc;
        padding: 10px 14px;
        border-radius: 8px;
        border-left: 4px solid #2563eb;
        margin-bottom: 10px;
    }
    .guide-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 0.84rem;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    /* 📱 모바일 최적화 미디어 쿼리 (화면 너비 768px 이하) */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.0rem !important;
            padding-bottom: 2.0rem !important;
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
        }
        h1 {
            font-size: 1.35rem !important;
            line-height: 1.25 !important;
            margin-bottom: 0.2rem !important;
        }
        h2 {
            font-size: 1.15rem !important;
        }
        h3 {
            font-size: 1.05rem !important;
        }
        h4 {
            font-size: 0.95rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            padding-bottom: 4px !important;
            gap: 2px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px !important;
            font-size: 0.80rem !important;
            white-space: nowrap !important;
        }
        .macro-4card-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 6px !important;
        }
        .macro-ticker-item {
            min-width: 95px !important;
            padding: 5px 8px !important;
        }
        .macro-val {
            font-size: 0.92rem !important;
        }
        .card-buy, .card-sell, .card-hold {
            padding: 10px 12px !important;
        }
        .card-buy h4, .card-sell h4, .card-hold h4 {
            font-size: 0.92rem !important;
        }
        .card-empty {
            padding: 8px 10px !important;
            font-size: 0.8rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===== 데이터 디렉토리 및 영구 저장 파일 경로 =====
DATA_DIR = Path(__file__).parent / "user_data"
DATA_DIR.mkdir(exist_ok=True)
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
CUSTOM_THEMES_FILE = DATA_DIR / "custom_themes.json"

# ===== 티커 - 한글명 - 영문명 종합 사전 =====
STOCK_META = {
    "GOOGL": {"kr": "구글 (알파벳)", "en": "Alphabet"},
    "AMZN":  {"kr": "아마존", "en": "Amazon"},
    "DE":    {"kr": "존 디어 (농기계)", "en": "Deere & Co"},
    "BRK-B": {"kr": "버크셔 해서웨이", "en": "Berkshire Hathaway"},
    "NVO":   {"kr": "노보 노디스크 (비만치료)", "en": "Novo Nordisk"},
    "RKLB":  {"kr": "로켓 랩 (우주발사체)", "en": "Rocket Lab"},
    "TXG":   {"kr": "10x 지노믹스 (유전자)", "en": "10x Genomics"},
    "MSFT":  {"kr": "마이크로소프트", "en": "Microsoft"},
    "NVDA":  {"kr": "엔비디아 (AI반도체)", "en": "NVIDIA"},
    "DRAM":  {"kr": "라운드힐 메모리 반도체 (DRAM)", "en": "Roundhill Memory ETF"},
    "VYLR":  {"kr": "바이러 (VYLR)", "en": "Vylor Inc."},
    "LLY":   {"kr": "일라이 릴리 (비만치료)", "en": "Eli Lilly"},
    "AAPL":  {"kr": "애플", "en": "Apple"},
    "META":  {"kr": "메타 (페이스북)", "en": "Meta Platforms"},
    "TSLA":  {"kr": "테슬라 (전기차/AI)", "en": "Tesla"},
    "TSM":   {"kr": "TSMC (반도체파운드리)", "en": "Taiwan Semiconductor"},
    "AVGO":  {"kr": "브로드컴 (통신반도체)", "en": "Broadcom"},
    "AMD":   {"kr": "AMD (AI칩)", "en": "Advanced Micro Devices"},
    "ASML":  {"kr": "ASML (노광장비)", "en": "ASML Holding"},
    "AMAT":  {"kr": "어플라이드 머티어리얼즈", "en": "Applied Materials"},
    "MU":    {"kr": "마이크론 (HBM메모리)", "en": "Micron Technology"},
    "VRT":   {"kr": "버티브 (데이터센터냉각)", "en": "Vertiv Holdings"},
    "CEG":   {"kr": "컨스텔레이션 에너지 (원전)", "en": "Constellation Energy"},
    "GEV":   {"kr": "GE 버노바 (전력망)", "en": "GE Vernova"},
    "ETN":   {"kr": "이튼 (전력인프라)", "en": "Eaton Corp"},
    "PWR":   {"kr": "콴타 서비스 (송배전)", "en": "Quanta Services"},
    "CCJ":   {"kr": "카메코 (우라늄1위)", "en": "Cameco"},
    "OKLO":  {"kr": "오클로 (소형원전 SMR)", "en": "Oklo Inc"},
    "SMR":   {"kr": "뉴스케일 파워 (SMR)", "en": "NuScale Power"},
    "NNE":   {"kr": "나노 뉴클리어 에너지", "en": "Nano Nuclear Energy"},
    "VST":   {"kr": "비스트라 (민간발전)", "en": "Vistra Corp"},
    "ASTS":  {"kr": "AST 스페이스모바일 (위성)", "en": "AST SpaceMobile"},
    "LUNR":  {"kr": "인튜이티브 머신스 (달탐사)", "en": "Intuitive Machines"},
    "KTOS":  {"kr": "크라토스 (군용드론)", "en": "Kratos Defense"},
    "PLTR":  {"kr": "팔란티어 (AI데이터)", "en": "Palantir Technologies"},
    "IONQ":  {"kr": "아이온큐 (양자컴)", "en": "IonQ"},
    "RGTI":  {"kr": "리게티 컴퓨팅 (양자컴)", "en": "Rigetti Computing"},
    "QBTS":  {"kr": "디웨이브 (양자컴퓨팅)", "en": "D-Wave Quantum"},
    "QUBT":  {"kr": "퀀텀 컴퓨팅 (양자)", "en": "Quantum Computing Inc"},
    "UBER":  {"kr": "우버 (모빌리티)", "en": "Uber Technologies"},
    "RIVN":  {"kr": "리비안 (전기차)", "en": "Rivian Automotive"},
    "ISRG":  {"kr": "인튜이티브 서지컬 (수술로봇)", "en": "Intuitive Surgical"},
    "SYM":   {"kr": "심보틱 (AI물류로봇)", "en": "Symbotic"},
    "PATH":  {"kr": "유아이패스 (업무자동화)", "en": "UiPath"},
    "VKTX":  {"kr": "바이킹 테라퓨틱스 (비만)", "en": "Viking Therapeutics"},
    "AMGN":  {"kr": "암젠 (바이오대형)", "en": "Amgen"},
    "VRTX":  {"kr": "버텍스 (난치병신약)", "en": "Vertex Pharmaceuticals"},
    "CRSP":  {"kr": "크리스퍼 테라퓨틱스 (유전자)", "en": "CRISPR Therapeutics"},
    "BEAM":  {"kr": "빔 테라퓨틱스 (염기교정)", "en": "Beam Therapeutics"},
    "NTLA":  {"kr": "인텔리아 (유전자가위)", "en": "Intellia Therapeutics"},
    "MSTR":  {"kr": "마이크로스트래티지 (비트코인)", "en": "MicroStrategy"},
    "COIN":  {"kr": "코인베이스 (크립토거래소)", "en": "Coinbase Global"},
    "CLSK":  {"kr": "클린스파크 (채굴)", "en": "CleanSpark"},
    "MARA":  {"kr": "마라 홀딩스 (비트코인채굴)", "en": "MARA Holdings"},
    "IREN":  {"kr": "아이리스 에너지 (채굴/AI)", "en": "Iris Energy"},
    "V":     {"kr": "비자 (글로벌결제)", "en": "Visa"},
    "MA":    {"kr": "마스터카드 (글로벌결제)", "en": "Mastercard"},
    "PYPL":  {"kr": "페이팔 (전자결제)", "en": "PayPal"},
    "HOOD":  {"kr": "로빈후드 (온라인증권)", "en": "Robinhood Markets"},
    "CRWD":  {"kr": "크라우드스트라이크 (보안)", "en": "CrowdStrike"},
    "PANW":  {"kr": "팔로알토 네트웍스 (보안)", "en": "Palo Alto Networks"},
    "FTNT":  {"kr": "포티넷 (네트워크보안)", "en": "Fortinet"},
    "NET":   {"kr": "클라우드플레어 (CDN/보안)", "en": "Cloudflare"},
    "ZS":    {"kr": "지스케일러 (클라우드보안)", "en": "Zscaler"},
    "CRM":   {"kr": "세일즈포스 (CRM클라우드)", "en": "Salesforce"},
    "NOW":   {"kr": "서비스나우 (엔터프라이즈)", "en": "ServiceNow"},
    "SNOW":  {"kr": "스노우플레이크 (데이터클라우드)", "en": "Snowflake"},
    "ADBE":  {"kr": "어도비 (창작소프트웨어)", "en": "Adobe"},
    "LMT":   {"kr": "록히드 마틴 (방산1위)", "en": "Lockheed Martin"},
    "RTX":   {"kr": "RTX (레이시온 방산)", "en": "RTX Corp"},
    "NOC":   {"kr": "노스롭 그루먼 (스텔스방산)", "en": "Northrop Grumman"},
    "GD":    {"kr": "제너럴 다이내믹스 (방산/잠수함)", "en": "General Dynamics"},
    "BA":    {"kr": "보잉 (항공우주)", "en": "Boeing"},
    "NEM":   {"kr": "뉴몬트 (글로벌금채굴1위)", "en": "Newmont"},
    "GOLD":  {"kr": "배릭 골드 (금채굴)", "en": "Barrick Gold"},
    "AEM":   {"kr": "애그니코 이글 (금채굴)", "en": "Agnico Eagle Mines"},
    "AG":    {"kr": "퍼스트 마제스틱 (은채굴)", "en": "First Majestic Silver"},
    "PAAS":  {"kr": "팬 아메리칸 실버 (은채굴)", "en": "Pan American Silver"},
    "XOM":   {"kr": "엑손 모빌 (석유에너지1위)", "en": "Exxon Mobil"},
    "CVX":   {"kr": "셰브론 (석유에너지)", "en": "Chevron"},
    "OXY":   {"kr": "옥시덴탈 (버핏투자 석유)", "en": "Occidental Petroleum"},
    "SLB":   {"kr": "SLB (유전서비스)", "en": "Schlumberger"},
    "COP":   {"kr": "코노코필립스 (원유탐사)", "en": "ConocoPhillips"},
    "ZIM":   {"kr": "ZIM 종합 해운", "en": "ZIM Integrated Shipping"},
    "MATX":  {"kr": "맷슨 (해운물류)", "en": "Matson"},
    "FDX":   {"kr": "페덱스 (글로벌물류)", "en": "FedEx"},
    "UPS":   {"kr": "UPS (화물특송)", "en": "United Parcel Service"},
    "JPM":   {"kr": "JP모건 체이스 (월가1위은행)", "en": "JPMorgan Chase"},
    "GS":    {"kr": "골드만 삭스 (투자은행)", "en": "Goldman Sachs"},
    "MS":    {"kr": "모건 스탠리 (자산관리)", "en": "Morgan Stanley"},
    "BAC":   {"kr": "뱅크오브아메리카 (대형은행)", "en": "Bank of America"},
    "BLK":   {"kr": "블랙록 (세계최대자산운용)", "en": "BlackRock"},
    "O":     {"kr": "리얼티 인컴 (월배당리츠)", "en": "Realty Income"},
    "SCHD":  {"kr": "SCHD (슈드 배당성장ETF)", "en": "Schwab US Dividend ETF"},
    "PG":    {"kr": "P&G (소비재 배당귀족)", "en": "Procter & Gamble"},
    "KO":    {"kr": "코카콜라 (배당킹)", "en": "Coca-Cola"},
    "JNJ":   {"kr": "존슨앤드존슨 (헬스케어배당)", "en": "Johnson & Johnson"},
    "ABBV":  {"kr": "애브비 (고배당바이오)", "en": "AbbVie"},
    "CAT":   {"kr": "캐터필러 (중장비/인프라)", "en": "Caterpillar"},
    "SPY":   {"kr": "S&P 500 지수 ETF", "en": "SPDR S&P 500 ETF"},
    "QQQ":   {"kr": "나스닥 100 지수 ETF", "en": "Invesco QQQ"}
}

def get_stock_label(ticker):
    """티커를 받아서 '한글이름 (영문명 / TICKER)' 형태로 직관적인 라벨 반환"""
    meta = STOCK_META.get(ticker)
    if meta:
        return f"{meta['kr']} ({meta['en']} / {ticker})"
    return ticker

def get_stock_short_label(ticker):
    """표나 카드용 간결한 라벨 '한글명 (TICKER)'"""
    meta = STOCK_META.get(ticker)
    if meta:
        return f"{meta['kr']} ({ticker})"
    return ticker

def resolve_ticker_input(query):
    """한글, 영문, 티커 입력을 실제 티커로 자동 변환"""
    q = query.strip().upper()
    if q in STOCK_META:
        return q
    # 한글 검색 또는 영문 검색 매칭
    for t, m in STOCK_META.items():
        if query.strip().lower() in m['kr'].lower() or query.strip().lower() in m['en'].lower():
            return t
    return q

# ===== 20대 기본 테마 정의 =====
DEFAULT_THEMES = {
    "🤖 AI 가속기 & 반도체": {
        "cat": "IT/테크", "desc": "인공지능 GPU, 파운드리, HBM 메모리 대장주",
        "symbols": ["NVDA", "TSM", "AVGO", "AMD", "ASML", "AMAT", "MU"]
    },
    "⚡ 데이터센터 전력 & 냉각": {
        "cat": "에너지/인프라", "desc": "AI 전력 소모 폭증, 액체 냉각 및 전력망 인프라",
        "symbols": ["VRT", "CEG", "GEV", "ETN", "PWR"]
    },
    "⚛️ 원자력 & SMR (차세대 전력)": {
        "cat": "에너지/인프라", "desc": "빅테크 데이터센터 전력 계약 및 소형 모듈 원자로",
        "symbols": ["CCJ", "OKLO", "SMR", "NNE", "VST"]
    },
    "🚀 우주항공 & 위성 통신": {
        "cat": "우주/방산", "desc": "로켓 발사체, 저궤도 위성, 우주 탐사",
        "symbols": ["RKLB", "ASTS", "LUNR", "KTOS", "PLTR"]
    },
    "🔬 양자컴퓨터 (Quantum)": {
        "cat": "미래기술", "desc": "차세대 퀀텀 컴퓨팅 알고리즘 및 하드웨어",
        "symbols": ["IONQ", "RGTI", "QBTS", "QUBT"]
    },
    "🚗 자율주행 & 로보택시": {
        "cat": "미래기술", "desc": "FSD, 비전 AI, 미래형 모빌리티 플랫폼",
        "symbols": ["TSLA", "GOOGL", "UBER", "RIVN"]
    },
    "🦾 휴머노이드 & 피지컬 로봇": {
        "cat": "미래기술", "desc": "인공지능 로봇, 산업 자동화, 의료용 수술 로봇",
        "symbols": ["TSLA", "ISRG", "SYM", "PATH"]
    },
    "🧬 비만치료제 (GLP-1)": {
        "cat": "바이오/헬스", "desc": "글로벌 비만/당뇨 치료제 신드롬 대장주",
        "symbols": ["LLY", "NVO", "VKTX", "AMGN"]
    },
    "✂️ 유전자 가위 & 세포치료": {
        "cat": "바이오/헬스", "desc": "CRISPR 유전자 교정 및 혁신 항암제",
        "symbols": ["CRSP", "BEAM", "NTLA", "TXG", "VRTX"]
    },
    "🪙 비트코인 & 크립토 채굴": {
        "cat": "금융/크립토", "desc": "비트코인 보유 기업 및 채굴/거래소 인프라",
        "symbols": ["MSTR", "COIN", "CLSK", "MARA", "IREN"]
    },
    "💳 핀테크 & 글로벌 결제망": {
        "cat": "금융/크립토", "desc": "글로벌 신용카드 네트워크 및 온라인 핀테크",
        "symbols": ["V", "MA", "PYPL", "HOOD"]
    },
    "🔒 사이버보안 (Cybersecurity)": {
        "cat": "IT/테크", "desc": "클라우드 보안 및 차세대 AI 보안 플랫폼",
        "symbols": ["CRWD", "PANW", "FTNT", "NET", "ZS"]
    },
    "☁️ 엔터프라이즈 SaaS & 클라우드": {
        "cat": "IT/테크", "desc": "기업용 B2B 소프트웨어 및 생산성 클라우드",
        "symbols": ["MSFT", "CRM", "NOW", "PLTR", "SNOW", "ADBE"]
    },
    "🛡️ 글로벌 방위산업 & 드론": {
        "cat": "우주/방산", "desc": "지정학적 리스크 수혜 차세대 안보 및 미사일/드론",
        "symbols": ["LMT", "RTX", "NOC", "GD", "BA"]
    },
    "⛏️ 금 & 은 채굴 (귀금속)": {
        "cat": "원자재/에너지", "desc": "글로벌 화폐가치 하락 및 안전자산 수혜 채굴주",
        "symbols": ["NEM", "GOLD", "AEM", "AG", "PAAS"]
    },
    "🛢️ 오일 & 천연가스 메이저": {
        "cat": "원자재/에너지", "desc": "전통 화석연료 배당 및 에너지 대기업",
        "symbols": ["XOM", "CVX", "OXY", "SLB", "COP"]
    },
    "🚢 해운 & 물류 공급망": {
        "cat": "산업/물류", "desc": "해상 운임 및 글로벌 물류 공급망 핵심주",
        "symbols": ["ZIM", "MATX", "FDX", "UPS"]
    },
    "🏦 월가 대형 투자은행": {
        "cat": "금융/크립토", "desc": "자산관리 및 금리인하기 수혜 월가 대장주",
        "symbols": ["JPM", "GS", "MS", "BAC", "BLK"]
    },
    "🏢 고배당 배당귀족 & 리츠": {
        "cat": "배당/가치", "desc": "월배당 부동산 리츠 및 50년 연속 배당성장주",
        "symbols": ["O", "SCHD", "PG", "KO", "JNJ", "ABBV"]
    },
    "☁️ 빅테크 메가캡 (M7)": {
        "cat": "IT/테크", "desc": "독점적 현금흐름의 글로벌 시가총액 최상위주",
        "symbols": ["AAPL", "MSFT", "AMZN", "META", "GOOGL"]
    }
}

PRESETS = {
    "Dr_Rotation_Basket v1.3 실전 바스켓 (기본)": [
        {"symbol": "GOOGL", "use": True,  "qty": 30.0,  "avg": 349.77, "belief": True},
        {"symbol": "AMZN",  "use": True,  "qty": 30.0,  "avg": 254.99, "belief": False},
        {"symbol": "DE",    "use": True,  "qty": 25.0,  "avg": 628.75, "belief": False},
        {"symbol": "BRK-B", "use": True,  "qty": 7.0,   "avg": 506.50, "belief": True},
        {"symbol": "NVO",   "use": True,  "qty": 20.0,  "avg": 43.68,  "belief": True},
        {"symbol": "RKLB",  "use": True,  "qty": 255.0, "avg": 82.19,  "belief": True},
        {"symbol": "DRAM",  "use": True,  "qty": 180.0, "avg": 52.00,  "belief": False},
        {"symbol": "VYLR",  "use": True,  "qty": 150.0, "avg": 73.03,  "belief": True},
        {"symbol": "TXG",   "use": False, "qty": 0.0,   "avg": 0.0,    "belief": False},
        {"symbol": "LLY",   "use": False, "qty": 0.0,   "avg": 0.0,    "belief": False},
        {"symbol": "NVDA",  "use": False, "qty": 0.0,   "avg": 0.0,    "belief": False},
    ],
    "매그니피센트 7 (빅테크)": [
        {"symbol": "NVDA", "use": True, "qty": 0.0, "avg": 0.0, "belief": False},
        {"symbol": "MSFT", "use": True, "qty": 0.0, "avg": 0.0, "belief": False},
        {"symbol": "AAPL", "use": True, "qty": 0.0, "avg": 0.0, "belief": False},
        {"symbol": "GOOGL","use": True, "qty": 0.0, "avg": 0.0, "belief": False},
        {"symbol": "AMZN", "use": True, "qty": 0.0, "avg": 0.0, "belief": False},
        {"symbol": "META", "use": True, "qty": 0.0, "avg": 0.0, "belief": False},
        {"symbol": "TSLA", "use": True, "qty": 0.0, "avg": 0.0, "belief": False},
    ],
    "미국 대표 배당 성장주": [
        {"symbol": "SCHD", "use": True, "qty": 0.0, "avg": 0.0, "belief": True},
        {"symbol": "JNJ",  "use": True, "qty": 0.0, "avg": 0.0, "belief": True},
        {"symbol": "PG",   "use": True, "qty": 0.0, "avg": 0.0, "belief": True},
        {"symbol": "KO",   "use": True, "qty": 0.0, "avg": 0.0, "belief": True},
        {"symbol": "PEP",  "use": True, "qty": 0.0, "avg": 0.0, "belief": True},
        {"symbol": "ABBV", "use": True, "qty": 0.0, "avg": 0.0, "belief": True},
    ]
}

DEFAULT_SETTINGS = {
    "max_pos": 4, "start_year": 2006, "oos_year": 2020, "cost_pct": 0.10, "cash_yield": 0.0,
    "sma_len": 200, "slope_len": 20, "break_pct": 3.0, "support_pct": 3.0,
    "use_a": True, "use_b": True, "use_c": True, "use_deep": True, "deep_pct": 1.0, "use_vol_filt": True,
    "rank_mode": "6개월 모멘텀", "acct_usd": 0.0
}

# ===== 파일 영구 저장 / 로딩 헬퍼 =====
def load_saved_basket():
    if PORTFOLIO_FILE.exists():
        try:
            with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if "belief" not in item:
                        item["belief"] = item.get("symbol") in ["GOOGL", "BRK-B", "NVO", "RKLB", "VYLR"]
                return data
        except Exception:
            pass
    return PRESETS["Dr_Rotation_Basket v1.3 실전 바스켓 (기본)"]

def save_basket_to_disk(basket):
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(basket, f, ensure_ascii=False, indent=2)

def load_saved_settings():
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                res = dict(DEFAULT_SETTINGS)
                res.update(saved)
                return res
        except Exception:
            pass
    return DEFAULT_SETTINGS

def save_settings_to_disk(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def load_all_themes():
    themes = dict(DEFAULT_THEMES)
    if CUSTOM_THEMES_FILE.exists():
        try:
            with open(CUSTOM_THEMES_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
                themes.update(custom)
        except Exception:
            pass
    return themes

def save_custom_theme_to_disk(name, info):
    custom = {}
    if CUSTOM_THEMES_FILE.exists():
        try:
            with open(CUSTOM_THEMES_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
        except Exception:
            pass
    custom[name] = info
    with open(CUSTOM_THEMES_FILE, "w", encoding="utf-8") as f:
        json.dump(custom, f, ensure_ascii=False, indent=2)

# 세션 상태 초기화
if "basket" not in st.session_state:
    st.session_state.basket = load_saved_basket()
if "settings" not in st.session_state:
    st.session_state.settings = load_saved_settings()
if "themes" not in st.session_state:
    st.session_state.themes = load_all_themes()

# ===== 데이터 다운로드 캐싱 =====
@st.cache_data(ttl=3600*2)
def fetch_stock_data(tickers, start_date):
    fetch_start = (pd.to_datetime(start_date) - pd.Timedelta(days=500)).strftime('%Y-%m-%d')
    all_tickers = list(set(tickers + ["SPY"]))
    data = yf.download(all_tickers, start=fetch_start, progress=False, group_by='ticker', auto_adjust=True)
    return data

@st.cache_data(ttl=600)
def fetch_macro_data():
    macro_map = {
        "원/달러 환율": "KRW=X",
        "코스피 (KOSPI)": "^KS11",
        "S&P 500": "^GSPC",
        "나스닥 100": "QQQ",
        "금 (Gold)": "GC=F",
        "비트코인": "BTC-USD",
        "미국 10년물 국채": "^TNX",
        "WTI 원유": "CL=F"
    }
    df = yf.download(list(macro_map.values()), period="5d", progress=False, group_by='ticker', auto_adjust=True)
    res = {}
    for label, t in macro_map.items():
        try:
            if t in df.columns.levels[0]:
                sub = df[t].dropna(subset=['Close'])
                if len(sub) >= 2:
                    curr = sub['Close'].iloc[-1]
                    prev = sub['Close'].iloc[-2]
                    res[label] = {"val": curr, "chg": (curr / prev - 1.0) * 100.0, "ticker": t}
        except Exception:
            pass
    return res

@st.cache_data(ttl=1800)
def fetch_all_themes_data(theme_dict):
    all_tickers = []
    for info in theme_dict.values():
        all_tickers.extend(info['symbols'])
    all_tickers = list(set(all_tickers))
    df = yf.download(all_tickers, period="3mo", progress=False, group_by='ticker', auto_adjust=True)
    return df

def calc_indicators(df, cfg):
    c = df['Close']; o = df['Open']; h = df['High']; l = df['Low']; v = df['Volume']
    sma200 = c.rolling(cfg['sma_len']).mean()
    rising = sma200 > sma200.shift(cfg['slope_len'])
    regime = (c >= sma200) & rising
    brk = sma200 * (1.0 - cfg['break_pct'] / 100.0)
    broken = (c < brk) & (c.shift(1) < brk.shift(1))
    
    e20 = c.ewm(span=20, adjust=False).mean()
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    hist_up = hist > hist.shift(1)
    gold = (macd > signal) & (macd.shift(1) <= signal.shift(1))
    deep = (macd < 0) & (macd.rolling(10).min() / c * 100.0 <= -1.0)
    vol_ok = v >= v.rolling(20).mean() * 0.8
    
    tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    body = (c - o).abs()
    low_tail = np.minimum(o, c) - l
    hammer = (low_tail >= 1.8 * body) & ((h - l) > atr * 0.3)
    engulf = (c.shift(1) < o.shift(1)) & (c > o) & (c >= o.shift(1)) & (o <= c.shift(1))
    
    sigA = cfg['use_a'] & (l <= sma200 * (1.0 + cfg['support_pct'] / 100.0)) & (hammer | engulf) & hist_up
    sigB = cfg['use_b'] & (l <= e20 * 1.015) & (c >= e20 * 0.99) & (c > o) & hist_up
    sigC = cfg['use_c'] & gold & deep & vol_ok
    
    sig = pd.Series(0, index=df.index)
    rank_mode = cfg.get('rank_mode', "6개월 모멘텀")
    if rank_mode == "12-1개월 모멘텀":
        mom = c.shift(21) / c.shift(252) - 1.0 if len(c) > 252 else (c / c.shift(126) - 1.0 if len(c) > 126 else pd.Series(np.nan, index=df.index))
    else:
        mom = c / c.shift(126) - 1.0 if len(c) > 126 else pd.Series(np.nan, index=df.index)
    
    reg_code = pd.Series(np.nan, index=df.index)
    reg_code[regime] = 2; reg_code[~regime & (c >= sma200)] = 1
    reg_code[~regime & (c < sma200) & rising] = 0; reg_code[~regime & (c < sma200) & ~rising] = -1
    
    return pd.DataFrame({
        'Open': o, 'High': h, 'Low': l, 'Close': c, 'Volume': v,
        'SMA200': sma200, 'E20': e20, 'Brk': brk, 'Broken': broken,
        'Regime': regime, 'RegCode': reg_code, 'Sig': sig, 'Mom': mom, 'ATR': atr
    }, index=df.index)

# ===== 상단 1: 매크로 전광판 (모바일 가로 스와이프 지원!) =====
macro_data = fetch_macro_data()
if macro_data:
    chips_html = []
    for label, item in macro_data.items():
        val = item['val']; chg = item['chg']
        chg_cls = "macro-chg-up" if chg >= 0 else "macro-chg-down"
        chg_sign = "+" if chg >= 0 else ""
        if "원/달러" in label:
            fmt_val = f"₩{val:,.1f}"
        elif "코스피" in label:
            fmt_val = f"{val:,.1f}p"
        elif "국채" in label:
            fmt_val = f"{val:.2f}%"
        elif "비트코인" in label:
            fmt_val = f"${val:,.0f}"
        else:
            fmt_val = f"${val:,.2f}"
            
        short_lbl = label.replace(" (KOSPI)", "").replace(" (Gold)", "")
        chips_html.append(f'<div class="macro-ticker-item"><div class="macro-title">{short_lbl}</div><div class="macro-val">{fmt_val}</div><div class="{chg_cls}">{chg_sign}{chg:.2f}%</div></div>')
    
    full_macro_html = f"""
    <div style="margin-bottom: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 0.82rem; font-weight: 700; color: #475569;">🌐 글로벌 매크로 실시간 전광판</span>
            <span style="font-size: 0.72rem; color: #94a3b8;">👉 좌우로 스와이프</span>
        </div>
        <div class="macro-ticker-scroll">
            {''.join(chips_html)}
        </div>
    </div>
    """
    render_html(full_macro_html)

# ===== 데이터 로드 및 최신 상태 도출 =====
cfg = st.session_state.settings
active_tickers = [item['symbol'] for item in st.session_state.basket if item.get('use', True)]
raw_data = fetch_stock_data(active_tickers, f"{cfg['start_year']}-01-01")

ind_dict = {}
for sym in active_tickers:
    if sym in raw_data.columns.levels[0]:
        df_sym = raw_data[sym].dropna(subset=['Close'])
        if len(df_sym) >= 5:
            ind_dict[sym] = calc_indicators(df_sym, cfg)

spy_df = raw_data['SPY'].dropna(subset=['Close']) if 'SPY' in raw_data.columns.levels[0] else None
sim_start = pd.to_datetime(f"{cfg['start_year']}-01-01")
common_idx = spy_df.loc[spy_df.index >= sim_start].index if spy_df is not None else pd.date_index()

# 1. v1.3 실전자산 슬롯 & 보유 집계 (신념 보유 vs 시스템 스윙 구분)
my_held = 0  # 시스템 보유 (신념 제외)
my_sell = 0  # 시스템 보유 중 붕괴 이탈
my_bel = 0   # 신념 보유

for item in st.session_state.basket:
    if item.get('use', True) and item.get('qty', 0.0) > 0:
        sym = item['symbol']
        is_broken = False
        if sym in ind_dict and not ind_dict[sym].empty:
            b_val = ind_dict[sym]['Broken'].iloc[-1]
            is_broken = bool(b_val) if not pd.isna(b_val) else False
        if item.get('belief', False):
            my_bel += 1
        else:
            my_held += 1
            if is_broken:
                my_sell += 1

my_free = max(0, cfg['max_pos'] - my_held + my_sell)

# 2. 모멘텀 순위 매김 (유효한 모멘텀 기준)
m_ranks = {}
all_moms = {}
for item in st.session_state.basket:
    sym = item['symbol']
    if item.get('use', True) and sym in ind_dict and not ind_dict[sym].empty:
        val = ind_dict[sym]['Mom'].iloc[-1]
        if not pd.isna(val):
            all_moms[sym] = val
sorted_moms = sorted(all_moms.items(), key=lambda x: x[1], reverse=True)
for r_idx, (s, _) in enumerate(sorted_moms, start=1):
    m_ranks[s] = r_idx

# 3. 빈 슬롯에 들어갈 매수 후보 선정 (강세 + 신호 + 미보유 -> 모멘텀 상위 순)
picked_syms = set()
slots_left = my_free
cand_list = []
for item in st.session_state.basket:
    sym = item['symbol']
    if item.get('use', True) and item.get('qty', 0.0) <= 0 and sym in ind_dict and not ind_dict[sym].empty:
        lr = ind_dict[sym].iloc[-1]
        rc = lr['RegCode']; sig = lr['Sig']
        if rc == 2 and sig > 0:
            mm = lr['Mom'] if not pd.isna(lr['Mom']) else -9.0
            cand_list.append((sym, mm))
cand_list.sort(key=lambda x: x[1], reverse=True)
for s, _ in cand_list[:slots_left]:
    picked_syms.add(s)

# 4. 종목별 상태 및 v1.3 행동 도출
latest_status = []
for item in st.session_state.basket:
    sym = item['symbol']
    use = item.get('use', True)
    qty = item.get('qty', 0.0)
    avg = item.get('avg', 0.0)
    belief = item.get('belief', False)
    
    if not use:
        latest_status.append({
            'Symbol': sym, 'Close': np.nan, 'RegCode': np.nan, 'Sig': 0, 'Broken': False,
            'Brk': np.nan, 'DistBrk': np.nan, 'Mom': np.nan, 'MomRank': "-", 'Qty': qty, 'Avg': avg,
            'PnL_pct': np.nan, 'Belief': belief, 'Action': "제외", 'StatusType': "EXCLUDE",
            'Date': "-"
        })
        continue
        
    if sym not in ind_dict or ind_dict[sym].empty:
        latest_status.append({
            'Symbol': sym, 'Close': np.nan, 'RegCode': np.nan, 'Sig': 0, 'Broken': False,
            'Brk': np.nan, 'DistBrk': np.nan, 'Mom': np.nan, 'MomRank': "-", 'Qty': qty, 'Avg': avg,
            'PnL_pct': np.nan, 'Belief': belief, 'Action': "❔ 데이터 로드 중", 'StatusType': "PENDING",
            'Date': "-"
        })
        continue
        
    df_sym = ind_dict[sym]
    last_row = df_sym.iloc[-1]
    c = last_row['Close']
    rc = last_row['RegCode']
    sig = last_row['Sig']
    brk = last_row['Brk']
    broken = bool(last_row['Broken']) if not pd.isna(last_row['Broken']) else False
    mom = last_row['Mom']
    dist_brk = (brk / c - 1.0) * 100.0 if (not pd.isna(brk) and not pd.isna(c) and c > 0) else np.nan
    pnl_pct = (c / avg - 1.0) * 100.0 if (qty > 0 and avg > 0 and not pd.isna(c)) else np.nan
    mom_rank_str = str(m_ranks.get(sym, "-"))
    
    acct_usd = cfg.get('acct_usd', 0.0)
    shares_txt = ""
    if acct_usd > 0 and not pd.isna(c) and c > 0:
        calc_q = int((acct_usd / cfg['max_pos']) // c)
        if calc_q > 0:
            shares_txt = f" · 약 {calc_q:,}주"
            
    # v1.3 Action Logic
    if pd.isna(rc):
        act = "❔ 판정 불가 (SMA200 미형성 · 상장 200일 미만)"
        status_type = "PENDING"
    elif qty > 0 and belief:
        if broken:
            act = "📌 신념 보유 · 추세 붕괴 (논리 점검 권장)"
            status_type = "BELIEF_WARN"
        elif rc == 2:
            act = "📌 신념 보유 · 강세"
            status_type = "BELIEF_GOOD"
        else:
            act = "📌 신념 보유 · 약세 (참고)"
            status_type = "BELIEF_WEAK"
    elif qty > 0:
        if broken:
            act = "🔍 논리 점검 (추세 붕괴 → 정리 검토)"
            status_type = "SELL"
        elif rc == 2:
            act = "✅ 보유 유지"
            status_type = "HOLD_GOOD"
        else:
            act = "⚠️ 보유 · 약세 (붕괴선 주시)"
            status_type = "HOLD_WARN"
    elif rc != 2:
        act = "⛔ 매수 금지 (강세 아님)"
        status_type = "AVOID"
    elif sym in picked_syms:
        act = f"🟢 매수 (내일 시가){shares_txt}"
        status_type = "BUY"
    elif sig > 0:
        act = "⏸ 신호 있으나 슬롯 없음"
        status_type = "PAUSE"
    else:
        act = "👀 관찰 (강세 · 신호 대기)"
        status_type = "WATCH"
        
    latest_status.append({
        'Symbol': sym, 'Close': c, 'RegCode': rc, 'Sig': sig, 'Broken': broken,
        'Brk': brk, 'DistBrk': dist_brk, 'Mom': mom, 'MomRank': mom_rank_str, 'Qty': qty, 'Avg': avg,
        'PnL_pct': pnl_pct, 'Belief': belief, 'Action': act, 'StatusType': status_type,
        'Date': df_sym.index[-1].strftime('%Y-%m-%d')
    })

status_df = pd.DataFrame(latest_status)

# ===== 상단 2: 오늘의 행동 요약 카드 + ? 마크 도움말 =====
title_col, help_col = st.columns([5, 1])
recent_date = status_df['Date'].iloc[0] if not status_df.empty else datetime.today().strftime('%Y-%m-%d')
with title_col:
    st.title("🏛️ Brothers Capital (브라더스 캐피탈)")
    st.caption(f"◆ 실전 현황판 · {recent_date} 종가 기준 · 시스템 보유 {my_held}/{cfg['max_pos']} (빈 슬롯 {my_free}) · 신념 보유 {my_bel}개 | 익일 시가 실행")
with help_col:
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    with st.popover("❓ v1.3 규칙 및 카드 보는 법"):
        st.markdown("""
        **🏛️ Brothers Capital v1.3 핵심 실전 원칙:**
        - **시스템 스윙 (최대 K개) vs 신념 보유 (Conviction) 분리:**
          - **💼 시스템 스윙:** 추세 순환매를 따르는 종목. 슬롯(기본 4개)을 차지하며 2일 연속 붕괴선 이탈 시 **🔍 논리 점검 후 정리 검토**합니다.
          - **📌 신념 보유:** 장기 가치관으로 보유하는 핵심 자산(예: 구글, 버크셔, 노보 등). **스윙 슬롯을 차지하지 않으며**, 추세가 꺾여도 강제 매도가 아닌 **'논리 점검 권장'**으로 투자 아이디어를 스스로 재확인하도록 돕습니다.
        - **🟢 초록 카드 (매수 추천):** 강세 국면(SMA200 위 & 상승) + 진입 신호 + 모멘텀 상위 + 빈 슬롯 확보 시 익일 시가 매수.
        - **🔍 빨강 카드 (논리 점검):** 2일 연속 붕괴선(-3%) 이탈 종목. 투자 논리를 점검하고 정리를 검토합니다.
        - **❔ 200일 미만 종목:** DRAM, VYLR처럼 상장 후 200일이 안 된 종목은 왜곡을 막기 위해 **'판정 불가'**로 안전하게 관리합니다.
        """)

buy_items = status_df[status_df['StatusType'] == "BUY"] if not status_df.empty else pd.DataFrame()
sell_items = status_df[status_df['StatusType'] == "SELL"] if not status_df.empty else pd.DataFrame()
belief_items = status_df[status_df['StatusType'].str.startswith("BELIEF")] if not status_df.empty else pd.DataFrame()
hold_items = status_df[status_df['StatusType'].isin(["HOLD_GOOD", "HOLD_WARN"])] if not status_df.empty else pd.DataFrame()

c1, c2, c3, c4 = st.columns(4)
with c1:
    if not buy_items.empty:
        buy_sorted = buy_items.sort_values(by='Mom', ascending=False)
        symbols_str = ", ".join([f"<b>{get_stock_short_label(row['Symbol'])}</b>" for _, row in buy_sorted.iterrows()])
        render_html(f"""<div class="card-buy"><h4 style="margin:0; font-size:1.0rem;">🟢 매수 추천 ({len(buy_items)}건)</h4><p style="margin:6px 0 0 0; font-size:0.92rem;">{symbols_str}</p><small style="opacity:0.9;">강세 국면 + 눌림/반등 진입</small></div>""")
    else:
        render_html("""<div class="card-empty"><b>🟢 매수 추천: 없음</b><br><small>오늘은 진입 신호가 없습니다.</small></div>""")
with c2:
    if not sell_items.empty:
        symbols_str = ", ".join([f"<b>{get_stock_short_label(row['Symbol'])}</b>" for _, row in sell_items.iterrows()])
        render_html(f"""<div class="card-sell"><h4 style="margin:0; font-size:1.0rem;">🔍 논리 점검 ({len(sell_items)}건)</h4><p style="margin:6px 0 0 0; font-size:0.92rem;">{symbols_str}</p><small style="opacity:0.9;">추세 붕괴선 이탈 → 정리 검토</small></div>""")
    else:
        render_html("""<div class="card-empty"><b>🔍 논리 점검: 없음</b><br><small>붕괴선을 이탈한 종목이 없습니다.</small></div>""")
with c3:
    if not belief_items.empty:
        symbols_str = ", ".join([f"<b>{get_stock_short_label(row['Symbol'])}</b>" for _, row in belief_items.iterrows()])
        render_html(f"""<div class="card-belief"><h4 style="margin:0; font-size:1.0rem;">📌 신념 보유 ({len(belief_items)}건)</h4><p style="margin:6px 0 0 0; font-size:0.92rem;">{symbols_str}</p><small style="opacity:0.9;">장기 신념 종목 (슬롯 미차감)</small></div>""")
    else:
        render_html("""<div class="card-empty"><b>📌 신념 보유 없음</b><br><small>신념 보유로 지정된 종목이 없습니다.</small></div>""")
with c4:
    if not hold_items.empty:
        symbols_str = ", ".join([f"<b>{get_stock_short_label(row['Symbol'])}</b>" for _, row in hold_items.iterrows()])
        render_html(f"""<div class="card-hold"><h4 style="margin:0; font-size:1.0rem;">✅ 시스템 보유 ({len(hold_items)}건)</h4><p style="margin:6px 0 0 0; font-size:0.92rem;">{symbols_str}</p><small style="opacity:0.9;">스윙 추세 유지 중. 원칙 홀딩</small></div>""")
    else:
        render_html("""<div class="card-empty"><b>✅ 시스템 보유 없음</b><br><small>보유 중인 시스템 종목이 없습니다.</small></div>""")

st.markdown("---")

# ===== 스타일 헬퍼: 세련된 로즈 레드 & 로열 블루 컬러링 =====
def style_pnl_val(val):
    if pd.isna(val) or val == 0:
        return 'color: #64748b;'
    elif val > 0:
        return 'color: #e11d48; font-weight: 700; background-color: #fff1f2;'
    else:
        return 'color: #2563eb; font-weight: 700; background-color: #eff6ff;'

# ===== 메인 탭 6개 구성 =====
tab_dashboard, tab_theme, tab_chart, tab_backtest, tab_macro, tab_settings = st.tabs([
    "📋 실전 현황판",
    "🔥 20대 테마 수급 & 순환매",
    "📈 종목별 정밀 차트",
    "📊 백테스트 리포트",
    "🌍 매크로 자산 비교",
    "⚙️ 설정 & 전략 커스텀"
])

# --- [탭 1] 실전 현황판 (한글/영문/티커 병기 표기!) ---
with tab_dashboard:
    h_col1, h_col2 = st.columns([5, 1])
    with h_col1:
        st.subheader("📋 바스켓 실전 현황판")
        st.caption("종목명에 한글명·영문명·티커가 함께 표기됩니다. 붉은색은 상승/수익, 푸른색은 하락/마이너스를 나타냅니다.")
    with h_col2:
        with st.popover("❓ 현황판 지표 읽는 법"):
            st.markdown("""
            **📋 표 항목별 상세 가이드:**
            - **종목명:** 한국 투자자와 동생이 헷갈리지 않도록 **한글명 (영문명 / 티커)**를 함께 표기합니다.
            - **국면:**
              - 🟢 **강세:** 주가가 200일선 위에 있고 200일선이 상승 중 (매수 허용 구간)
              - 🟡 **중립:** 주가는 200일선 위이나 이동평균선이 꺾임
              - 🔴 **약세:** 주가가 200일선 아래 (매수 절대 금지)
            - **오늘 신호:**
              - **A 지지반등:** 200일선 근처에서 망치형/상승장악형 캔들 출현 + MACD 반등
              - **B 눌림회복:** 20일선 눌림목 후 종가 회복 + 양봉
              - **C 골든크로스:** 0선 아래 깊은 과매도에서 MACD 골든크로스 + 거래량 확인
            - **붕괴선 (거리):** 200일선 대비 -3% 아래 가격. **이 가격 아래로 2일 연속 종가가 마감되면 손절/전량 매도**합니다.
            - **6M 모멘텀 (순위):** 최근 6개월간 상승 탄력도. 신호가 여러 개 동시에 뜨면 모멘텀 1위 순으로 슬롯을 채웁니다.
            """)
            
    if not status_df.empty:
        # 보기 모드 & 필터 선택 (모바일 친화적)
        v_col1, v_col2 = st.columns([2, 1])
        with v_col1:
            view_mode = st.radio(
                "보기 형식",
                ["📱 모바일 간편 카드 뷰", "🖥️ 전체 정밀 표 보기"],
                index=0, horizontal=True,
                help="핸드폰에서는 가로 스크롤 없이 한눈에 들어오는 '모바일 간편 카드 뷰'를 추천합니다."
            )
        with v_col2:
            filter_mode = st.selectbox(
                "종목 필터",
                ["전체 종목", "🔔 신호 발생 (매수/논리점검)", "📌 신념 보유 종목만", "💼 시스템 스윙 종목만", "🟢 강세 국면만"],
                index=0
            )

        filtered_status = status_df.copy()
        if filter_mode == "🟢 강세 국면만":
            filtered_status = filtered_status[filtered_status['RegCode'] == 2]
        elif filter_mode == "🔔 신호 발생 (매수/논리점검)":
            filtered_status = filtered_status[filtered_status['StatusType'].isin(["BUY", "SELL", "BELIEF_WARN"])]
        elif filter_mode == "📌 신념 보유 종목만":
            filtered_status = filtered_status[filtered_status['Belief'] == True]
        elif filter_mode == "💼 시스템 스윙 종목만":
            filtered_status = filtered_status[(filtered_status['Belief'] == False) & (filtered_status['Qty'] > 0)]

        if "모바일" in view_mode:
            if filtered_status.empty:
                st.info("선택한 필터에 해당하는 종목이 없습니다.")
            else:
                m_cols = st.columns(2)
                for idx, (_, row) in enumerate(filtered_status.iterrows()):
                    col_target = m_cols[idx % 2]
                    sym = row['Symbol']
                    kr_name = STOCK_META.get(sym, {}).get('kr', sym)
                    rc = row['RegCode']
                    if pd.isna(rc):
                        reg_badge = "❔ 데이터 부족"
                        reg_color = "#64748b"
                    elif rc == 2:
                        reg_badge = "🟢 강세"
                        reg_color = "#15803d"
                    elif rc == 1:
                        reg_badge = "🟡 중립"
                        reg_color = "#b45309"
                    elif rc == 0:
                        reg_badge = "🟠 조정"
                        reg_color = "#d97706"
                    else:
                        reg_badge = "🔴 약세"
                        reg_color = "#b91c1c"
                    
                    st_type = row['StatusType']
                    if st_type == "BUY":
                        act_badge = "🟢 매수 추천"
                        act_bg = "#dcfce7"; act_fg = "#15803d"
                    elif st_type == "SELL":
                        act_badge = "🔍 논리 점검"
                        act_bg = "#fee2e2"; act_fg = "#b91c1c"
                    elif st_type == "BELIEF_WARN":
                        act_badge = "📌 논리 점검"
                        act_bg = "#fce7f3"; act_fg = "#be185d"
                    elif st_type == "BELIEF_GOOD":
                        act_badge = "📌 신념 강세"
                        act_bg = "#ede9fe"; act_fg = "#6d28d9"
                    elif st_type == "BELIEF_WEAK":
                        act_badge = "📌 신념 약세"
                        act_bg = "#f1f5f9"; act_fg = "#64748b"
                    elif st_type == "HOLD_GOOD":
                        act_badge = "✅ 보유 유지"
                        act_bg = "#eff6ff"; act_fg = "#1d4ed8"
                    elif st_type == "HOLD_WARN":
                        act_badge = "⚠️ 보유 약세"
                        act_bg = "#fef3c7"; act_fg = "#b45309"
                    elif st_type == "PENDING":
                        act_badge = "❔ 판정 불가"
                        act_bg = "#f8fafc"; act_fg = "#64748b"
                    elif st_type == "PAUSE":
                        act_badge = "⏸ 슬롯 부족"
                        act_bg = "#ffedd5"; act_fg = "#c2410c"
                    elif st_type == "WATCH":
                        act_badge = "👀 신호 대기"
                        act_bg = "#fef3c7"; act_fg = "#b45309"
                    else:
                        act_badge = "⛔ 매수 금지"
                        act_bg = "#f1f5f9"; act_fg = "#64748b"
                        
                    mom_val = row['Mom'] * 100.0 if not pd.isna(row['Mom']) else np.nan
                    mom_color = "#e11d48" if (not pd.isna(mom_val) and mom_val > 0) else ("#2563eb" if (not pd.isna(mom_val) and mom_val < 0) else "#64748b")
                    mom_str = f"{mom_val:+.1f}%" if not pd.isna(mom_val) else "N/A"
                    mom_rank = row['MomRank']
                    
                    pnl_val = row['PnL_pct']
                    if pd.isna(pnl_val):
                        pnl_str = "-"
                        pnl_color = "#64748b"
                    else:
                        pnl_str = f"{pnl_val:+.1f}%"
                        pnl_color = "#e11d48" if pnl_val > 0 else "#2563eb"
                        
                    belief_tag = '<span style="font-size:0.74rem; background:#ede9fe; color:#6d28d9; padding:1px 5px; border-radius:4px; font-weight:700; margin-left:4px; border:1px solid #ddd6fe;">📌 신념</span>' if row['Belief'] else ""
                    hold_info = f"{row['Qty']:.0f}주 보유" if row['Qty'] > 0 else "미보유"
                    price_str = f"${row['Close']:,.2f}" if not pd.isna(row['Close']) else "N/A"
                    brk_str = f"${row['Brk']:,.1f} ({row['DistBrk']:+.1f}%)" if not pd.isna(row['Brk']) else "N/A"
                    
                    with col_target:
                        card_html = f"""
                        <div class="mobile-stock-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                <span style="font-weight: 700; font-size: 0.98rem; color: #0f172a;">{kr_name} <span style="font-size: 0.8rem; color: #64748b; font-weight: normal;">({sym})</span>{belief_tag}</span>
                                <span style="font-size: 0.78rem; font-weight: 600; padding: 2px 6px; border-radius: 4px; background: #f8fafc; border: 1px solid #e2e8f0; color: {reg_color};">{reg_badge}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                                <div>
                                    <span style="font-size: 1.22rem; font-weight: 800; color: #0f172a;">{price_str}</span>
                                    <span style="font-size: 0.78rem; color: #64748b; margin-left: 6px;">({hold_info})</span>
                                </div>
                                <span style="font-size: 0.8rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; background-color: {act_bg}; color: {act_fg};">{act_badge}</span>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; background: #f8fafc; padding: 8px 10px; border-radius: 6px; font-size: 0.78rem; border: 1px solid #f1f5f9;">
                                <div><span style="color: #64748b;">모멘텀</span><br/><b style="color: {mom_color};">{mom_str} ({mom_rank}위)</b></div>
                                <div><span style="color: #64748b;">붕괴선</span><br/><b>{brk_str}</b></div>
                                <div><span style="color: #64748b;">내 손익률</span><br/><b style="color: {pnl_color};">{pnl_str}</b></div>
                            </div>
                        </div>
                        """
                        render_html(card_html)
        else:
            disp_df = filtered_status.copy()
            disp_df['구분'] = disp_df['Belief'].apply(lambda b: "📌 신념" if b else "💼 시스템")
            disp_df['종목 (한글 / 영문 / 티커)'] = disp_df['Symbol'].apply(get_stock_label)
            disp_df['현재가'] = disp_df['Close'].apply(lambda x: f"${x:,.2f}" if not pd.isna(x) else "N/A")
            disp_df['국면'] = disp_df['RegCode'].apply(lambda x: "🟢 강세" if x==2 else ("🟡 중립" if x==1 else ("🟠 조정" if x==0 else ("🔴 약세" if x==-1 else "❔ 데이터 부족"))))
            disp_df['오늘 신호'] = disp_df['Sig'].apply(lambda x: "A 지지반등" if x==1 else ("B 눌림회복" if x==2 else ("C 골든크로스" if x==3 else "-")))
            disp_df['붕괴선 (거리)'] = disp_df.apply(lambda r: f"${r['Brk']:,.2f} ({r['DistBrk']:+.1f}%)" if not pd.isna(r['Brk']) else "N/A", axis=1)
            disp_df['모멘텀 (순위)'] = disp_df.apply(lambda r: f"{r['Mom']*100.0:+.1f}% ({r['MomRank']}위)" if not pd.isna(r['Mom']) else "N/A", axis=1)
            disp_df['내 보유 (손익)'] = disp_df.apply(lambda r: f"{r['Qty']:.0f}주 @ ${r['Avg']:,.2f} ({r['PnL_pct']:+.1f}%)" if r['Qty']>0 and not pd.isna(r['PnL_pct']) else (f"{r['Qty']:.0f}주" if r['Qty']>0 else "-"), axis=1)
            disp_df['행동 가이드'] = disp_df['Action']
            
            cols_show = ['구분', '종목 (한글 / 영문 / 티커)', '현재가', '국면', '오늘 신호', '붕괴선 (거리)', '모멘텀 (순위)', '내 보유 (손익)', '행동 가이드']
            st.dataframe(disp_df[cols_show], use_container_width=True, hide_index=True)
    else:
        st.warning("등록된 종목이 없습니다. [⚙️ 설정] 탭에서 종목을 추가하세요.")

# --- [탭 2] 20대 테마 수급 & 순환매 ---
with tab_theme:
    t_head1, t_head2 = st.columns([5, 1])
    with t_head1:
        st.subheader("🔥 20대 시장 주도 테마 수급 & 자금 쏠림 트래커")
        st.caption("AI반도체, 원자력/SMR, 비만치료제, 양자컴 등 모든 종목의 한글명과 티커가 함께 표시됩니다.")
    with t_head2:
        with st.popover("❓ 테마 트래커 활용법"):
            st.markdown("""
            **🔥 테마 수급 분석 노하우:**
            - 상단 모멘텀 순위에서 **오늘 1~3위에 오른 강한 테마 (붉은색 바)**를 먼저 확인하세요.
            - 해당 테마의 종목들 중 거래량이 평소 대비 1.5~2배 이상 터진 종목을 눈여겨보세요.
            - 마음에 드는 종목은 **`[🧺 내 실전 바스켓에 추가]`** 버튼으로 바로 등록할 수 있습니다.
            """)
            
    current_themes = st.session_state.themes
    theme_raw = fetch_all_themes_data(current_themes)
    
    theme_stats = []
    symbol_details = {}
    
    for theme_name, t_info in current_themes.items():
        syms = t_info['symbols']
        chg_1d_list = []; chg_1w_list = []; chg_1m_list = []
        for s in syms:
            if s in theme_raw.columns.levels[0]:
                sub = theme_raw[s].dropna(subset=['Close'])
                if len(sub) >= 22:
                    c_now = sub['Close'].iloc[-1]; c_prev = sub['Close'].iloc[-2]
                    c_1w = sub['Close'].iloc[-5] if len(sub) >= 5 else sub['Close'].iloc[0]
                    c_1m = sub['Close'].iloc[-20] if len(sub) >= 20 else sub['Close'].iloc[0]
                    v_now = sub['Volume'].iloc[-1]; v_avg20 = sub['Volume'].iloc[-20:].mean()
                    r_1d = (c_now / c_prev - 1.0) * 100.0
                    r_1w = (c_now / c_1w - 1.0) * 100.0
                    r_1m = (c_now / c_1m - 1.0) * 100.0
                    vol_mult = (v_now / v_avg20) if v_avg20 > 0 else 1.0
                    chg_1d_list.append(r_1d); chg_1w_list.append(r_1w); chg_1m_list.append(r_1m)
                    symbol_details[s] = {
                        "theme": theme_name, "close": c_now, "chg_1d": r_1d,
                        "chg_1w": r_1w, "chg_1m": r_1m, "vol_mult": vol_mult, "df": sub
                    }
        theme_stats.append({
            "테마": theme_name, "분야": t_info.get('cat', '기타'), "설명": t_info['desc'],
            "오늘 평균": np.mean(chg_1d_list) if chg_1d_list else 0.0,
            "1주일 평균": np.mean(chg_1w_list) if chg_1w_list else 0.0,
            "1개월 평균": np.mean(chg_1m_list) if chg_1m_list else 0.0,
            "종목수": len(syms)
        })
    t_summary_df = pd.DataFrame(theme_stats)
    
    col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 2])
    with col_f1:
        cat_list = ["전체"] + sorted(list(set(t_summary_df['분야'])))
        selected_cat = st.selectbox("분야별 필터", cat_list, index=0, help="원하는 산업 분야만 모아봅니다.")
    with col_f2:
        time_sort = st.selectbox("모멘텀 정렬 기준", ["오늘 (1일)", "최근 1주일 (5일)", "최근 1개월 (20일)"], index=0, help="순위를 매길 기간을 선택합니다.")
    with col_f3:
        search_kw = st.text_input("테마 또는 종목 검색 (한글/영문/티커 전부 가능, 예: 엔비디아, Tesla, 원자력)", "", help="한글, 영문, 티커 상관없이 검색됩니다.").strip()
        if search_kw:
            preview_matches = []
            for s, meta in STOCK_META.items():
                if search_kw.lower() in s.lower() or search_kw.lower() in meta.get('kr', '').lower() or search_kw.lower() in meta.get('en', '').lower():
                    preview_matches.append(s)
            if preview_matches:
                st.caption(f"💡 연관 추천 종목 ({len(preview_matches)}건):")
                st.pills("연관 종목", options=preview_matches[:6], format_func=get_stock_short_label, label_visibility="collapsed", key="tab2_preview_pills")
        
    filtered_df = t_summary_df.copy()
    if selected_cat != "전체":
        filtered_df = filtered_df[filtered_df['분야'] == selected_cat]
    if search_kw:
        # 한글, 영문, 티커 매칭 검색
        filtered_df = filtered_df[
            filtered_df['테마'].str.contains(search_kw, case=False) |
            filtered_df['설명'].str.contains(search_kw, case=False) |
            filtered_df['테마'].apply(lambda t: any(
                search_kw.lower() in s.lower() or
                search_kw.lower() in STOCK_META.get(s, {}).get('kr', '').lower() or
                search_kw.lower() in STOCK_META.get(s, {}).get('en', '').lower()
                for s in current_themes.get(t, {}).get('symbols', [])
            ))
        ]
        
    sort_col = "오늘 평균" if "1일" in time_sort else ("1주일 평균" if "1주일" in time_sort else "1개월 평균")
    sorted_all_df = filtered_df.sort_values(by=sort_col, ascending=False)
    
    # 1. 상단 자금 유입 vs 자금 유출 핵심 요약 박스
    top_inflow = sorted_all_df.head(3)
    top_outflow = sorted_all_df.tail(3).sort_values(by=sort_col, ascending=True)
    
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        in_str = " | ".join([f"<b>{r['테마'].split(' ')[0]} {r['테마'].split(' ')[1]}</b> ({r[sort_col]:+.2f}%)" for _, r in top_inflow.iterrows()])
        render_html(f"""
        <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:10px; padding:12px 16px; margin-bottom:12px;">
            <b style="color:#e11d48; font-size:0.95rem;">🔥 자금 급유입 TOP 3 (돈이 몰리는 주도 테마)</b>
            <div style="margin-top:4px; font-size:0.92rem; color:#0f172a;">{in_str}</div>
        </div>
        """)
        
    with s_col2:
        out_str = " | ".join([f"<b>{r['테마'].split(' ')[0]} {r['테마'].split(' ')[1]}</b> ({r[sort_col]:+.2f}%)" for _, r in top_outflow.iterrows()])
        render_html(f"""
        <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:12px 16px; margin-bottom:12px;">
            <b style="color:#2563eb; font-size:0.95rem;">🧊 자금 급유출 TOP 3 (돈이 빠져나가는 소외 테마)</b>
            <div style="margin-top:4px; font-size:0.92rem; color:#0f172a;">{out_str}</div>
        </div>
        """)

    # 2. 유입 vs 유출 나란히 2단 차트 (좌측: 돈 몰리는 곳, 우측: 돈 빠지는 곳)
    c_chart_in, c_chart_out = st.columns(2)
    
    with c_chart_in:
        inflow_df = sorted_all_df.head(7).sort_values(by=sort_col, ascending=True)
        fig_in = go.Figure(go.Bar(
            x=inflow_df[sort_col], y=inflow_df['테마'], orientation='h',
            marker_color='#e11d48', text=[f"{x:+.2f}%" for x in inflow_df[sort_col]], textposition='outside'
        ))
        fig_in.update_layout(
            title=f"<b>🔥 자금 유입 상위 테마 ({time_sort})</b>",
            xaxis_title="평균 상승률 (%)", template="plotly_white", height=270,
            margin=dict(l=10, r=40, t=35, b=15)
        )
        st.plotly_chart(fig_in, use_container_width=True)
        
    with c_chart_out:
        outflow_df = sorted_all_df.tail(7).sort_values(by=sort_col, ascending=False)
        fig_out = go.Figure(go.Bar(
            x=outflow_df[sort_col], y=outflow_df['테마'], orientation='h',
            marker_color='#2563eb', text=[f"{x:+.2f}%" for x in outflow_df[sort_col]], textposition='outside'
        ))
        fig_out.update_layout(
            title=f"<b>🧊 자금 유출 (소외/하락) 테마 ({time_sort})</b>",
            xaxis_title="평균 하락률 (%)", template="plotly_white", height=270,
            margin=dict(l=10, r=40, t=35, b=15)
        )
        st.plotly_chart(fig_out, use_container_width=True)
        
    st.markdown("---")
    
    col_t_left, col_t_right = st.columns([1.2, 1.3])
    with col_t_left:
        st.markdown("#### 📂 테마 선택")
        selected_theme_name = st.selectbox("상세 종목을 확인할 테마를 고르세요", list(filtered_df['테마']), index=0 if not filtered_df.empty else 0)
        t_obj = current_themes.get(selected_theme_name, {})
        if t_obj:
            names_str = ", ".join([get_stock_short_label(s) for s in t_obj['symbols']])
            render_html(f"""
            <div class="theme-header">
                <h4 style="margin:0; color:#0f172a;">{selected_theme_name}</h4>
                <p style="margin:4px 0 0 0; color:#475569; font-size:0.9rem;">{t_obj['desc']}</p>
                <small style="color:#64748b;">분야: {t_obj.get('cat','')} | 구성 종목: {names_str}</small>
            </div>
            """)
            
            t_rows = []
            for s in t_obj['symbols']:
                if s in symbol_details:
                    it = symbol_details[s]
                    t_rows.append({
                        "종목 (한글 / 티커)": get_stock_short_label(s),
                        "현재가": f"${it['close']:,.2f}",
                        "오늘 등락률": it['chg_1d'],
                        "1주일 수익률": it['chg_1w'],
                        "1개월 수익률": it['chg_1m'],
                        "거래량(20일대비)": f"{it['vol_mult']:.1f}배",
                        "_ticker": s
                    })
            if t_rows:
                t_df_show = pd.DataFrame(t_rows).sort_values(by='오늘 등락률', ascending=False)
                styled_theme_df = t_df_show.style.format({
                    '오늘 등락률': lambda x: f"{x:+.2f}%",
                    '1주일 수익률': lambda x: f"{x:+.2f}%",
                    '1개월 수익률': lambda x: f"{x:+.2f}%",
                }).map(style_pnl_val, subset=['오늘 등락률', '1주일 수익률', '1개월 수익률'])
                st.dataframe(styled_theme_df, use_container_width=True, hide_index=True)
                
    with col_t_right:
        st.markdown("#### 📈 종목 즉시 차트 & 바스켓 추가")
        if t_obj and t_obj['symbols']:
            # 드롭다운 옵션에 한글명과 티커를 함께 표시!
            stock_options = {get_stock_label(s): s for s in t_obj['symbols']}
            selected_label = st.selectbox("차트를 볼 종목 선택", list(stock_options.keys()), index=0)
            target_stock = stock_options[selected_label]
            
            b_col1, b_col2 = st.columns([1, 1])
            with b_col1:
                if st.button(f"🧺 '{get_stock_short_label(target_stock)}' 바스켓에 추가", type="primary", use_container_width=True):
                    existing_b = [x['symbol'] for x in st.session_state.basket]
                    if target_stock in existing_b:
                        st.warning("이미 바스켓에 등록된 종목입니다.")
                    else:
                        st.session_state.basket.append({"symbol": target_stock, "use": True, "qty": 0.0, "avg": 0.0})
                        save_basket_to_disk(st.session_state.basket)
                        st.success(f"{get_stock_short_label(target_stock)} 종목이 내 바스켓에 영구 저장되었습니다!")
                        st.rerun()
            with b_col2:
                st.caption(f"이 종목을 내 실전 바스켓에 넣고 200일선 붕괴선 감시를 시작합니다.")
                
            if target_stock in symbol_details:
                df_sub = symbol_details[target_stock]['df']
                fig_sub = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25])
                fig_sub.add_trace(go.Candlestick(
                    x=df_sub.index, open=df_sub['Open'], high=df_sub['High'],
                    low=df_sub['Low'], close=df_sub['Close'], name='주가',
                    increasing=dict(line=dict(color='#e11d48'), fillcolor='#e11d48'),
                    decreasing=dict(line=dict(color='#2563eb'), fillcolor='#2563eb')
                ), row=1, col=1)
                e20_s = df_sub['Close'].ewm(span=20, adjust=False).mean()
                fig_sub.add_trace(go.Scatter(x=df_sub.index, y=e20_s, mode='lines', name='EMA 20', line=dict(color='#64748b', width=1.5)), row=1, col=1)
                v_col = ['#e11d48' if c >= o else '#2563eb' for c, o in zip(df_sub['Close'], df_sub['Open'])]
                fig_sub.add_trace(go.Bar(x=df_sub.index, y=df_sub['Volume'], name='거래량', marker_color=v_col), row=2, col=1)
                fig_sub.update_layout(
                    title=f"<b>{get_stock_label(target_stock)}</b> 최근 일봉 캔들 & 거래량",
                    xaxis_rangeslider_visible=False, template="plotly_white", height=380, hovermode="x unified"
                )
                st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown("---")
    with st.expander("➕ 나만의 커스텀 테마 새로 만들기 (원하는 종목 묶음 등록)"):
        st.caption("내가 관심 있는 종목들을 묶어서 새로운 테마로 등록하면, 자금 흐름과 순위가 자동으로 계산됩니다.")
        c_th1, c_th2 = st.columns(2)
        with c_th1:
            new_th_name = st.text_input("새 테마 이름 (예: 🚀 한국형 방산 수혜주, 💊 차세대 ADC 바이오)", "").strip()
            new_th_desc = st.text_input("테마 설명", "사용자 정의 관심 테마")
        with c_th2:
            new_th_cat = st.selectbox("테마 분야", ["IT/테크", "바이오/헬스", "에너지/인프라", "미래기술", "금융/크립토", "우주/방산", "기타"])
            new_th_syms = st.text_input("종목 티커 또는 한글명 (쉼표로 구분, 예: 엔비디아, 테슬라, PLTR)", "").strip()
            
        if st.button("✨ 새 테마 등록하기"):
            if new_th_name and new_th_syms:
                raw_items = [x.strip() for x in new_th_syms.split(',') if x.strip()]
                sym_list = [resolve_ticker_input(x) for x in raw_items]
                t_data = {"cat": new_th_cat, "desc": new_th_desc, "symbols": sym_list}
                st.session_state.themes[new_th_name] = t_data
                save_custom_theme_to_disk(new_th_name, t_data)
                st.cache_data.clear()
                st.success(f"'{new_th_name}' 테마가 성공적으로 등록 및 영구 저장되었습니다!")
                st.rerun()
            else:
                st.error("테마 이름과 1개 이상의 티커를 입력해주세요.")

# --- [탭 3] 종목별 정밀 차트 뷰어 (한글/영문/티커 병기) ---
with tab_chart:
    c_head1, c_head2 = st.columns([5, 1])
    with c_head1:
        st.subheader("📈 종목별 캔들스틱 & 지표 정밀 차트")
        st.caption("200일선(노란선), 20일선(회색선), 붕괴 방어선(빨간 점선)과 거래량을 정밀하게 분석합니다.")
    with c_head2:
        with st.popover("❓ 차트 지표 보는 법"):
            st.markdown("""
            **📈 차트 선의 의미와 매매 포인트:**
            - **양봉/음봉 색상:** 한국 투자자 기준 **붉은색이 상승(양봉)**, **푸른색이 하락(음봉)**입니다.
            - **노란 실선 (SMA 200):** 1년간의 평균 매수가격 (장기 생명선). 주가가 이 선 위에 있어야만 강세 국면입니다.
            - **회색 실선 (EMA 20):** 1달간의 단기 추세선. 강세장에서 주가가 20일선까지 눌렸다가 양봉으로 반등할 때(신호 B)가 훌륭한 매수 타점입니다.
            - **빨간 점선 (붕괴선):** 200일선 대비 -3% 아래 가격. 이 선 아래로 2일 연속 마감되면 추세가 완전히 깨진 것이므로 무조건 전량 매도합니다.
            """)
            
    available_symbols = list(ind_dict.keys())
    if available_symbols:
        chart_options = {get_stock_label(s): s for s in available_symbols}
        selected_chart_label = st.selectbox(
            "분석할 종목을 선택하세요 (한글/영문/티커)",
            list(chart_options.keys()),
            index=0,
            help="드롭다운을 누르고 '엔비', '테슬' 등을 타이핑하면 원하는 종목으로 바로 이동합니다."
        )
        selected_sym = chart_options[selected_chart_label]
        
        if len(available_symbols) <= 12:
            st.caption("⚡ **원터치 빠른 종목 전환:**")
            quick_p = st.pills(
                "빠른 종목 선택",
                options=available_symbols,
                format_func=get_stock_short_label,
                default=selected_sym,
                label_visibility="collapsed",
                key="tab3_pills_picker"
            )
            if quick_p and quick_p != selected_sym:
                selected_sym = quick_p
                
        df_target = ind_dict[selected_sym].tail(250).copy()
        
        # 보조지표 계산
        close_s = df_target['Close']
        high_s = df_target['High']
        low_s = df_target['Low']
        vol_s = df_target['Volume']
        
        # 1) 볼린저 밴드 (20, 2)
        bb_mid = close_s.rolling(20).mean()
        bb_std = close_s.rolling(20).std()
        bb_upper = bb_mid + (2 * bb_std)
        bb_lower = bb_mid - (2 * bb_std)
        
        # 2) 다중 이동평균선 (5, 60, 120일)
        sma5 = close_s.rolling(5).mean()
        sma60 = close_s.rolling(60).mean()
        sma120 = close_s.rolling(120).mean()
        
        # 3) RSI (14)
        delta = close_s.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss.replace(0, np.nan))
        rsi = 100 - (100 / (1 + rs))
        
        # 4) MACD (12, 26, 9)
        e12 = close_s.ewm(span=12, adjust=False).mean()
        e26 = close_s.ewm(span=26, adjust=False).mean()
        macd_line = e12 - e26
        macd_sig = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - macd_sig
        
        # ===== 보조지표 On/Off 토글 컨트롤 바 =====
        st.markdown("**🛠️ 보조지표 On / Off 토글:**")
        tog_c1, tog_c2, tog_c3, tog_c4, tog_c5, tog_c6 = st.columns(6)
        with tog_c1:
            t_strat = st.checkbox("전략선 (200선/붕괴선)", value=True, help="200일선과 -3% 붕괴 손절선을 표시합니다.")
        with tog_c2:
            t_bb = st.checkbox("볼린저 밴드 (20, 2)", value=False, help="20일 기준 표준편차 ±2 밴드를 표시합니다.")
        with tog_c3:
            t_emas = st.checkbox("이평선 (5/60/120선)", value=False, help="5일(초단기), 60일(중기), 120일(경기선)을 표시합니다.")
        with tog_c4:
            t_vol = st.checkbox("거래량 (Volume)", value=True, help="일별 거래량 바 차트를 표시합니다.")
        with tog_c5:
            t_rsi = st.checkbox("RSI (14)", value=False, help="과열(70)과 과매도(30)를 감지하는 RSI 보조지표를 표시합니다.")
        with tog_c6:
            t_macd = st.checkbox("MACD (12,26,9)", value=False, help="추세 전환과 골든크로스를 감지하는 MACD를 표시합니다.")

        # 서브플롯 동적 행 구성 및 높이 정규화
        subplot_titles = ["<b>주가 (일봉 캔들)</b>"]
        n_rows = 1
        row_map = {}
        if t_vol:
            n_rows += 1
            row_map['vol'] = n_rows
            subplot_titles.append("<b>거래량</b>")
        if t_rsi:
            n_rows += 1
            row_map['rsi'] = n_rows
            subplot_titles.append("<b>RSI (14)</b>")
        if t_macd:
            n_rows += 1
            row_map['macd'] = n_rows
            subplot_titles.append("<b>MACD (12, 26, 9)</b>")
            
        if n_rows == 1:
            row_heights = [1.0]
            total_height = 460
        else:
            sub_h = 0.35 / (n_rows - 1)
            row_heights = [0.65] + [sub_h] * (n_rows - 1)
            total_height = 420 + (n_rows - 1) * 110
            
        fig_c = make_subplots(
            rows=n_rows, cols=1, shared_xaxes=True,
            vertical_spacing=0.04, row_heights=row_heights,
            subplot_titles=subplot_titles
        )
        
        # 1. 메인 캔들스틱 (Row 1)
        fig_c.add_trace(go.Candlestick(
            x=df_target.index, open=df_target['Open'], high=df_target['High'],
            low=df_target['Low'], close=df_target['Close'], name='주가 (일봉)',
            increasing=dict(line=dict(color='#e11d48'), fillcolor='#e11d48'),
            decreasing=dict(line=dict(color='#2563eb'), fillcolor='#2563eb')
        ), row=1, col=1)
        
        # 전략선 (SMA200, 붕괴선, EMA20)
        if t_strat:
            fig_c.add_trace(go.Scatter(x=df_target.index, y=df_target['SMA200'], mode='lines', name=f'SMA {cfg["sma_len"]}', line=dict(color='#eab308', width=2)), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=df_target['E20'], mode='lines', name='EMA 20', line=dict(color='#64748b', width=1.5)), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=df_target['Brk'], mode='lines', name='붕괴선', line=dict(color='#dc2626', width=1.2, dash='dot')), row=1, col=1)
            
        # 볼린저 밴드
        if t_bb:
            fig_c.add_trace(go.Scatter(x=df_target.index, y=bb_upper, mode='lines', name='BB 상단', line=dict(color='#a855f7', width=1, dash='dot')), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=bb_lower, mode='lines', name='BB 하단', line=dict(color='#a855f7', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(168, 85, 247, 0.05)'), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=bb_mid, mode='lines', name='BB 중심(20)', line=dict(color='#c084fc', width=1)), row=1, col=1)

        # 다중 이평선
        if t_emas:
            fig_c.add_trace(go.Scatter(x=df_target.index, y=sma5, mode='lines', name='SMA 5 (초단기)', line=dict(color='#06b6d4', width=1.2)), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=sma60, mode='lines', name='SMA 60 (중기)', line=dict(color='#10b981', width=1.5)), row=1, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=sma120, mode='lines', name='SMA 120 (경기)', line=dict(color='#f97316', width=1.5)), row=1, col=1)

        # 2. 거래량 서브플롯
        if t_vol and 'vol' in row_map:
            v_row = row_map['vol']
            colors_vol = ['#e11d48' if c >= o else '#2563eb' for c, o in zip(df_target['Close'], df_target['Open'])]
            fig_c.add_trace(go.Bar(x=df_target.index, y=vol_s, name='거래량', marker_color=colors_vol), row=v_row, col=1)
            vol_ma20 = vol_s.rolling(20).mean()
            fig_c.add_trace(go.Scatter(x=df_target.index, y=vol_ma20, mode='lines', name='거래량 20MA', line=dict(color='#f59e0b', width=1)), row=v_row, col=1)

        # 3. RSI 서브플롯
        if t_rsi and 'rsi' in row_map:
            r_row = row_map['rsi']
            fig_c.add_trace(go.Scatter(x=df_target.index, y=rsi, mode='lines', name='RSI', line=dict(color='#8b5cf6', width=1.8)), row=r_row, col=1)
            fig_c.add_hline(y=70, line_dash="dash", line_color="#e11d48", line_width=1, row=r_row, col=1)
            fig_c.add_hline(y=30, line_dash="dash", line_color="#2563eb", line_width=1, row=r_row, col=1)
            fig_c.update_yaxes(range=[10, 90], row=r_row, col=1)

        # 4. MACD 서브플롯
        if t_macd and 'macd' in row_map:
            m_row = row_map['macd']
            fig_c.add_trace(go.Scatter(x=df_target.index, y=macd_line, mode='lines', name='MACD', line=dict(color='#3b82f6', width=1.5)), row=m_row, col=1)
            fig_c.add_trace(go.Scatter(x=df_target.index, y=macd_sig, mode='lines', name='Signal', line=dict(color='#f97316', width=1.2)), row=m_row, col=1)
            hist_colors = ['#e11d48' if val >= 0 else '#2563eb' for val in macd_hist]
            fig_c.add_trace(go.Bar(x=df_target.index, y=macd_hist, name='오실레이터', marker_color=hist_colors), row=m_row, col=1)

        fig_c.update_layout(
            xaxis_rangeslider_visible=False,
            template="plotly_white",
            height=total_height,
            hovermode="x unified",
            margin=dict(l=10, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_c, use_container_width=True)
        
        # 하단 AI 종합 기술적 진단 요약 박스
        last_item = df_target.iloc[-1]
        c_val = last_item['Close']; s200_val = last_item['SMA200']
        dist_sma = (c_val / s200_val - 1.0) * 100.0 if (not pd.isna(s200_val) and s200_val > 0) else np.nan
        last_rsi = rsi.iloc[-1] if not rsi.empty else np.nan
        last_macd_h = macd_hist.iloc[-1] if not macd_hist.empty else np.nan
        
        rsi_comment = "과열권 (차익실현 주의)" if (not pd.isna(last_rsi) and last_rsi >= 70) else ("과매도권 (기술적 반등 기대)" if (not pd.isna(last_rsi) and last_rsi <= 30) else "안정적 중립 구간")
        macd_comment = "매수 우위 (양의 모멘텀)" if (not pd.isna(last_macd_h) and last_macd_h > 0) else "조정/매도 우위 (음의 모멘텀)"
        
        c_str = f"${c_val:,.2f}" if not pd.isna(c_val) else "-"
        s200_str = f"${s200_val:,.2f}" if not pd.isna(s200_val) else "계산중"
        dist_str = f"{dist_sma:+.1f}%" if not pd.isna(dist_sma) else "-"
        brk_str = f"${last_item['Brk']:,.2f}" if not pd.isna(last_item['Brk']) else "계산중"
        rsi_str = f"{last_rsi:.1f}" if not pd.isna(last_rsi) else "-"
        macd_str = f"{last_macd_h:+.2f}" if not pd.isna(last_macd_h) else "-"
        
        st.markdown(f"""
        > 💡 **{get_stock_short_label(selected_sym)} 실시간 기술적 진단 리포트:**
        > - **200일선 이격도:** 현재가 **{c_str}**는 200일선({s200_str}) 대비 **{dist_str}** 위치에 있습니다.
        > - **붕괴 방어선:** **{brk_str}** (2일 연속 이탈 시 원칙 손절)
        > - **RSI(14):** **{rsi_str}** 👉 **{rsi_comment}**
        > - **MACD 모멘텀:** **{macd_comment}** (오실레이터: {macd_str})
        """)
    else:
        st.info("차트를 표시할 종목 데이터가 없습니다.")

# --- [탭 4] 백테스트 리포트 ---
with tab_backtest:
    b_head1, b_head2 = st.columns([5, 1])
    with b_head1:
        st.subheader("📊 맞춤형 포트폴리오 백테스트 리포트")
        st.caption(f"시뮬레이션 기간: {cfg['start_year']}년 ~ 현재 | 최대 동시 보유 {cfg['max_pos']}개 슬롯 | 모멘텀 상위 순환 배분")
    with b_head2:
        with st.popover("❓ 백테스트 지표 용어 정리"):
            st.markdown("""
            **📊 성과 분석 핵심 지표:**
            - **연평균 수익률 (CAGR):** 복리로 계산한 1년 평균 성장률입니다. 단순 합산이 아닌 진짜 복리 수익률입니다.
            - **최대 낙폭 (MDD):** 역사상 고점에서 계좌가 가장 크게 깨졌을 때의 하락폭(%)입니다. 숫자가 작을수록(덜 떨어질수록) 안전합니다.
            - **위험 감소율 (%p 방어):** 지수(SPY)가 폭락할 때 내 전략이 얼마나 덜 떨어졌는지를 보여주는 방어력 수치입니다.
            - **칼마 비율 (Calmar Ratio):** `CAGR / |MDD|`로, "위험(MDD) 대비 얼마나 많은 수익(CAGR)을 냈는가"를 측정하는 퀀트 핵심 지표입니다. 높을수록 우수합니다.
            - **승률 (Win Rate):** 전체 매매 중 이익으로 청산된 거래의 비율입니다.
            """)
            
    def run_sim(ind_dict, common_idx, max_pos, cost_pct, cash_yield=0.0):
        cash = 100.0; equity = 100.0
        sh = {s: 0.0 for s in ind_dict}; e_px = {s: np.nan for s in ind_dict}; e_cost = {s: 0.0 for s in ind_dict}
        e_date = {s: None for s in ind_dict}; p_buy = {s: False for s in ind_dict}; p_sell = {s: False for s in ind_dict}
        trades = []; daily_eq = []; daily_ew = []; ew_eq = 100.0; prev_p = {}
        daily_exposure = []
        gross_p = 0.0; gross_l = 0.0
        
        for dt in common_idx:
            if cash_yield > 0:
                cash *= (1.0 + cash_yield / 100.0 / 252.0)
                
            for s in ind_dict:
                if p_sell[s]:
                    q = sh[s]
                    if q > 0 and dt in ind_dict[s].index:
                        px = ind_dict[s].loc[dt, 'Open']
                        proc = q * px * (1.0 - cost_pct); pnl = proc - e_cost[s]
                        if pnl > 0: gross_p += pnl
                        else: gross_l += abs(pnl)
                        trades.append({'Symbol': s, 'EntryDate': e_date[s], 'ExitDate': dt, 'PnL_pct': (proc / e_cost[s] - 1.0) * 100.0, 'HoldDays': (dt - e_date[s]).days if e_date[s] else 0, 'PnL': pnl})
                        cash += proc; sh[s] = 0.0; e_cost[s] = 0.0
                    p_sell[s] = False
                    
            for s in ind_dict:
                if p_buy[s]:
                    if dt in ind_dict[s].index:
                        px = ind_dict[s].loc[dt, 'Open']; bud = min(equity / max_pos, cash)
                        if bud > 0 and px > 0:
                            q = bud / (px * (1.0 + cost_pct)); cost = q * px * (1.0 + cost_pct)
                            cash -= cost; sh[s] = q; e_cost[s] = cost; e_date[s] = dt
                    p_buy[s] = False
                    
            pos_val = 0.0; held_n = 0; ew_day = []
            for s in ind_dict:
                if dt in ind_dict[s].index:
                    c = ind_dict[s].loc[dt, 'Close']
                    if sh[s] > 0:
                        pos_val += sh[s] * c; held_n += 1
                    if s in prev_p and prev_p[s] > 0:
                        ew_day.append(c / prev_p[s] - 1.0)
                    prev_p[s] = c
            equity = cash + pos_val; daily_eq.append(equity)
            daily_exposure.append(pos_val / equity * 100.0 if equity > 0 else 0.0)
            if ew_day:
                ew_eq *= (1.0 + np.mean(ew_day))
            daily_ew.append(ew_eq)
            
            n_sell = 0
            for s in ind_dict:
                if sh[s] > 0 and dt in ind_dict[s].index:
                    if ind_dict[s].loc[dt, 'Broken']:
                        p_sell[s] = True; n_sell += 1
                        
            free_slots = max_pos - held_n + n_sell
            if free_slots > 0:
                cands = []
                for s in ind_dict:
                    if sh[s] == 0 and not p_buy[s] and dt in ind_dict[s].index:
                        r = ind_dict[s].loc[dt]
                        if r['Sig'] > 0:
                            cands.append((s, r['Mom']))
                cands.sort(key=lambda x: x[1] if not np.isnan(x[1]) else -999, reverse=True)
                for cand in cands[:free_slots]:
                    p_buy[cand[0]] = True
                    
        res_df = pd.DataFrame({'Date': common_idx, 'Strategy': daily_eq, 'EqualWeight': daily_ew, 'Exposure': daily_exposure}).set_index('Date')
        stats_extra = {'gross_p': gross_p, 'gross_l': gross_l}
        return res_df, pd.DataFrame(trades), stats_extra

    if ind_dict and len(common_idx) > 20:
        sim_res, t_df, s_extra = run_sim(ind_dict, common_idx, cfg['max_pos'], cfg['cost_pct']/100.0, cfg.get('cash_yield', 0.0))
        spy_c = spy_df.loc[common_idx, 'Close']
        sim_res['SPY'] = spy_c / spy_c.iloc[0] * 100.0
        
        def get_stat(series):
            if len(series) < 5:
                return np.nan, np.nan, np.nan
            yrs = (series.index[-1] - series.index[0]).days / 365.25
            cagr = ((series.iloc[-1] / series.iloc[0]) ** (1.0 / yrs) - 1.0) * 100.0 if yrs >= 0.5 else np.nan
            mdd = ((series / series.cummax() - 1.0) * 100.0).min()
            calmar = abs(cagr / mdd) if (mdd < 0 and not pd.isna(cagr)) else np.nan
            return cagr, mdd, calmar
            
        c_s, m_s, cal_s = get_stat(sim_res['Strategy'])
        c_e, m_e, cal_e = get_stat(sim_res['EqualWeight'])
        c_b, m_b, cal_b = get_stat(sim_res['SPY'])
        
        win_r = (t_df['PnL'] > 0).mean() * 100.0 if not t_df.empty else 0.0
        pf = s_extra['gross_p'] / s_extra['gross_l'] if s_extra['gross_l'] > 0 else np.nan
        avg_exp = sim_res['Exposure'].mean() if 'Exposure' in sim_res.columns else 0.0
        avg_hold = t_df['HoldDays'].mean() if not t_df.empty else 0.0
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("전략 연평균 수익률 (CAGR)", f"{c_s:.1f}%", f"{c_s - c_b:+.1f}% vs SPY")
        m2.metric("최대 낙폭 (MDD)", f"{m_s:.1f}%", f"{abs(m_b) - abs(m_s):.1f}%p 방어", delta_color="normal")
        m3.metric("칼마 비율 (수익/위험)", f"{cal_s:.2f}", f"{cal_s - cal_b:+.2f} vs SPY")
        m4.metric("승률 (Win Rate)", f"{win_r:.1f}%", f"총 {len(t_df)}회 거래")
        
        # Pine Script v1.3 스타일 핵심 성과 요약 배너
        pf_str = f"{pf:.2f}" if not pd.isna(pf) else "-"
        st.markdown(f"""
        <div style="background:#f1f5f9; border-radius:8px; padding:10px 14px; margin-bottom:12px; font-size:0.9rem; color:#334155; border:1px solid #e2e8f0;">
            📊 <b>실전 통계:</b> 평균 투자비중 <b>{avg_exp:.0f}%</b> · 총 거래 <b>{len(t_df)}회</b> · 승률 <b>{win_r:.1f}%</b> · Profit Factor <b>{pf_str}</b> · 평균 보유일수 <b>{avg_hold:.0f}일</b>
        </div>
        """, unsafe_allow_html=True)
        
        # OOS 검증 기간 비교 (oos_year 설정 시)
        oos_yr = cfg.get('oos_year', 2020)
        if oos_yr > 0 and common_idx[-1].year >= oos_yr:
            oos_dt = pd.to_datetime(f"{oos_yr}-01-01")
            is_strat = sim_res['Strategy'].loc[sim_res.index < oos_dt]
            oos_strat = sim_res['Strategy'].loc[sim_res.index >= oos_dt]
            is_ew = sim_res['EqualWeight'].loc[sim_res.index < oos_dt]
            oos_ew = sim_res['EqualWeight'].loc[sim_res.index >= oos_dt]
            is_spy = sim_res['SPY'].loc[sim_res.index < oos_dt]
            oos_spy = sim_res['SPY'].loc[sim_res.index >= oos_dt]
            
            _, _, cal_is_s = get_stat(is_strat)
            c_oos_s, m_oos_s, cal_oos_s = get_stat(oos_strat)
            _, _, cal_is_e = get_stat(is_ew)
            c_oos_e, m_oos_e, cal_oos_e = get_stat(oos_ew)
            _, _, cal_is_b = get_stat(is_spy)
            c_oos_b, m_oos_b, cal_oos_b = get_stat(oos_spy)
            
            cmp_data = [
                {"지표": "CAGR (전체)", "전략": f"{c_s:+.1f}%", "동일비중(EW)": f"{c_e:+.1f}%", "SPY 지수": f"{c_b:+.1f}%"},
                {"지표": "MDD (최대낙폭)", "전략": f"{m_s:.1f}%", "동일비중(EW)": f"{m_e:.1f}%", "SPY 지수": f"{m_b:.1f}%"},
                {"지표": "Calmar (전체)", "전략": f"{cal_s:.2f}", "동일비중(EW)": f"{cal_e:.2f}", "SPY 지수": f"{cal_b:.2f}"},
                {"지표": f"Calmar IS (~{oos_yr-1}년)", "전략": f"{cal_is_s:.2f}" if not pd.isna(cal_is_s) else "-", "동일비중(EW)": f"{cal_is_e:.2f}" if not pd.isna(cal_is_e) else "-", "SPY 지수": f"{cal_is_b:.2f}" if not pd.isna(cal_is_b) else "-"},
                {"지표": f"Calmar OOS ({oos_yr}년~)", "전략": f"{cal_oos_s:.2f}" if not pd.isna(cal_oos_s) else "-", "동일비중(EW)": f"{cal_oos_e:.2f}" if not pd.isna(cal_oos_e) else "-", "SPY 지수": f"{cal_oos_b:.2f}" if not pd.isna(cal_oos_b) else "-"},
                {"지표": f"CAGR OOS ({oos_yr}년~)", "전략": f"{c_oos_s:+.1f}%" if not pd.isna(c_oos_s) else "-", "동일비중(EW)": f"{c_oos_e:+.1f}%" if not pd.isna(c_oos_e) else "-", "SPY 지수": f"{c_oos_b:+.1f}%" if not pd.isna(c_oos_b) else "-"},
                {"지표": f"MDD OOS ({oos_yr}년~)", "전략": f"{m_oos_s:.1f}%" if not pd.isna(m_oos_s) else "-", "동일비중(EW)": f"{m_oos_e:.1f}%" if not pd.isna(m_oos_e) else "-", "SPY 지수": f"{m_oos_b:.1f}%" if not pd.isna(m_oos_b) else "-"},
            ]
            st.dataframe(pd.DataFrame(cmp_data), use_container_width=True, hide_index=True)
            
        fig_s = go.Figure()
        fig_s.add_trace(go.Scatter(x=sim_res.index, y=sim_res['Strategy'], name='순환 스윙 전략', line=dict(color='#e11d48', width=2.5)))
        fig_s.add_trace(go.Scatter(x=sim_res.index, y=sim_res['EqualWeight'], name='바스켓 단순보유 (EW)', line=dict(color='#2563eb', width=1.5)))
        fig_s.add_trace(go.Scatter(x=sim_res.index, y=sim_res['SPY'], name='S&P 500 (SPY)', line=dict(color='#94a3b8', width=1.2, dash='dot')))
        fig_s.update_layout(title="자산 성장 곡선 (시작=100)", template="plotly_white", hovermode="x unified", height=450)
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("백테스트 데이터가 부족합니다.")

# --- [탭 5] 매크로 자산 비교 ---
@st.cache_data(ttl=1800)
def fetch_macro_comparison_data(period_str):
    tickers = ["^KS11", "SPY", "QQQ", "GLD", "BTC-USD", "KRW=X"]
    return yf.download(tickers, period=period_str, progress=False, group_by='ticker', auto_adjust=True)

with tab_macro:
    m_head1, m_head2 = st.columns([5, 1])
    with m_head1:
        st.subheader("🌍 주요 글로벌 자산 vs 현금/예금 종합 비교")
        st.caption("주식·비트코인·금 등 위험 자산의 성과를 '순수 현금 보유(0%)' 및 '은행 정기예금 복리 이자'와 객관적으로 비교 검증합니다.")
    with m_head2:
        with st.popover("❓ 매크로 & 현금/예금 비교 가이드"):
            st.markdown("""
            **🌍 왜 현금 보유 및 은행 예금과 비교해야 할까요?**
            - **1) 무위험 수익률(은행 예금) 초과 여부:**  
              투자에서 가장 중요한 원칙은 *"내가 감수한 위험에 걸맞은 초과 수익(Risk Premium)을 얻었는가?"* 입니다. 1년 동안 마음 졸이며 투자한 결과가 안전한 은행 정기예금(연 3.5%)보다 낮다면, 차라리 은행에 넣어두는 것이 더 유리했던 셈입니다.
            - **2) 순수 현금 보유 (0% 수익률)의 함정:**  
              "주식을 안 사고 가만히 있으면 본전"이라고 생각하기 쉽지만, 연 2~3%대의 인플레이션(물가상승)으로 인해 현금의 실질 구매력은 매년 조용히 깎여나가는 **'조용한 실질 손실'**을 입게 됩니다.
            - **3) 하락장에서의 현금의 위력:**  
              하지만 시장이 폭락할 때는 현금(0%)이 최고의 자산이 됩니다. 주식이 -30% 깨질 때 현금을 쥐고 있으면 엄청난 초과 성과를 내며 바닥에서 헐값에 주식을 담을 수 있습니다.
            """)
            
    # 상단 컨트롤 바 (기간 선택 & 은행 예금 금리 설정)
    col_m_per, col_m_rate = st.columns([1, 1])
    with col_m_per:
        period_map = {
            "최근 1년 (권장)": "1y",
            "최근 6개월": "6mo",
            "최근 3년": "3y",
            "최근 5년": "5y"
        }
        sel_period_label = st.selectbox("📅 비교 분석 기간", list(period_map.keys()), index=0, help="분석할 기간을 선택하세요.")
        period_val = period_map[sel_period_label]
        
    with col_m_rate:
        deposit_rate = st.number_input(
            "🏦 비교할 은행 예금 금리 (연 %)",
            min_value=0.5, max_value=15.0, value=3.5, step=0.1,
            help="현재 시중 정기예금 또는 파킹통장의 연이율을 입력하세요 (기본값: 연 3.5%)."
        )

    macro_meta = {
        "코스피 (KOSPI)": {"ticker": "^KS11", "color": "#e11d48"},
        "S&P 500": {"ticker": "SPY", "color": "#3b82f6"},
        "나스닥 100": {"ticker": "QQQ", "color": "#8b5cf6"},
        "금 (Gold)": {"ticker": "GLD", "color": "#eab308"},
        "비트코인": {"ticker": "BTC-USD", "color": "#f97316"},
        "원/달러 환율": {"ticker": "KRW=X", "color": "#06b6d4"}
    }
    
    with st.spinner("글로벌 거시경제 및 예금/현금 데이터 동기화 중..."):
        m_raw = fetch_macro_comparison_data(period_val)
        
    # 날짜 기준점 잡기 (SPY 또는 가용 자산 기준)
    ref_t = "SPY" if "SPY" in m_raw.columns.levels[0] else list(m_raw.columns.levels[0])[0]
    ref_s = m_raw[ref_t]['Close'].dropna()
    dates = ref_s.index
    
    if len(dates) >= 2:
        d_start, d_end = dates[0], dates[-1]
        total_days = max(1, (d_end - d_start).days)
        
        # 은행 예금 누적 수익률 계산 (일 복리 연환산)
        dep_cum_ret = ((1.0 + deposit_rate / 100.0) ** (total_days / 365.25) - 1.0) * 100.0
        
        # 자산별 수익률 데이터 수집
        score_list = []
        for lbl, meta in macro_meta.items():
            t = meta["ticker"]
            if t in m_raw.columns.levels[0]:
                sub_c = m_raw[t]['Close'].dropna()
                if len(sub_c) >= 2:
                    ret = (sub_c.iloc[-1] / sub_c.iloc[0] - 1.0) * 100.0
                    score_list.append({
                        "name": lbl, "ret": ret, "sub_c": sub_c,
                        "color": meta["color"], "type": "asset"
                    })
        
        score_list_sorted = sorted(score_list, key=lambda x: x['ret'], reverse=True)
        best_asset = score_list_sorted[0] if score_list_sorted else None
        worst_asset = score_list_sorted[-1] if score_list_sorted else None
        
        # 1. 상단 4단 요약 메트릭 카드 (모바일 2x2 반응형 그리드)
        c3_html = ""
        if best_asset:
            diff_dep = best_asset['ret'] - dep_cum_ret
            diff_color = "#e11d48" if diff_dep >= 0 else "#2563eb"
            c3_html = f"""
            <div style="background-color: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 0.78rem; color: #9f1239; font-weight: 600;">🏆 최고 수익 자산</span><br/>
                <span style="font-size: 1.2rem; color: #e11d48; font-weight: 700;">{best_asset['name'].split()[0]} {best_asset['ret']:+.1f}%</span><br/>
                <span style="font-size: 0.72rem; color: {diff_color};">예금 대비 {diff_dep:+.1f}%p</span>
            </div>
            """
        c4_html = ""
        if worst_asset:
            diff_dep_w = worst_asset['ret'] - dep_cum_ret
            diff_color_w = "#e11d48" if diff_dep_w >= 0 else "#2563eb"
            c4_html = f"""
            <div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 0.78rem; color: #1e40af; font-weight: 600;">🧊 최저 성과 자산</span><br/>
                <span style="font-size: 1.2rem; color: #2563eb; font-weight: 700;">{worst_asset['name'].split()[0]} {worst_asset['ret']:+.1f}%</span><br/>
                <span style="font-size: 0.72rem; color: {diff_color_w};">예금 대비 {diff_dep_w:+.1f}%p</span>
            </div>
            """
            
        grid_cards_html = f"""
        <div class="macro-4card-grid">
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 0.78rem; color: #166534; font-weight: 600;">🏦 은행 정기예금 (기준)</span><br/>
                <span style="font-size: 1.2rem; color: #15803d; font-weight: 700;">+{dep_cum_ret:.2f}%</span><br/>
                <span style="font-size: 0.72rem; color: #166534;">연 {deposit_rate}% 복리</span>
            </div>
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; text-align: center;">
                <span style="font-size: 0.78rem; color: #475569; font-weight: 600;">💵 순수 현금 보유</span><br/>
                <span style="font-size: 1.2rem; color: #64748b; font-weight: 700;">0.00%</span><br/>
                <span style="font-size: 0.72rem; color: #94a3b8;">물가 감안 실질 손실</span>
            </div>
            {c3_html}
            {c4_html}
        </div>
        """
        render_html(grid_cards_html)
                
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        
        # 2. 메인 비교 차트 (시작=100)
        fig_m = go.Figure()
        
        # 현금 보유 (0%) - 차분한 회색 점선
        fig_m.add_trace(go.Scatter(
            x=dates, y=[100.0] * len(dates),
            name="💵 순수 현금 보유 (0.0%)",
            line=dict(color="#64748b", width=2.0, dash="dash"),
            hovertemplate="💵 순수 현금: 100.0 (수익률 0.0%)<extra></extra>"
        ))
        
        # 은행 정기예금 - 든든한 녹색 실선
        dep_curve = [100.0 * ((1.0 + deposit_rate / 100.0) ** ((d - d_start).days / 365.25)) for d in dates]
        fig_m.add_trace(go.Scatter(
            x=dates, y=dep_curve,
            name=f"🏦 은행 정기예금 (연 {deposit_rate}%)",
            line=dict(color="#10b981", width=2.6),
            hovertemplate=f"🏦 은행 예금: %{{y:.2f}} (누적 +{dep_cum_ret:.1f}%)<extra></extra>"
        ))
        
        # 글로벌 자산들
        for item in score_list:
            sub_c = item['sub_c']
            norm = sub_c / sub_c.iloc[0] * 100.0
            fig_m.add_trace(go.Scatter(
                x=norm.index, y=norm,
                name=item['name'],
                line=dict(color=item['color'], width=1.8),
                hovertemplate=f"<b>{item['name']}</b>: %{{y:.2f}} ({item['ret']:+.1f}%)<extra></extra>"
            ))
            
        fig_m.update_layout(
            title=f"<b>글로벌 주요 자산 vs 현금/은행예금 성장 곡선 ({sel_period_label}, 시작=100)</b>",
            template="plotly_white",
            hovermode="x unified",
            height=420,
            yaxis_title="자산 가치 (기준점 = 100)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_m, use_container_width=True)
        
        # 3. 자산별 수익률 성적표 & 현금/예금 대비 성과 테이블
        st.markdown("#### 📋 자산별 수익률 성적표 & 현금/예금 대비 성과 비교")
        
        all_items = []
        for item in score_list:
            all_items.append({"name": item['name'], "ret": item['ret'], "type": "asset"})
        all_items.append({"name": f"🏦 은행 정기예금 (연 {deposit_rate}%)", "ret": dep_cum_ret, "type": "deposit"})
        all_items.append({"name": "💵 순수 현금 보유", "ret": 0.0, "type": "cash"})
        
        all_items_sorted = sorted(all_items, key=lambda x: x['ret'], reverse=True)
        
        tbl_rows = []
        for rank, it in enumerate(all_items_sorted, 1):
            r_val = it['ret']
            vs_dep = r_val - dep_cum_ret
            vs_cash = r_val
            
            if it['type'] == 'deposit':
                status = "🛡️ 무위험 원금 보장 (투자 기준점)"
                bg_style = "background-color: #f0fdf4;"
            elif it['type'] == 'cash':
                status = "⏳ 물가상승 실질 손실 (구매력 하락)"
                bg_style = "background-color: #f8fafc;"
            elif r_val >= dep_cum_ret + 10.0:
                status = "🔥 초과 달성 (위험 프리미엄 극대화)"
                bg_style = "background-color: #fff1f2;"
            elif r_val >= dep_cum_ret:
                status = "✨ 예금 초과 달성 (투자 성공)"
                bg_style = "background-color: #fff1f2;"
            elif r_val >= 0.0:
                status = "⚠️ 예금 미달 (예금 넣는 게 더 이득)"
                bg_style = "background-color: #fffbeb;"
            else:
                status = "🧊 원금 손실 (투자 실패 구간)"
                bg_style = "background-color: #eff6ff;"
                
            ret_color = "#e11d48" if r_val > 0 else ("#2563eb" if r_val < 0 else "#64748b")
            dep_color = "#e11d48" if vs_dep > 0 else ("#2563eb" if vs_dep < 0 else "#64748b")
            cash_color = "#e11d48" if vs_cash > 0 else ("#2563eb" if vs_cash < 0 else "#64748b")
            
            tbl_rows.append(f"""
            <tr style="{bg_style} border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 10px; font-weight: 600; text-align: center;">{rank}</td>
                <td style="padding: 10px; font-weight: 700;">{it['name']}</td>
                <td style="padding: 10px; font-weight: 700; color: {ret_color}; text-align: right;">{r_val:+.2f}%</td>
                <td style="padding: 10px; font-weight: 600; color: {dep_color}; text-align: right;">{vs_dep:+.2f}%p</td>
                <td style="padding: 10px; font-weight: 600; color: {cash_color}; text-align: right;">{vs_cash:+.2f}%p</td>
                <td style="padding: 10px; font-size: 0.88rem;">{status}</td>
            </tr>
            """)
            
        table_html = f"""
        <div style="overflow-x: auto; border: 1px solid #cbd5e1; border-radius: 8px;">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.92rem; text-align: left;">
                <thead>
                    <tr style="background-color: #f1f5f9; border-bottom: 2px solid #cbd5e1; color: #334155;">
                        <th style="padding: 10px; text-align: center; width: 60px;">순위</th>
                        <th style="padding: 10px;">자산명</th>
                        <th style="padding: 10px; text-align: right;">기간 누적 수익률</th>
                        <th style="padding: 10px; text-align: right;">🏦 은행예금 대비</th>
                        <th style="padding: 10px; text-align: right;">💵 현금보유 대비</th>
                        <th style="padding: 10px;">투자 가치 진단</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(tbl_rows)}
                </tbody>
            </table>
        </div>
        """
        render_html(table_html)
        
        st.markdown(f"""
        > 💡 **실전 투자 교훈 & 인사이트:**
        > - **은행 예금({deposit_rate}%)은 투자의 절대적 마지노선입니다.** 위험을 짊어지고 주식을 매매했는데 예금 이자보다 낮다면 포트폴리오를 점검해야 합니다.
        > - **현금(0%)은 상승장에서는 소외되지만, 하락장에서는 가장 강력한 무기입니다.** 우리 시스템의 전략이 '약세 국면'에서 현금 비중을 늘리는 이유가 바로 여기에 있습니다.
        """)
    else:
        st.info("매크로 데이터를 불러오는 중입니다. 잠시 후 다시 시도해주세요.")

# --- [탭 6] 설정 & 전략 커스텀 (한글 입력 지원!) ---
with tab_settings:
    s_head1, s_head2 = st.columns([5, 1])
    with s_head1:
        st.subheader("⚙️ 포트폴리오 & 전략 설정 센터")
        st.caption("여기서 종목을 추가(한글/티커 둘 다 가능)하거나, 전략 규칙과 파라미터를 마음대로 바꿀 수 있습니다.")
    with s_head2:
        with st.popover("❓ 전략 설정 튜닝 팁"):
            st.markdown("""
            **⚙️ 나만의 전략 최적화 가이드:**
            - **동시 보유 슬롯 (K):** 보통 3~5개가 적당합니다.
            - **국면 SMA 기간:** 기본 200일선이 가장 클래식하고 안전합니다.
            - **종목 검색:** '엔비디아', '테슬라'처럼 한글로 입력해도 자동으로 티커(NVDA, TSLA)를 찾아줍니다.
            """)
            
    st.markdown("#### 1️⃣ 종목 바스켓 간편 관리 & 자동화")
    col_pre, col_add = st.columns([1, 1])
    with col_pre:
        st.markdown("**⚡ 추천 프리셋 한 번에 불러오기**")
        selected_preset = st.selectbox("프리셋 선택", list(PRESETS.keys()), index=0, help="미리 구성된 우량 바스켓을 불러옵니다.")
        if st.button("📥 선택한 프리셋으로 바스켓 교체하기", use_container_width=True, help="클릭 시 바스켓이 교체되고 즉시 하드디스크에 영구 저장됩니다."):
            st.session_state.basket = PRESETS[selected_preset]
            save_basket_to_disk(st.session_state.basket)
            st.success(f"'{selected_preset}' 목록으로 교체 및 영구 저장되었습니다!")
            st.rerun()
            
    with col_add:
        st.markdown("**🔍 종목 실시간 검색 & 자동완성 추가**")
        search_kw = st.text_input(
            "종목 이름 또는 티커 검색 (일부만 쳐보세요)",
            value="",
            placeholder="예: 엔비, 테슬, 일라이, 비만, 양자, NV, AAPL...",
            help="한글 초성이나 단어 일부만 입력해도 일치하는 종목이 실시간으로 검색됩니다."
        ).strip()
        
        # 1. 일치하는 종목 검색 (Fuzzy match in STOCK_META)
        matched_syms = []
        if search_kw:
            kw_low = search_kw.lower()
            for sym, meta in STOCK_META.items():
                kr_name = meta.get('kr', '')
                en_name = meta.get('en', '')
                if kw_low in sym.lower() or kw_low in kr_name.lower() or kw_low in en_name.lower():
                    matched_syms.append(sym)
                    
        # 2. 자동완성 미리보기 및 선택
        target_ticker = None
        if matched_syms:
            if len(matched_syms) <= 8:
                selected_pill = st.pills(
                    f"👇 일치하는 추천 종목 ({len(matched_syms)}건) 터치하여 선택:",
                    options=matched_syms,
                    format_func=get_stock_short_label,
                    default=matched_syms[0],
                    key="tab6_matched_pills"
                )
                target_ticker = selected_pill if selected_pill else matched_syms[0]
            else:
                cand_options = {get_stock_label(s): s for s in matched_syms}
                selected_cand_label = st.selectbox(
                    f"👇 일치하는 추천 종목 ({len(matched_syms)}건) 중 선택",
                    list(cand_options.keys()), index=0
                )
                target_ticker = cand_options[selected_cand_label]
            st.caption(f"✅ 선택된 종목: **{get_stock_label(target_ticker)}**")
        elif search_kw:
            target_ticker = resolve_ticker_input(search_kw)
            st.info(f"💡 등록 사전에 없는 종목입니다. 해외 티커 **'{target_ticker}'**(으)로 직접 추가됩니다.")
        else:
            all_sym_opts = {"(검색어를 입력하거나 전체 목록에서 선택하세요)": ""}
            for s in sorted(STOCK_META.keys()):
                all_sym_opts[get_stock_label(s)] = s
            quick_pick_label = st.selectbox(
                "또는 전체 인기 우량주(80여 개) 목록에서 선택",
                list(all_sym_opts.keys()), index=0
            )
            target_ticker = all_sym_opts[quick_pick_label]

        c_q, c_a, c_b = st.columns(3)
        with c_q:
            new_qty = st.number_input("내 보유 수량", min_value=0.0, value=0.0, step=1.0)
        with c_a:
            new_avg = st.number_input("내 평단가 ($)", min_value=0.0, value=0.0, step=0.1)
        with c_b:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            new_belief = st.checkbox("📌 신념 보유 (슬롯 미차감)", value=False, help="체크 시 장기 가치관으로 보유하는 종목으로 지정되어 시스템 스윙 슬롯을 차지하지 않습니다.")

        btn_enabled = bool(target_ticker)
        btn_text = f"➕ '{get_stock_short_label(target_ticker)}' 바스켓에 추가하기" if target_ticker else "➕ 종목을 먼저 선택해 주세요"
        
        if st.button(btn_text, type="primary", use_container_width=True, disabled=(not btn_enabled)):
            if target_ticker:
                existing = [x['symbol'] for x in st.session_state.basket]
                if target_ticker in existing:
                    st.warning(f"이미 바스켓에 존재하는 종목입니다: {get_stock_label(target_ticker)}")
                else:
                    st.session_state.basket.append({"symbol": target_ticker, "use": True, "qty": new_qty, "avg": new_avg, "belief": new_belief})
                    save_basket_to_disk(st.session_state.basket)
                    st.success(f"'{get_stock_label(target_ticker)}' 종목이 바스켓에 영구 추가되었습니다!")
                    st.rerun()

    st.markdown("---")
    st.markdown("**📂 증권사 엑셀/CSV 잔고 파일 업로드 (자동 입력)**")
    uploaded_file = st.file_uploader("티커, 수량, 평단가가 포함된 CSV 파일을 올리면 자동으로 등록됩니다.", type=['csv'])
    if uploaded_file is not None:
        try:
            up_df = pd.read_csv(uploaded_file)
            st.write("업로드된 파일 미리보기:", up_df.head())
            col_map_t = st.selectbox("종목 티커 컬럼 선택", up_df.columns)
            col_map_q = st.selectbox("수량 컬럼 선택", up_df.columns)
            col_map_a = st.selectbox("평단가 컬럼 선택", up_df.columns)
            if st.button("🔄 이 파일로 바스켓 자동 덮어쓰기"):
                new_b = []
                for _, r in up_df.iterrows():
                    new_b.append({"symbol": str(r[col_map_t]).strip().upper(), "use": True, "qty": float(r[col_map_q]), "avg": float(r[col_map_a]), "belief": False})
                st.session_state.basket = new_b
                save_basket_to_disk(st.session_state.basket)
                st.success("엑셀 파일이 성공적으로 영구 등록되었습니다!")
                st.rerun()
        except Exception as e:
            st.error(f"오류: {e}")

    st.markdown("---")
    st.markdown("**📝 현재 바스켓 목록 직접 편집**")
    b_df = pd.DataFrame(st.session_state.basket)
    b_df['회사명 (한글/영문)'] = b_df['symbol'].apply(get_stock_short_label)
    if 'belief' not in b_df.columns:
        b_df['belief'] = False
    cols_order = ['symbol', '회사명 (한글/영문)', 'use', 'belief', 'qty', 'avg']
    ed_df = st.data_editor(
        b_df[cols_order],
        column_config={
            "symbol": st.column_config.TextColumn("티커"),
            "회사명 (한글/영문)": st.column_config.TextColumn("회사명 (한글/영문)", disabled=True),
            "use": st.column_config.CheckboxColumn("활성화", default=True),
            "belief": st.column_config.CheckboxColumn("📌 신념 보유", default=False, help="신념 보유 종목은 시스템 슬롯을 차지하지 않으며, 붕괴선 이탈 시 '논리 점검'으로 표시됩니다."),
            "qty": st.column_config.NumberColumn("내 보유 수량", min_value=0.0),
            "avg": st.column_config.NumberColumn("평단가 ($)", min_value=0.0)
        },
        use_container_width=True, num_rows="dynamic", hide_index=True
    )
    if st.button("💾 테이블 변경사항 영구 저장하기", type="primary"):
        clean_records = []
        for r in ed_df.to_dict('records'):
            clean_records.append({
                "symbol": r['symbol'],
                "use": r.get('use', True),
                "belief": bool(r.get('belief', False)),
                "qty": float(r.get('qty', 0.0)),
                "avg": float(r.get('avg', 0.0))
            })
        st.session_state.basket = clean_records
        save_basket_to_disk(st.session_state.basket)
        st.success("✅ 브라우저를 새로고침하거나 껐다 켜도 유지되도록 안전하게 영구 저장되었습니다!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 2️⃣ 개인별 백테스트 전략 룰 & 파라미터 조절")
    cfg_col1, cfg_col2, cfg_col3 = st.columns(3)
    with cfg_col1:
        n_max_pos = st.number_input("동시 보유 슬롯 수 (K)", min_value=1, max_value=20, value=cfg['max_pos'])
        year_options = [2000, 2006, 2010, 2015, 2018, 2020]
        cur_yr = cfg.get('start_year', 2006)
        yr_idx = year_options.index(cur_yr) if cur_yr in year_options else 1
        n_start_year = st.selectbox("시뮬레이션 시작 연도", year_options, index=yr_idx)
        n_cost = st.number_input("거래 비용 (편도 %)", min_value=0.0, max_value=1.0, value=cfg['cost_pct'], step=0.01)
        n_acct = st.number_input("스윙 계좌 총액 ($)", min_value=0.0, value=float(cfg.get('acct_usd', 0.0)), step=1000.0, help="0이면 수량 미표시. 금액 입력 시 매수 후보에 슬롯 금액(총액/K) 기준 매수 예상 수량을 자동 표시합니다.")
    with cfg_col2:
        n_sma = st.number_input("국면 SMA 기간", value=cfg['sma_len'], min_value=50, max_value=300)
        n_slope = st.number_input("기울기 확인 기간 (일)", value=cfg['slope_len'], min_value=5, max_value=60)
        n_break = st.number_input("추세 붕괴 이탈폭 (%)", value=cfg['break_pct'], min_value=0.5, max_value=10.0, step=0.5)
        n_rank = st.selectbox("신호 동시 발생 시 우선순위", ["6개월 모멘텀", "12-1개월 모멘텀"], index=0 if cfg.get('rank_mode', '6개월 모멘텀') == "6개월 모멘텀" else 1)
    with cfg_col3:
        n_use_a = st.checkbox("신호 A: SMA 지지반등 사용", value=cfg['use_a'])
        n_supp = st.number_input("A 지지 근접 범위 (%)", value=cfg['support_pct'], min_value=1.0, max_value=8.0, step=0.5)
        n_use_b = st.checkbox("신호 B: EMA20 눌림 회복 사용", value=cfg['use_b'])
        n_use_c = st.checkbox("신호 C: MACD 골든크로스 사용", value=cfg['use_c'])
        n_oos = st.number_input("검증(OOS) 시작 연도 (0=끔)", min_value=0, max_value=2035, value=int(cfg.get('oos_year', 2020)))
        n_yield = st.number_input("대기 현금 이자 (연 %)", min_value=0.0, max_value=10.0, value=float(cfg.get('cash_yield', 0.0)), step=0.25)
        
    if st.button("🚀 전략 파라미터 적용 & 영구 저장", type="primary", use_container_width=True):
        st.session_state.settings = {
            "max_pos": n_max_pos, "start_year": n_start_year, "cost_pct": n_cost,
            "acct_usd": n_acct, "rank_mode": n_rank, "oos_year": n_oos, "cash_yield": n_yield,
            "sma_len": n_sma, "slope_len": n_slope, "break_pct": n_break,
            "support_pct": n_supp, "use_a": n_use_a, "use_b": n_use_b, "use_c": n_use_c,
            "use_deep": True, "deep_pct": 1.0, "use_vol_filt": True
        }
        save_settings_to_disk(st.session_state.settings)
        st.success("✅ 전략 설정이 컴퓨터에 안전하게 영구 저장되었습니다!")
        st.rerun()

# ===== 사이드바: 실전 현황판 매매 나침반 =====
st.sidebar.title("🏛️ Brothers Capital")
st.sidebar.caption("브라더스 캐피탈 실전 스윙 나침반 v1.3")

if st.sidebar.button("🔄 데이터 실시간 새로고침", use_container_width=True, help="야후 파이낸스에서 지금 이 순간의 최신 시세를 즉시 다시 긁어옵니다."):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Dr_Rotation v1.3 실전 루틴")

render_html("""
<div class="guide-box">
<b>⏰ 확인 시간: 매일 아침 7~9시</b><br>
미국 장 마감 후 사이트를 딱 1번 확인하고 오늘 밤 주문을 미리 결정합니다.
</div>

<div class="guide-box" style="border-left: 4px solid #16a34a;">
<b style="color:#15803d;">🟢 1. 매수 (신규 진입)</b><br>
- <b>조건:</b> 200일선 위 강세 + 신호(지지/눌림/골든) 감지<br>
- <b>행동:</b> 빈 슬롯이 있으면 <b>모멘텀 상위순 오늘 밤 시가 매수</b> 예약! (계좌 총액 기준 권장 수량 안내)
</div>

<div class="guide-box" style="border-left: 4px solid #dc2626;">
<b style="color:#b91c1c;">🔍 2. 논리 점검 (추세 붕괴)</b><br>
- <b>시스템 종목:</b> 2일 연속 붕괴선(-3%) 하회 시 <b>내일 시가 정리</b> (원칙 방패)<br>
- <b>신념 종목:</b> 기계적 손절 대신 <b>기업 펀더멘털 & 투자 아이디어 재점검</b>
</div>

<div class="guide-box" style="border-left: 4px solid #7c3aed;">
<b style="color:#6d28d9;">📌 3. 신념 보유 분리 관리</b><br>
- 구글, 버크셔, 노보 등 장기 가치주는 <b>스윙 슬롯(기본 4개)을 소모하지 않음</b><br>
- 스윙 자금과 장기 신념 자금을 완벽히 분리해 운용
</div>

<div class="guide-box" style="border-left: 4px solid #2563eb;">
<b style="color:#1d4ed8;">💼 4. 슬롯 자금 배분 원칙</b><br>
- 최대 <b>4종목 (슬롯당 1/4 균등)</b> 분산 스윙<br>
- 신호 동시 발생 시 <b>6개월 모멘텀 상위순</b> 자동 배분
</div>
""")
