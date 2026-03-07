import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import select
from langchain_openai import ChatOpenAI

from src.database.session import AsyncSessionLocal
from src.database.models import ResearchCache, ResearchSourceType
from src.services.market_data import get_historical_prices_async
from src.graph.utils.calendar import get_previous_trading_day
from src.graph.utils.agents import with_logging

class NarrativeShift(BaseModel):
    current_narrative: str = Field(description="Synthesis of today's market drivers")
    top_3_drivers: List[str] = Field(description="The three most significant factors moving the market today")
    sentiment_shift: str = Field(description="Description of how the narrative shifted from the previous session")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")

NARRATIVE_SHIFT_PROMPT = """
You are a senior market strategist. Synthesize the provided research data into a 'Growth Narrative'.

**Current Research Data (Price/Macro/News):**
{current_data}

**Previous Session Narrative (if available):**
{previous_narrative}

**Instructions:**
1. Identify the Top 3 Narrative Drivers from the current data.
2. If a previous narrative is provided, explicitly describe the shift (e.g., 'Pivot from inflation fears to growth optimism').
3. If no previous narrative is provided, focus on the current drivers and note 'No baseline available'.
4. Return a structured JSON response.
{subject_instruction}
"""

@with_logging
async def get_indices_performance(**kwargs) -> str:
    """
    Fetches the 5-day performance pulse for major indices (SPY, QQQ, DIA) and volatility (VIX).
    Useful for establishing broad market context.
    """
    tickers = ["SPY", "QQQ", "DIA", "^VIX"]
    price_tasks = [get_historical_prices_async(t, period="5d") for t in tickers]
    price_histories = await asyncio.gather(*price_tasks)
    
    current_prices = {}
    missing_tickers = []
    for i, symbol in enumerate(tickers):
        hist = price_histories[i]
        if not hist.empty and len(hist) > 1:
            last_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            current_prices[symbol] = f"{last_close:.2f} ({pct_change:+.2f}%)"
        else:
            missing_tickers.append(symbol)

    output = ["### Major Indices Pulse (5D)"]
    for s, v in current_prices.items():
        output.append(f"- **{s}**: {v}")
    
    if missing_tickers:
        output.append(f"\n**WARNING: Data missing for indices: {', '.join(missing_tickers)}**")
    
    return "\n".join(output) + "\n"

@with_logging
async def get_historical_narrative(subject: Optional[str] = None) -> str:
    """
    Retrieves the last known growth narrative for a subject from the cache (7-day lookback).
    Provides the baseline for identifying shifts.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    subject_slug = subject.replace(" ", "_") if subject else "broad_market"
    prev_trading_day = get_previous_trading_day(now)
    
    async with AsyncSessionLocal() as db:
        try:
            for i in range(1, 8):
                check_date = prev_trading_day - timedelta(days=i-1)
                prev_key = f"narrative_{subject_slug}_{check_date.strftime('%Y%m%d')}"
                stmt = select(ResearchCache).where(ResearchCache.key == prev_key)
                result = await db.execute(stmt)
                cached = result.scalar_one_or_none()
                if cached:
                    return f"### Previous Narrative for {subject or 'Broad Market'}\n{cached.content}\n"
        except Exception as e:
            # Log error and return missing data description
            print(f"[ERROR] Database failure retrieving previous narrative for {subject_slug}: {e}")
            return f"### Previous Narrative for {subject or 'Broad Market'}\n[DATA MISSING: Database error occurred while retrieving historical narrative]\n"
            
    return f"### Previous Narrative for {subject or 'Broad Market'}\n[DATA MISSING: No historical narrative found in cache for the last 7 days]\n"

@with_logging
async def synthesize_growth_narrative(
    research_context: Optional[str] = None, 
    subject: Optional[str] = None,
    **kwargs
) -> str:
    """
    Synthesizes multiple research data points (prices, news, previous narratives) 
    into a final Growth Narrative report and caches it.
    
    Args:
        research_context: Combined string of all data gathered (indices, news, history).
        subject: The specific entity or topic (optional).
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    # Fallback context
    context = research_context or ""
    
    # Try to infer subject if missing but provided in kwargs or context
    final_subject = subject
    if not final_subject:
        # Check if kwargs has it (sometimes passed by agent incorrectly)
        final_subject = kwargs.get("subject")
    
    subject_slug = final_subject.replace(" ", "_") if final_subject else "broad_market"
    today_key = f"narrative_{subject_slug}_{now.strftime('%Y%m%d')}"

    # Extract previous narrative if it was passed in the context
    prev_narrative = "Not provided in context."
    if "### Previous Narrative" in context:
        prev_narrative = context.split("### Previous Narrative")[1].split("###")[0].strip()

    # Analyze with LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(NarrativeShift)
    
    subject_instr = f"\nNote: The focus is specifically on the growth narrative of '{final_subject}'." if final_subject else ""
    
    shift_analysis = await structured_llm.ainvoke(
        NARRATIVE_SHIFT_PROMPT.format(
            current_data=context,
            previous_narrative=prev_narrative,
            subject_instruction=subject_instr
        )
    )

    # Cache result
    async with AsyncSessionLocal() as db:
        try:
            stmt = select(ResearchCache).where(ResearchCache.key == today_key)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            narrative_content = f"Drivers: {', '.join(shift_analysis.top_3_drivers)}\nSummary: {shift_analysis.current_narrative}"
            
            if existing:
                existing.content = narrative_content
                existing.expire_at = now + timedelta(days=1)
            else:
                new_cache = ResearchCache(
                    source_type=ResearchSourceType.NARRATIVE,
                    ticker=final_subject if (final_subject and len(final_subject) <= 5 and final_subject.isupper()) else None,
                    key=today_key,
                    content=narrative_content,
                    expire_at=now + timedelta(days=1)
                )
                db.add(new_cache)
            await db.commit()
        except Exception as e:
            print(f"Error caching narrative for {subject_slug}: {e}")

    # Format Output
    title = f"## Growth Narrative: {final_subject}" if final_subject else "## Market Narrative of the Day"
    output = [
        title,
        f"**Current Pulse:** {shift_analysis.current_narrative}",
        "\n### Top 3 Narrative Drivers:",
        "\n".join([f"{i+1}. {driver}" for i, driver in enumerate(shift_analysis.top_3_drivers)]),
        f"\n**Narrative Shift:** {shift_analysis.sentiment_shift}",
        f"\n*Confidence Score: {shift_analysis.confidence:.2f}*"
    ]
    
    return "\n".join(output) + "\n"
