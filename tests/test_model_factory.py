from models import MockModel, create_model


def test_create_mock_model():
    model = create_model(
        {
            "provider": "mock",
            "model": "deterministic-mock",
        }
    )

    assert isinstance(model, MockModel)
