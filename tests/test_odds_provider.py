from sports_agent.odds_provider import probe_odds_api

class Response:
    status_code = 200
    def json(self):
        return [{"bookmakers": [{"key": "bet365"}, {"key": "fanduel"}]}]

def test_missing_secret():
    assert probe_odds_api(api_key="")["reason"] == "secret_not_configured"

def test_provider_connectivity_does_not_claim_verified_prices():
    def fake_get(url, params, timeout):
        assert params["markets"] == "h2h"
        assert timeout == 15
        return Response()
    result = probe_odds_api(api_key="dummy", get=fake_get)
    assert result["ok"]
    assert result["bet365_present"]
    assert result["prices_verified"] is False
