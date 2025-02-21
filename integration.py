from fastapi import Request


@telex_router.get("/integration.json")
def get_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "descriptions": {
                "app_name": "Server file Monitor",
                "app_description": "Monitors files in a server",
                "app_url": base_url,
                "app_logo": "https://i.imgur.com/lZqvffp.png",
                "background_color": "#fff"
            },
            "integration_type": "interval",
            "integration_category": "Monitoring and logging",
            "key_features": [
            "\"checks server file deletions\""
            ],
            "settings": [
                {"label": "site-1", "type": "text", "required": True, "default": ""},
                {"label": "site-2", "type": "text", "required": True, "default": ""},
                {"label": "interval", "type": "text", "required": True, "default": "* * * * *"}
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": f"{base_url}"
        }
    }

@telex_router.get("/get_modifier_integration_json")
async def get_modifier_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "descriptions": {
                "app_name": "Word modifier",
                "app_description": "Modifies words",
                "app_url": base_url,
                "app_logo": "https://media.tifi.tv/telexbucket/public/logos/formatter.png",
                "background_color": "#fffddd"
            },
            "integration_type": "modifier",
            "integration_category": " Communication & Collaboration",
            "key_features": [
			"Receive messages from Telex channels.",
			"Format messages based on predefined templates or logic.",
			"Send formatted responses back to the channel.",
			"Log message formatting activity for auditing purposes."
            ],
            "permissions": {
                "events": [
                    "Receive messages from Telex channels.",
                    "Format messages based on predefined templates or logic.",
                    "Send formatted responses back to the channel.",
                    "Log message formatting activity for auditing purposes."
                ]
            },
            "settings": [
                {
                    "default": 100,
                    "label": "maxMessageLength",
                    "required": True,
                    "type": "number"
                },
                {
                    "default": "world,happy",
                    "label": "repeatWords",
                    "required": True,
                    "type": "multi-select"
                },
                {
                    "default": 2,
                    "label": "noOfRepetitions",
                    "required": True,
                    "type": "number"
                }
            ],
            "target_url": f"{base_url}/format_message",
            "tick_url": f"{base_url}/format_message",
        }
    }

@telex_router.get("/integration_error_logger.json")
def get_error_integration_json(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return {
        "data": {
            "descriptions": {
                "app_name": "Error logger",
                "app_description": "Checks out error logs and forwards to channels",
                "app_url": base_url,
                "app_logo": "https://i.imgur.com/lZqvffp.png",
                "background_color": "#fff"
            },
            "integration_type": "interval",
            "integration_category": "Error logging",
            "key_features": [
            "\"sends in errors\""
            ],
            "settings": [
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": f"{base_url}"
        }
    }

