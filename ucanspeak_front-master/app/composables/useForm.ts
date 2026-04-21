import { reactive, ref } from "vue";
import { FetchError } from 'ofetch';

export default function useForm<
	TFormData extends Record<string, unknown>,
	TApiResult
>(config: {
	apiFn: (args: TFormData | FormData) => Promise<TApiResult>,
	formData: TFormData,
	onSuccess?: (args: TApiResult) => void,
	asFormData?: boolean
}) {

	const { apiFn, formData, onSuccess, asFormData = false } = config;

	const form = reactive(formData);
	const errors = ref<Record<keyof TFormData, string | undefined> | null | Record<string, string>>(null);
	const notice = ref<string | null>(null);
	const pending = ref(false);
	const success = ref(false);

	// Вспомогательная функция для форматирования даты в YYYY-MM-DD
	function formatDateToYYYYMMDD(date: Date): string {
		const year = date.getFullYear();
		const month = String(date.getMonth() + 1).padStart(2, '0');
		const day = String(date.getDate()).padStart(2, '0');
		return `${year}-${month}-${day}`;
	}

	function toFormData(obj: Record<string, unknown>): FormData {
		const fd = new FormData();
		console.log('creating form', obj);
		for (const [key, value] of Object.entries(obj)) {
			if (value === undefined || value === null) continue;

			// Массивы
			if (Array.isArray(value)) {
				value.forEach(item => {
					if (item === undefined || item === null) return;

					const arrayKey = key.endsWith('[]') ? key : key;

					if (item instanceof File || item instanceof Blob) {
						fd.append(arrayKey, item);
					} else if (typeof item === 'object') {
						// Для объектов с id - берем только id
						if (item && 'id' in item && item.id !== undefined && item.id !== null) {
							fd.append(arrayKey, String(item.id));
						}
						// Для других объектов - JSON
						else {
							fd.append(arrayKey, JSON.stringify(item));
						}
					} else {
						fd.append(arrayKey, String(item));
					}
				});
			}
			// Одиночные файлы
			else if (value instanceof File || value instanceof Blob) {
				fd.append(key, value);
			}
			// Одиночные даты
			else if (value instanceof Date) {
				fd.append(key, formatDateToYYYYMMDD(value));
			}
			// Одиночные объекты
			else if (typeof value === 'object' && !(value instanceof Date)) {
				// Для объектов с id - берем только id
				if (value && 'id' in value && value.id !== undefined && value.id !== null) {
					fd.append(key, String(value.id));
				}
				// Для других объектов - JSON
				else {
					fd.append(key, JSON.stringify(value));
				}
			}
			// Остальное
			else {
				fd.append(key, String(value));
			}
		}

		return fd;
	}


	async function send() {
		errors.value = null;
		notice.value = null;
		pending.value = true;
		success.value = false;
		console.log(form)
		try {
			const payload = asFormData ? toFormData(form) : form;
			console.log(payload)
			const res = await apiFn(payload as any);
			success.value = true;
			onSuccess?.(res);

		} catch (e) {
			if (e instanceof FetchError) {
				console.error(e.data);
				errors.value = e.data;
			} else {
				notice.value = 'Непредвиденная ошибка на сервере';
			}
		} finally {
			pending.value = false;
		}
	}

	return {
		form,
		errors,
		notice,
		send,
		pending,
		success,
	};
}

