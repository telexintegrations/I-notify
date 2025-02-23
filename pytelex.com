curl --location 'https://telex-app.onrender.com/tick' --header 'Content-Type: application/json' --data '{
    "channel_id": "0195336b-936c-7c6e-b962-dd25d02c7aba",
    "return_url": "https://ping.telex.im/v1/webhooks/0195336b-936c-7c6e-b962-dd25d02c7aba",
    "settings": [
        {
            "label": "site",
            "type": "text",
            "required": true,
            "default": "https://telex-app.onrender.com/logs"
        },
        {
            "label": "interval",
            "type": "text",
            "required": true,
            "default": "* * * * *"
        }
    ]
}'
