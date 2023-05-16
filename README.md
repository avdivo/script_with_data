Редактор и исполнитель скриптов с подстановкой данных

Программа предназначена для создания, редактирования и исполнения скриптов управляющих компьютером 
через графический интерфейс пользователя. Позволяет автоматизировать заполнение различных форм 
и выполнение других рутинных операций. 


Формат данных

Скрипт - это папка с именем script, внутри которой файл script, без расширения, в текстовом формате. 
Он хранит настройки и команды скрипта. Формат файла описан в файле data_description.txt.
В папке также хранятся изображения элементов интерфейса (значки, иконки, кнопки) нужные для выпонения
скрипта. 
При сохранении скрипта папка упаковывается в ZIP архив с расширением .script. А при открытии в редакторе 
сохраняется в папке программы в распакованном виде.

Данные для подстановки в формы хранятся в Excel таблице, каждое поле в ней представляет собой 
отдельный список данных, которые последовательно вставляются в указанных полях на экране. Файл с данными 
должен находиться в одной папке с папкой script при выполнении скрипта. 
Соответственно когда пользователь указывает на файл с данными он копируется в папку с программой и 
удаляется после окончания работы со скриптом.


Записываемые и воспроизводимые действия

Для мыши: 
- клик в указанных координатах;
- двойной клик в указанных координатах;
- клик правой клавишей в указанных координатах.

Для клавиатуры:
- нажатие клавиши;
- отпускание клавиши.


Общие настройки скрипта

Часть из них можно менять командами в скрипте:
- пауза между нажатием клавиш клавиатуры (после отпускания)
- пауза после клика мыши
- пауза между командами
- убеждаться, что нужный элемент (кнопка, иконка ...) присутствует в заданных координатах
- сколько раз следует повторить паузу в 1 секунду между поисками элемента, прежде чем искать по всему экрану
- производить поиск элемента на всем экране, если в нужных координатах он не найден или проверка отключена
- действие, если элемент не найден: остановить/игнорировать/выполнить блок или перейти к якорю с указанным именем
- действие, если нет данных: остановить/игнорировать/выполнить блок или перейти к якорю с указанным именем


Дополнения и возможности скрипта

- Команды скрипта копируются, перемещаются, удаляются и редактируются вручную. 
- Команды добавляются в любом месте вручную.
- После любого действия можно добавить паузу в секундах.
- В любом месте можно применить функцию вставки данных из указанного поля или просто текста
- Можно организовать циклическое выполнение части скрипта заданное количество раз 
  или выполнить ее для каждого элемента указанного поля таблицы с данными.
- Можно выделить не выполняемый в обычной последовательности блок скрипта, 
  выполнение которого вызывается в любой части скрипта или при некоторых ошибках.
- Из любого места можно совершить переход в любое место скрипта
- Реакция на ошибки может быть настроена в самом скрипте


Команды скрипта

Клик левой клавишей мыши
Клик правой клавишей мыши
Двойной клик мыши 
Нажать клавишу n (n - название клавиши)
Отпустить клавишу n (n - название клавиши)
Пауза n секунд (n - целое число)
Вывести текст 'text'
Вывести данные из 'field_name'
Следующий элемент поля 'field_name' ('Поле таблицы (столбец) представлено в виде списка данных. Эта команда '
                'переводит указатель чтения к следующему элементу списка')
Цикл по полю 'field_name' (Начало блока команд, которые повторятся столько раз, сколько строк в указанном поле. 
                Окончание блока - команда Конец цикла)
Цикл n раз (n - число) (Начало блока команд, которые повторятся указанное в команде количество раз. 
                Окончание блока - команда Конец блока)
Конец цикла (Конец блока команд повторяющихся столько раз, сколько указано в начале блока, начатого командой Цикл.)
Блок 'name' (Поименованный блок команд который не выполняется в обычном порядке. Он вызывается командой 
            Выполнить или Ошибка. Блок завершается командой Конец блока. После чего скрипт выполняется от команды 
            вызвавшей блок.)
Конец блока (Завершение списка команд относящихся к последнему (перед этой командой) объявленному блоку. 
            Начало блока - команда Блок 'name'.)
Метка 'name' (Метка в скрипте, куда может быть совершен переход командами Выполнить или Ошибка.)
Выполнить 'name' (Выполняет блок или совершает переход к метке с указанным именем.)
Ошибка 'Нет элемента' (Меняет текущую реакцию скрипта на возникновение ошибки: 
            остановить скрипт/игнорировать/выполнить блок или перейти к якорю с указанным именем)
Ошибка 'Нет данных' (Меняет текущую реакцию скрипта на возникновение ошибки: 
            остановить скрипт/игнорировать/выполнить блок или перейти к якорю с указанным именем)
