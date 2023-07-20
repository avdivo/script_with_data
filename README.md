# Script with data справка

(полная справка в файле SWD справка.pdf)

## Описание программы

Программа "Script with data" представляет собой инструмент для выполнения скриптов с подстановкой данных. Она разработана для записи и воспроизведения действий пользователя на компьютере, таких как перемещение мыши, клики мышью и нажатия клавиш клавиатуры.

Все действия пользователя записываются в виде команд для программы и могут быть отредактированы пользователем. Затем эти действия могут быть воспроизведены, позволяя компьютеру повторить все действия пользователя. Таким образом, программа позволяет автоматизировать выполнение рутинных задач, освобождая человека от их выполнения. Некоторые примеры использования включают отправку электронных писем, тестирование программ и другие подобные задачи.

## Состав программы

Программа состоит из 3 компонентов:

1. Редактор скриптов - отдельное окно, с помощью которого можно записать действия пользователя и преобразовать их в список команд (скрипт). Скрипт может быть набран в ручном режиме, дополнен вспомогательными командами и настроен в соответствии с требованиями пользователя.
1. Менеджер проектов - окно, в котором отображаются проекты из рабочей папки. Тут проектам присваиваются и переназначаются пользователем уникальные (в рамках рабочей папки) коды для запуска. Создаются штрих-коды и ярлыки на рабочем столе для быстрого запуска.
1. Окно быстрого запуска. Служит для запуска скрипта из рабочей папки по коду или посредством сканера штрих-кодов.

## Отличительные возможности программы

Script with data является мощным инструментом автоматизации рутинных задач на компьютере. В этом разделе мы рассмотрим отличительные функциональные возможности данной программы. Среди них:

* Запись и сверка пиксельных изображений: возможность записи изображений участков интерфейса приложений или веб-страниц позволяет программе решать проблему изменения внешнего вида интерфейса. Сверка изображений во время воспроизведения позволяет реагировать на изменения интерфейса для принятия решений о выполнении действий.
* Реакция на ошибки: программа обладает возможностью автоматического принятия решения на основе возникших ошибок.
* Вставка текстов в поля приложений или веб-страниц: данные для вставки могут быть заранее записаны в скрипт или взяты из табличных файлов.&nbsp;
* Организация циклов: возможность организации циклов команд на основе нужного количества повторений или перебора записей файла.
* Переход по меткам: программа поддерживает возможность перехода по меткам, что улучшает управление скриптом.
* Организация подпрограмм: участок скрипта, который можно выполнить из разных частей программы.
* Гибкое редактирование команд кликов мыши: программа предоставляет гибкий механизм редактирования команд кликов мышки, что позволяет избегать ошибок при выполнении скрипта.
* Сокращение некоторых комбинаций клавиш в отдельные команды: программа позволяет сократить некоторые комбинации клавиш в отдельные команды для более эффективного управления.
* Работа с буфером обмена: программа поддерживает возможность работы с буфером обмена через комбинации клавиш.

Набор скрипта в редакторе: возможность полностью набрать скрипт в редакторе или записать действия пользователя с последующим редактированием.

&nbsp;

&nbsp;

&nbsp;

## Доработки

&#49;. Поработать над алгоритмом распознавания картинок чтобы изменение яркости меньше влияло

&#50;. Проверить влияние порога чувствительности распознавания, можно вынести в настройки

&#51;. Добавить уменьшение размера значна (по периметру) с целью обрезки границ

&#52;. Объединение в одну команду Нажатия и Отпускания одной кнопки и таких операций в команду

&#53;. Изменить функцию сохранения ярлыка и его имя.

&#54;. При переходе в другие окна из редактора предложить сохранить проект


## Как сделать Installer

* Выполнить: pyinstaller --windowed --icon=icon/run.ico  main.py
* Из добавить в папку dist\swd: 
    * icon
    * DejaVuSansMono.ttf
* В проводнике Windows. В папке dist\swd выделить все файлы, в контекстном меню выбрать Добавить в архив (Winrar)
* Поставить галочку Создать SFX-архив. Нажать ОК. Получим swd.exe
* Открыть и скопировать содержимое файла Add\Для swf.txt в буфер обмена
* Открыть контекстное меню на dist\swd\swd.exe, выбрать Открыть в WinRAR
* Нажать кнопку Комментарий, вставить содержимое буфера обмена, нажать ОК, закрыть WinRAR
* swd.exe готов к использованию
