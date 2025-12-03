from app.models import Metadata


def test_metadata_validation():
    payload = {
        "title": "My Edit",
        "overlays": [
            {
                "id": "overlay-1",
                "type": "text",
                "content": "Hello",
                "position": {"x": 0.5, "y": 0.5},
                "scale": 1.0,
                "rotation": 0,
                "opacity": 1.0,
                "start_time": 1.0,
                "end_time": 2.0,
                "z_index": 1,
            }
        ],
        "output_format": "mp4",
        "resolution": {"width": 1280, "height": 720},
    }
    meta = Metadata.model_validate(payload)
    assert meta.title == "My Edit"
    assert meta.overlays[0].type == "text"
