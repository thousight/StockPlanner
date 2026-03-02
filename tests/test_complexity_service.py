from src.services.complexity import evaluate_complexity, requires_interrupt

def test_complexity_scoring():
    # Simple text
    easy_text = "The cat sat on the mat."
    score1 = evaluate_complexity(easy_text)
    print(f"Easy text: '{easy_text}' -> Score: {score1}, Interrupt: {requires_interrupt(score1)}")

    # Complex text (sampled from something harder)
    hard_text = "The implementation of the agentic orchestration flow requires an intricate understanding of LangGraph's asynchronous execution model and the persistence layers involved in state management."
    score2 = evaluate_complexity(hard_text)
    print(f"Hard text: '{hard_text}' -> Score: {score2}, Interrupt: {requires_interrupt(score2)}")

    # Action keyword (BUY)
    buy_text = "I recommend you to BUY this stock."
    score3 = evaluate_complexity(buy_text)
    print(f"Action keyword text: '{buy_text}' -> Score: {score3}, Interrupt: {requires_interrupt(score3)}")

    # Action keyword (SELL)
    sell_text = "It's time to SELL your positions."
    score4 = evaluate_complexity(sell_text)
    print(f"Action keyword text: '{sell_text}' -> Score: {score4}, Interrupt: {requires_interrupt(score4)}")

    # Action keyword (TRADE)
    trade_text = "We should TRADE some options."
    score5 = evaluate_complexity(trade_text)
    print(f"Action keyword text: '{trade_text}' -> Score: {score5}, Interrupt: {requires_interrupt(score5)}")

    # Action keyword (INVEST)
    invest_text = "You should INVEST in this fund."
    score6 = evaluate_complexity(invest_text)
    print(f"Action keyword text: '{invest_text}' -> Score: {score6}, Interrupt: {requires_interrupt(score6)}")

if __name__ == "__main__":
    test_complexity_scoring()