Стоп (Остановить выполнение скрипта)


Ошибки

Во время выполнения скрипта могут возникать ошибки. Реакция на них определена в скрипте 
и может изменяться командами скрипта по ходу выполнения.

- 'no element' - перед кликом по координатам программа пытается найти указанный элемент 
  (кнопку, иконку ...) в нужном месте экрана, если это не удается, программа ожидает 1 секунду, после 
  чего повторяет попытку. После нескольких попыток (количество указывается в настройке скрипта) 
  производится попытка поиска по всему экрану. В случае неудачи генерируется это исключение. Описанное 
  поведение задается настройками скрипта и может быть другим.

- 'no data' - возникает, когда программе не удается получить доступ к данным для подстановки. 
  Если отсутствует файл с данными, в файле нет поля указанного в скрипте, кончились элементы в поле.


Интерфейс и редактирование

Выбор скрипта.
В меню Файл:
пункты Создать, Открыть, Сохранить, Сохранить как... при нажатии на которые открывается окно 
работы с файлом.
Имя текущего файла (скрипта) и текстовое описание можно посмотреть в Настройках скрипта.

Выбор источника данных.
В меню Файл:
пункт Источник данных открывает окно выбора файла, в котором можно указать файл в формате excel из полей которого
будут сформированы словари. Имя поля - это ключ словаря, данные в строках присваиваются этому ключу в виде списка.
В верхней части окна Источник данных: текстовое поле с именами полей.

Настройки.
Пункт меню, которая откроет диалоговое окно с настройками скрипта. 
Тут указано имя текущего файла (скрипта) и текстовое описание. Общие настройки скрипта, которые описаны выше.
Настройки подгружаются из файла скрипта при его выборе. Или устанавливаются по умолчанию для нового скрипта.

Список команд скрипта.
Пронумерованные от 0 строки содержащие команды скрипта, каждая команда в отдельной строке.
Первая строка (с номером 0) всегда пустая.
В списке можно выделить строку или несколько строк с зажатой клавишей Shift или Ctrl.
Выбор строк приводит к изменению содержимого Редактора команд.
Над выбранными строками можно выполнять некоторые действия (описанные ниже).

Запись и воспроизведение
Блок кнопок для записи и воспроизведения скрипта.
- Запись - при нажатии кнопки сворачивается окно программы, ключается пауза 3 секунды, после чего звуковой сигнал
           сообщает, что запись начата (остановка записи клавишами CTRL+ESC или кнопкой стоп). Новые команды 
           записываются начиная с позиции, следующей за последней выделенной в списке.
- Стоп - останавливает запись (активируется когда запись включена).
- Выполнить - выполняет скрипт с позиции первой выбранной в списке и до последней выбранной (включительно). Если 
              выбрана одна строка, то выполнение скрипта начинается с нее и до конца. Встречаемые в скрипте 
              команды конца цикла или блока игнорируются, если не было начала.
              Перед выполнением выдерживается пауза 3 секунды и звучит сигнал.

Редактор команд.
Представляет собой строку с выпадающим списком. В ней отображается команда выбранная в списке.
Поле для ввода комментария позволят ввести название действия, при его наличии в списке отображается не 
команда, а введенный комментарий.
Ниже параметры этой команды в отдельных полях. Для команд мыши отображается картинка с элементом (кнопкой, иконкой..).
Если в списке выбрано несколько строк, то в выпадающем списке будет пустая строка.
Если в списке выбрать другую команду - это не повлияет на содержимое списка, пока не будет нажата
нужная кнопка редактора.

Кнопки редактора.
- Сохранить - изменяет выбранную в списке команду на ту, что находится в редакторе.
- Вставить - вставляет команду из редактора в список, после текущей команды.


Редактор списка.
Включает несколько кнопок:
- Копировать - копирует одну или несколько выделенных строк из списка
- Вырезать - копирует и удаляет одну или несколько выделенных строк из списка
- Вставить - вставляет скопированные ранее строки за последней выделенной строкой
- Удалить - удаляет выделенные строки, удаление команд где используется изображение не удаляет его.

История
- Назад - откат состояния списка перед последней выполненной операцией
- Вперед - активируется после нажатия клавиши назад и повторяет отмененные операции


План исправлений и доработок
- Работа горячих клавиш в Windows не зависимо от раскладки клавиатуры
- Проблема с однотонными изображениями

- Сокращение команд за счет введения кодирования горячих клавиш в одну команду
- Добавление функции скриншота места под курсором
- Замена изображения элемента в командах мыши сделанным скриншотом
- Удаление изображения элемента в командах мыши (проверить работу команд без изображения)
- Добавление команды ожидания появления элемента на экране и выполнение действия в случае отсутствия