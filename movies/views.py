import time
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Movie, Genre, MovieNation

def movie_search(request):
    start_time = time.time()  # 시작 시간 측정
    
    movies = Movie.objects.all()
    q = request.GET.get('q', '')
    director = request.GET.get('director', '')
    genre = request.GET.get('genre', '')
    year_start = request.GET.get('year_start', '')
    year_end = request.GET.get('year_end', '')
    movie_state = request.GET.get('movie_state', '')
    movie_type = request.GET.get('movie_type', '')
    nation = request.GET.get('nation', '')
    index = request.GET.get('index', '')

    # DB에서 실제 데이터 목록 가져오기 (None 값 필터링)
    available_types = list(Movie.objects.values_list('movie_type', flat=True).distinct().exclude(movie_type__isnull=True).exclude(movie_type=''))
    
    # 제작상태에서 None 값을 완전히 제거 - 더 강력한 필터링
    all_states = Movie.objects.values_list('movie_state', flat=True).distinct()
    available_states = [state for state in all_states if state and state != 'None' and str(state).strip() != 'None']
    
    available_genres = list(Genre.objects.values_list('genre', flat=True).distinct().exclude(genre__isnull=True).exclude(genre=''))
    available_nations = list(MovieNation.objects.values_list('nation', flat=True).distinct().exclude(nation__isnull=True).exclude(nation=''))
    
    # 필터링 로직
    if q:
        from django.db.models import Q
        movies = movies.filter(
            Q(movie_name__icontains=q) | 
            Q(movie_engname__icontains=q)
        )
    if director:
        movies = movies.filter(castings__director__dname__icontains=director)
    if genre:
        genre_list = [g.strip() for g in genre.split(',') if g.strip()]
        movies = movies.filter(genres__genre__in=genre_list)
    if year_start:
        movies = movies.filter(create_year__gte=year_start)
    if year_end:
        movies = movies.filter(create_year__lte=year_end)
    if movie_state:
        state_list = [s.strip() for s in movie_state.split(',') if s.strip()]
        movies = movies.filter(movie_state__in=state_list)
    if movie_type:
        type_list = [t.strip() for t in movie_type.split(',') if t.strip()]
        movies = movies.filter(movie_type__in=type_list)
    if nation:
        nation_list = [n.strip() for n in nation.split(',') if n.strip()]
        movies = movies.filter(nations__nation__in=nation_list)
    
    # 영화명 인덱싱 - 수정된 부분
    if index:
        from django.db.models import Q
        if index in "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ":
            start, end = get_chosung_range(index)
            movies = movies.filter(movie_name__gte=start, movie_name__lt=end)
        elif index in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            # 영어 인덱싱 - 영화명만 검색
            movies = movies.filter(movie_name__istartswith=index)

    movies = movies.distinct()
    
    # 페이지네이션
    total_count = movies.count()
    paginator = Paginator(movies, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 결과에서도 None 값을 빈 문자열로 처리
    for movie in page_obj:
        if movie.movie_state is None or movie.movie_state == 'None':
            movie.movie_state = ''
    
    list(page_obj)
    
    end_time = time.time()
    query_time = round((end_time - start_time) * 1000, 2)

    context = {
        'results': page_obj,
        'page_obj': page_obj,
        'query': q,
        'director': director,
        'genre': genre,
        'year_start': year_start,
        'year_end': year_end,
        'movie_state': movie_state,
        'movie_type': movie_type,
        'nation': nation,
        'index': index,
        'year_range': range(1900, 2030),
        'available_types': available_types,
        'available_states': available_states,
        'available_genres': available_genres,
        'available_nations': available_nations,
        'query_time': query_time,
    }
    return render(request, 'movies/movie_search.html', context)

def get_chosung_range(chosung):
    # 초성별 범위 매핑
    chosung_ranges = {
        'ㄱ': ('가', '나'),
        'ㄴ': ('나', '다'),
        'ㄷ': ('다', '라'),
        'ㄹ': ('라', '마'),
        'ㅁ': ('마', '바'),
        'ㅂ': ('바', '사'),
        'ㅅ': ('사', '아'),
        'ㅇ': ('아', '자'),
        'ㅈ': ('자', '차'),
        'ㅊ': ('차', '카'),
        'ㅋ': ('카', '타'),
        'ㅌ': ('타', '파'),
        'ㅍ': ('파', '하'),
        'ㅎ': ('하', '힣'),
    }
    return chosung_ranges.get(chosung, ('', ''))
