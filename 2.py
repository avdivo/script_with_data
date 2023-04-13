class SaveLoad:
    """ Сохранение и чтение скрипта """
    editor = None  # Ссылка на объект класса Редактор (реализация паттерна Наблюдатель)

    @classmethod
    def load_script(cls):
        # открываем диалоговое окно для выбора файла
        file_path = fd.askopenfilename(initialdir=settings.path_to_script, title="Открыть скрипт",
                                               filetypes=(("Скрипт", "script"),("All files", "*.*")))

        try:
            with open(file_path, "r") as f:
                commands_dict = json.load(f)
            script = json.loads(commands_dict['script'])

            # При построении скрипта команды меток и названий блоков должны быть добавлены в первую очередь
            # Поэтому создаем сначала все команды, чтобы убедиться в правильности их записей
            commands = []  # Итоговый список объектов команд, готовый для добавления
            for cmd_dict in script:
                commands.append(CommandClasses.create_command(
                        *cmd_dict['val'], command=cmd_dict['cmd'], description=cmd_dict['des']))

            # Удаляем старый скрипт и записываем новый
            data.data_source.clear()
            data.obj_command.clear()
            data.pointer_command = 0

            # Добавляем команды с метками по очереди их нахождения в скрипте
            for cmd_dict in commands:
                # Создаем объект команды с метками по краткой записи
                if cmd_dict.__class__.__name__ == 'BlockCmd' or cmd_dict.__class__.__name__ == 'LabelCmd':
                    data.add_new_command(cmd_dict)

            # Добавляем остальные команды, вставляя их на свои места
            for i, cmd_dict in enumerate(script):
                # Добавляем остальные команды по краткой записи
                if cmd_dict.__class__.__name__ != 'BlockCmd' or cmd_dict.__class__.__name__ != 'LabelCmd':
                    data.pointer_command = i
                    data.add_new_command(cmd_dict)

        except:
            cls.editor.to_report('Ошибка чтения скрипта.')
            raise


    @classmethod
    def save_script(cls):
        # открываем диалоговое окно для выбора файла
        file_path = fd.asksaveasfilename(initialdir=settings.path_to_script, title="Сохранить скрипт",
                                               filetypes=(("Скрипт", "script"),))
        script = json.dumps([data.obj_command[label].command_to_dict() for label in data.queue_command], default=lambda o: o.__json__())
        sett = json.dumps(settings.get_dict_settings(), default=lambda o: o.__json__())
        # сохраняем в файл
        with open(file_path, "w") as f:
            json.dump({'script': script, 'settings': sett}, f)
