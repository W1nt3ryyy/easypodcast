from django.http import HttpResponse, JsonResponse


OPENAPI_SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "Easy Podcasts API",
        "version": "1.0.0",
        "description": "API for authentication, podcast catalog, subscriptions, RSS preview, episodes and listening progress.",
    },
    "servers": [{"url": "/"}],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        },
        "schemas": {
            "AuthPayload": {
                "type": "object",
                "required": ["username", "password"],
                "properties": {
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string", "format": "password"},
                },
            },
            "FeedInput": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {"type": "string", "format": "uri"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "image_url": {"type": "string", "format": "uri"},
                    "category": {"type": "string"},
                },
            },
            "Feed": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "url": {"type": "string", "format": "uri"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "image_url": {"type": "string", "format": "uri"},
                    "category": {"type": "string"},
                    "is_subscribed": {"type": "boolean"},
                },
            },
            "ProgressInput": {
                "type": "object",
                "required": ["episode_url"],
                "properties": {
                    "episode_url": {"type": "string", "format": "uri"},
                    "current_time": {"type": "number"},
                    "duration": {"type": "number"},
                    "episode_title": {"type": "string"},
                    "podcast_title": {"type": "string"},
                    "podcast_url": {"type": "string", "format": "uri"},
                    "image_url": {"type": "string", "format": "uri"},
                },
            },
        },
    },
    "paths": {
        "/api/podcasts/": {
            "get": {
                "summary": "List current user's subscribed podcasts",
                "security": [{"BearerAuth": []}],
                "parameters": [{"name": "category", "in": "query", "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Podcast list"}},
            }
        },
        "/api/podcasts/auth/register/": {
            "post": {
                "summary": "Create account",
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthPayload"}}}},
                "responses": {"200": {"description": "Token and user"}},
            }
        },
        "/api/podcasts/auth/login/": {
            "post": {
                "summary": "Login",
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthPayload"}}}},
                "responses": {"200": {"description": "Token and user"}},
            }
        },
        "/api/podcasts/auth/me/": {
            "get": {"summary": "Current user", "security": [{"BearerAuth": []}], "responses": {"200": {"description": "User"}}}
        },
        "/api/podcasts/auth/profile/": {
            "post": {
                "summary": "Update profile",
                "security": [{"BearerAuth": []}],
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthPayload"}}}},
                "responses": {"200": {"description": "Updated user"}},
            }
        },
        "/api/podcasts/add/": {
            "post": {
                "summary": "Add podcast to current user's subscriptions",
                "security": [{"BearerAuth": []}],
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/FeedInput"}}}},
                "responses": {"200": {"description": "Subscribed feed"}},
            }
        },
        "/api/podcasts/search/": {
            "get": {
                "summary": "Search podcast directory",
                "parameters": [{"name": "q", "in": "query", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Directory items"}},
            }
        },
        "/api/podcasts/popular/": {
            "get": {
                "summary": "Popular podcasts by genre",
                "parameters": [{"name": "genre", "in": "query", "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Directory items"}},
            }
        },
        "/api/podcasts/audio/": {
            "get": {
                "summary": "Proxy podcast audio through the backend",
                "parameters": [{"name": "url", "in": "query", "required": True, "schema": {"type": "string", "format": "uri"}}],
                "responses": {
                    "200": {"description": "Audio stream"},
                    "206": {"description": "Partial audio stream"},
                },
            }
        },
        "/api/podcasts/preview/": {
            "post": {
                "summary": "Preview RSS episodes without subscribing",
                "parameters": [
                    {"name": "offset", "in": "query", "schema": {"type": "integer"}},
                    {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                ],
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/FeedInput"}}}},
                "responses": {"200": {"description": "Feed preview"}},
            }
        },
        "/api/podcasts/{feed_id}/parse/": {
            "get": {
                "summary": "Get episodes for a subscribed feed",
                "parameters": [
                    {"name": "feed_id", "in": "path", "required": True, "schema": {"type": "integer"}},
                    {"name": "offset", "in": "query", "schema": {"type": "integer"}},
                    {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                ],
                "responses": {"200": {"description": "Episode page"}},
            }
        },
        "/api/podcasts/subscriptions/toggle/": {
            "post": {
                "summary": "Toggle subscription",
                "security": [{"BearerAuth": []}],
                "requestBody": {"content": {"application/json": {"schema": {"type": "object", "properties": {"feed_id": {"type": "integer"}}}}}},
                "responses": {"200": {"description": "Subscription state"}},
            }
        },
        "/api/podcasts/progress/": {
            "get": {
                "summary": "Get listening progress",
                "parameters": [{"name": "episode_url", "in": "query", "required": True, "schema": {"type": "string", "format": "uri"}}],
                "responses": {"200": {"description": "Progress"}},
            }
        },
        "/api/podcasts/progress/save/": {
            "post": {
                "summary": "Save listening progress",
                "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/ProgressInput"}}}},
                "responses": {"200": {"description": "Saved progress"}},
            }
        },
        "/api/podcasts/history/": {
            "get": {"summary": "Listening history", "security": [{"BearerAuth": []}], "responses": {"200": {"description": "History items"}}}
        },
    },
}


def schema(request):
    return JsonResponse(OPENAPI_SCHEMA)


def swagger_ui(request):
    html = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Easy Podcasts API Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>
      body { margin: 0; background: #f7f7f8; }
      .swagger-ui .topbar { display: none; }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: "/api/schema/",
        dom_id: "#swagger-ui",
        deepLinking: true,
        persistAuthorization: true
      });
    </script>
  </body>
</html>
"""
    return HttpResponse(html)
