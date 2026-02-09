from langchain_core.prompts import ChatPromptTemplate

ANALYST_PROMPT = ChatPromptTemplate.from_template("""
First, summarize and analyze the macro economic news of the day:
{macro_news}
    
Then, for each stock in the portfolio, analyze:
1. Valuation (PE ratio, comparison to sector if known)
2. Recent News Sentiment and how they can impact each stocks
3. Earnings Outlook (if data available)
4. Performance (Current Price vs Avg Cost)

Finally, provide a "Buy", "Sell", or "Hold" recommendation with reasoning.

Portfolio Data:
{portfolio}

Provide a comprehensive Markdown report.
""")