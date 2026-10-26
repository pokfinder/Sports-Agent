from sports_agent.market_research import research_moneylines

def event():
    return {"id":"e1","home_team":"Home","away_team":"Away","bookmakers":[
        {"key":"a","markets":[{"key":"h2h","outcomes":[{"name":"Home","price":130},{"name":"Away","price":-150}]}]},
        *[{"key":name,"markets":[{"key":"h2h","outcomes":[{"name":"Home","price":-110},{"name":"Away","price":-110}]}]}
          for name in ("b","c","d")] ]}

def test_best_price_ranked_without_self_reference():
    results=research_moneylines([event()])
    home=next(x for x in results if x["sportsbook"]=="a" and x["selection"]=="Home")
    assert home["peer_book_count"]==3
    assert home["peer_no_vig_probability"]==0.5
    assert home["market_implied_ev"]==0.15
    assert home["status"]=="research_only"

def test_insufficient_independent_books():
    e=event()
    e["bookmakers"]=e["bookmakers"][:3]
    assert research_moneylines([e])==[]

def test_mismatched_and_bad_market_rejected():
    e=event()
    e["bookmakers"][0]["markets"][0]["outcomes"][0]["name"]="Wrong"
    assert all(x["sportsbook"]!="a" for x in research_moneylines([e]))
