from sqlalchemy.orm import Session
import random
import string
import validators
from typing import Optional, Dict, Any
from ..models.url import URL
from ..cache.redis_config import get_cache, set_cache

class URLService:
    def __init__(self, db: Session):
        self.db = db

    def create_random_code(self, length: int = 6) -> str:
        """Generate a random short code"""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def create_unique_code(self) -> str:
        """Generate a unique short code"""
        while True:
            code = self.create_random_code()
            if not self.db.query(URL).filter(URL.short_code == code).first():
                return code

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing trailing slash"""
        return url.rstrip('/')

    def create_short_url(self, original_url: str, base_url: str) -> Dict[str, str]:
        """Create a shortened URL"""
        if not validators.url(original_url):
            raise ValueError("Invalid URL format")

        original_url = self.normalize_url(original_url)
        base_url = self.normalize_url(base_url)

        cache_key = f"url:{original_url}"
        cached_url = get_cache(cache_key)
        if cached_url:
            return {
                "short_url": f"{base_url}/{cached_url['short_code']}",
                "original_url": cached_url['original_url']
            }

        db_url = self.db.query(URL).filter(URL.original_url == original_url).first()
        if db_url:
            # Cache the result
            set_cache(cache_key, {
                "short_code": db_url.short_code,
                "original_url": db_url.original_url
            })
            return {
                "short_url": f"{base_url}/{db_url.short_code}",
                "original_url": db_url.original_url
            }

        short_code = self.create_unique_code()
        db_url = URL(
            original_url=original_url,
            short_code=short_code,
            clicks=0  # Initialize click counter
        )
        self.db.add(db_url)
        self.db.commit()
        self.db.refresh(db_url)

        # Cache the URL
        set_cache(cache_key, {
            "short_code": short_code,
            "original_url": original_url
        })
        set_cache(f"code:{short_code}", {
            "original_url": original_url
        })

        return {
            "short_url": f"{base_url}/{short_code}",
            "original_url": original_url
        }

    def increment_clicks(self, short_code: str) -> None:
        """Increment click counter for a URL"""
        db_url = self.db.query(URL).filter(URL.short_code == short_code).first()
        if db_url:
            db_url.clicks += 1
            self.db.commit()
            # Invalidate stats cache
            cache_key = f"stats:{short_code}"
            set_cache(cache_key, None)

    def get_original_url(self, short_code: str) -> Optional[str]:
        """Get original URL and increment click count"""
        cache_key = f"code:{short_code}"
        cached_url = get_cache(cache_key)
        if cached_url:
            # Asynchronously update click count
            self.increment_clicks(short_code)
            return self.normalize_url(cached_url["original_url"])

        db_url = self.db.query(URL).filter(URL.short_code == short_code).first()
        if not db_url:
            return None

        set_cache(cache_key, {
            "original_url": db_url.original_url
        })

        self.increment_clicks(short_code)

        return self.normalize_url(db_url.original_url)

    def get_url_stats(self, short_code: str) -> Optional[Dict[str, Any]]:
        """Get URL statistics"""
        db_url = self.db.query(URL).filter(URL.short_code == short_code).first()
        if not db_url:
            return None

        stats = {
            "original_url": self.normalize_url(db_url.original_url),
            "short_code": db_url.short_code,
            "clicks": db_url.clicks or 0,  # Ensure clicks is never None
            "created_at": db_url.created_at
        }

        cache_key = f"stats:{short_code}"
        set_cache(cache_key, stats, ttl=300)

        return stats 