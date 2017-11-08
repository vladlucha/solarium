#!/bin/bash
cd /app && exec daphne -b 0.0.0.0 -p 8000 asgi:channel_layer
