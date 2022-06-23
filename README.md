### Тестовое задание для компании AEROSPACE AGRO
### Выполнил Артём Минин

### Текст задания:
Необходимо разработать веб-сервис, который будет выгружать космические снимки и определять NDVI на поле, предоставляя REST API.
### Стек
Python, Fast API
### Функционал
    1. Добавить и удалить сельхоз поле в формате GeoJSON
    2. Получение снимка поля по API поставщиков космических снимков
    3. Расчёт NDVI для сельхоз поля
    4. Получить изображение поля с NDVI
### Ресурсы
    • Космические снимки можно получать с помощью Python библиотеки sentinelsat (github.com/sentinelsat/sentinelsat) или Google Earth Engine API
    • NDVI, он же индекс вегетации, рассчитывается по формуле, используя разные каналы космического снимка
### Требования
    1. Выложить исходный код на GitHub
    2. Разместить backend на AWS
    3. Оформить REST API в Postman
### Отправка решений
Необходимо отправить своё решение, состоящие из ссылок на GitHub репозиторий, задеплоенный backend на AWS и файл коллекции Postman.

### Результат выполнения:
Задание выполнено частично. API работает. По запросу /footprints появляется предложение загрузить файл.
При прикреплении файла geoJson формируется запись в базу PosgreSQL.
Далее происходит запрос к API sentinel, получается список подходящих для данной локации спутниковых снимков.
Из этих снимков выбирается снимок с наименьшей облачностью и скачивается в хранилище.
Далее скаченный файл распаковывается и по его директориям проводится поиск нужных цветовых каналов.
По этим каналам далее строится изображение.
Проблема возникла с формированием корректного файла tiff и вырезанием из него нужной области (сельхоз поля),
что не позволяет далее получить снимок с NDVI.