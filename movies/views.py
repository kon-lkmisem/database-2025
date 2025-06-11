import time
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
from django.conf import settings
from .models import Movie, Genre, MovieNation

def movie_search(request):
    start_time = time.time()
    
    # DEBUG 모드에서만 쿼리 추적
    if settings.DEBUG:
        initial_queries = len(connection.queries)
    else:
        initial_queries = 0
    
    movies = Movie.objects.all()
    q = request.GET.get('q', '')
    use_match = request.GET.get('use_match', 'true').lower()  # 기본값은 True로 설정
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
        if use_match == 'true': # Match 사용
            movies = movies.extra(
                where=["MATCH(movie_name) AGAINST(%s IN NATURAL LANGUAGE MODE)"],
                params=[q]
            )
        else: # like 사용
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
    
    # 영화명 인덱싱
    if index:
        if index in "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ":
            start, end = get_chosung_range(index)
            movies = movies.filter(movie_name__gte=start, movie_name__lt=end)
        elif index in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
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
    
    # 페이지 객체를 실제로 평가하여 쿼리 실행
    list(page_obj)
    
    end_time = time.time()
    query_time = round((end_time - start_time) * 1000, 2)
    
    # 쿼리 정보 수집 (DEBUG 모드에서만)
    query_info = []
    total_db_time = 0
    query_count = 0
    
    if settings.DEBUG and hasattr(connection, 'queries'):
        try:
            executed_queries = connection.queries[initial_queries:]
            query_count = len(executed_queries)
            
            for i, query in enumerate(executed_queries, 1):
                query_time_ms = float(query.get('time', 0)) * 1000
                total_db_time += query_time_ms
                query_info.append({
                    'number': i,
                    'sql': query.get('sql', 'N/A'),
                    'time': round(query_time_ms, 2)
                })
        except Exception as e:
            # 에러가 발생하면 기본값 사용
            query_info = [{'number': 1, 'sql': f'쿼리 수집 중 오류: {str(e)}', 'time': 0}]
            total_db_time = 0
            query_count = 0

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
        'query_info': query_info,
        'query_count': query_count,
        'total_db_time': round(total_db_time, 2),
    }
    return render(request, 'movies/movie_search.html', context)

def get_chosung_range(chosung):
    """
    초성에 해당하는 정확한 유니코드 범위를 계산하여 반환
    """
    # 초성 리스트 (ㄱ~ㅎ)
    chosung_list = ['ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    
    if chosung not in chosung_list:
        return ('', '')
    
    # 초성의 인덱스
    chosung_index = chosung_list.index(chosung)
    
    # 한글 유니코드 시작점 (가 = 0xAC00)
    hangul_start = 0xAC00
    
    # 각 초성마다 588개의 글자 (중성 21개 × 종성 28개)
    chars_per_chosung = 588
    
    # 해당 초성의 시작과 끝
    start_code = hangul_start + (chosung_index * chars_per_chosung)
    end_code = start_code + chars_per_chosung
    
    return (chr(start_code), chr(end_code))