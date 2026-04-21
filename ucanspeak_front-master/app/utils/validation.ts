// maybe ove to config, maybe i18n logic included etc

const validationMessages: Record<string, string> = {
	'is_null': 'Не может быть пустым',
	'wrong_credentials': 'Неправильный логин или пароль',
	'len': 'Введите от :0 до :1 символов',
	'not_unique': 'Такой вариант уже занят, нужен уникальный'
}

export function ruleToText(rule: string, args: Array<string | number> = []){
	if(rule in validationMessages){
		const template = validationMessages[rule];

    if(template){
      const message = template.replace(/:(\d)/g, function(_, index){
        return args[index] ? args[index].toString() : '';
      });

      return message;
    }

		return '';
	}
	else{
		return rule;
	}
}