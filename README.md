#     Большая задача по Maps API.
#### Авторы решения: Аксенов Никита и Прохорова Анна
##    Особенности структуры проекта
В главной ветке репозитория `master` находятся файлы с решениями каждой из задач 1-12 названные
соответственно **`task_<номер_задачи>.py`**. Также здесь расположены иконки для кнопок интерфейса программы.
## Для запуска
Для запуска каждой из задач необходимо запустить соответствующий файл с решением **`task_<номер_задачи>.py`** Если задачи с таким
номером нет, то нужно выбрать задачу с номером больше него. Для проверки можно посмотреть на комментарий в начале кода. Там 
написан номер задачи. До запуска нужно убедиться, что в папке с этой программой находятся иконки **`plus.png, minus.png, layers.png`**.  Без
них кнопки увеличения и уменьшения масштаба, переключатель слоев карты корректно отображены не будут.

## Примечания по работе программы:
1. Перемещение карты с помощью клавиш *вверх/вниз/вправо/влево* сделать не
удалось из-за особенности работы PyQt5. Поэтому были использованы кнопки
*WASD (W - вверх, A - влево, S - вниз, D - вправо)*.
2. В задаче 12 поиск организаций удалось осуществить только по их адресу, получаемому
по координатам выбираемой точки. Напрямую получить все близлежащие организации через 
Yandex.Maps API не представилось возможным.
3. Корректность выбора точки на карте по клику мышью может меняться в зависимости от широты
и расстояния точки до центра карты. Это связано с особенностью карты и координатами на ней.
