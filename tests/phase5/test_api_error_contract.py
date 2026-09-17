from api_server import app


def test_debug_endpoints_reject_empty_or_unextractable_traces():
    client = app.test_client()

    invalid_inputs = [
        {},
        {"events": []},
        {"steps": []},
        {"trajectory": []},
        {"unexpected": "structure"},
    ]

    for payload in invalid_inputs:
        for endpoint in ("/debug", "/api/v1/debug"):
            response = client.post(endpoint, json=payload)

            assert response.status_code == 400, (
                endpoint,
                payload,
                response.status_code,
                response.get_json(),
            )
            assert response.is_json
            assert response.get_json()


def test_debug_endpoints_accept_valid_generic_trace():
    client = app.test_client()

    payload = {
        "events": [{
            "id": "e1",
            "event_type": "THOUGHT",
            "content": "test",
        }]
    }

    for endpoint in ("/debug", "/api/v1/debug"):
        response = client.post(endpoint, json=payload)

        assert response.status_code == 200, (
            endpoint,
            response.get_json(),
        )
        assert response.is_json
        assert response.get_json()["status"] == "success"
