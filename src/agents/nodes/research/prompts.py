from langchain_core.prompts import ChatPromptTemplate

ARTICLE_SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
Summarize the key financial insights from the following article. 
Focus on information relevant to stock analysis, market trends, and economic indicators.
Keep the summary concise (2-3 sentences).

Article Content:
{content}
""")