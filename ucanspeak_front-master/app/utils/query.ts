export function makeQuery(query:any){
    const queryString = new URLSearchParams(query).toString()
    return  `&${queryString}`
}

export function getQueryString(query: Record<string, any>){
    const sanitizedQuery = query || {};
    // Фильтрация параметров, чтобы включать только те, которые не равны null и undefined
    const filteredQuery = Object.fromEntries(
        Object.entries(sanitizedQuery).filter(([_, value]) => value !== null && value !== undefined)
    );
    // Создание строки запроса из отфильтрованных параметров
    const queryString = new URLSearchParams(filteredQuery).toString();
    return queryString ? `&${queryString}` : '';
}