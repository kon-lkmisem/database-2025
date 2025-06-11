FROM python:3.12

WORKDIR /app

# 시스템 의존성 설치 (MySQL 클라이언트 포함)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 정적 파일 수집
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Django 개발 서버 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]