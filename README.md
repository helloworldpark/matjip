# matjip
개발자가 삿포로에 갈 일이 있어 내친김에 해본 덕질

# 개요
누구나 맛집에 가고 싶어합니다. 그런데 맛집 사이트마다 맛집에 대한 평가가 다 다릅니다. 어디를, 무엇을 믿어야 할까요?
조만간 삿포로에 갈 일이 있는데, 대체 왜 타베로그에 올라온 식당들의 평점은 죄다 3점대일까요. 구글에 나와있는 평가와는 무슨 관련이 있을까요.
그게 너무 궁금해서 [타베로그](https://tabelog.com/)에 올라와 있는 정보를 크롤링하고, 구글에 올라와 있는 정보를 [Google Places API](https://developers.google.com/places/web-service/intro?hl=ko)로 불러오도록 작업해봤습니다.
그리고 그렇게 조금이나마 모아본 데이터를 활용해서 통계 분석도 약간 해보았습니다.
이 리포지토리가 [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)을 이용한 크롤러 제작에 도움이 되고, 
여러분들의 [Google Places API](https://developers.google.com/places/web-service/intro?hl=ko) 사용에 도움이 되었으면 좋겠습니다.

# 설치
## Pipenv로 설치하기(추천!)
```pipenv```를 사용할 수 있는 환경이라면
1. 이 리포지토리를 clone합니다
```git clone https://github.com/helloworldpark/matjip.git```
2. 클론한 위치로 이동 후 ```pipenv```로 간단하게 설치합니다
```
$ pipenv --python 3.7
$ pipenv install
```

## pip으로 직접 설치하기
```Pipfile```에 명세된 라이브러리들을 ```pip```으로 직접 설치해줍니다.

만일 해당 운영체제의 기본 파이썬 버전이 3점대라면:

> ```pip install numpy```

만일 해당 운영체제의 기본 파이선 버전이 2점대라면:

> ```pip3 install numpy```

## Anaconda로 설치하기
그냥 아나콘다에 맡겨버립니다.

# 라이센스
MIT 라이센스를 따릅니다.
