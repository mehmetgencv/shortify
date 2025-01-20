# Shortify

A modern, high-performance URL shortening service built with FastAPI and Python. Shortify provides a robust API for creating, managing, and tracking shortened URLs with enterprise-grade features.

## ✨ Features

- 🔗 **URL Shortening**: Convert long URLs into concise, shareable links
- 📊 **Analytics**: Track clicks and usage statistics for each shortened URL
- 🚀 **High Performance**: Redis caching for optimal response times
- 🔄 **RESTful API**: Clean and well-documented API endpoints
- 📝 **OpenAPI/Swagger**: Interactive API documentation
- 🔒 **Data Integrity**: PostgreSQL for reliable data storage
- 🧪 **Test Coverage**: Comprehensive test suite with pytest
- 🐳 **Docker Ready**: Easy deployment with Docker and Docker Compose

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Testing**: pytest with mocking
- **Documentation**: OpenAPI/Swagger
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/mehmetgencv/shortify.git
cd shortify
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start services with Docker:
```bash
docker-compose up -d
```

4. Access the application:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

## 🔧 Local Development

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start dependencies:
```bash
docker-compose up -d postgres redis
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## 🧪 Testing

Run tests with pytest:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_url_service.py -v
```

## 📝 API Documentation

### Create Short URL
```http
POST /shorten
{
    "url": "https://example.com/very/long/url"
}
```

### Redirect to Original URL
```http
GET /{short_code}
```

### Get URL Statistics
```http
GET /url/{short_code}/stats
```

## 🏗️ Project Structure

```
shortify/
├── app/
│   ├── models/      # Database models
│   ├── schemas/     # Pydantic schemas
│   ├── services/    # Business logic
│   ├── database/    # Database config
│   ├── cache/       # Redis config
│   └── tests/       # Test suite
├── docker/          # Docker configuration
└── docs/           # Additional documentation
```

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_USER | Database username | postgres |
| POSTGRES_PASSWORD | Database password | postgres |
| POSTGRES_DB | Database name | url_shortener |
| REDIS_HOST | Redis host | localhost |
| REDIS_PORT | Redis port | 6379 |
| CACHE_TTL | Cache TTL (seconds) | 3600 |


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 