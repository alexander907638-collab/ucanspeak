export function priceFormat(price: number ): string {
    return new Intl.NumberFormat('ru-RU', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(price);
}

export function priceFixed(price: string ): string {
    return parseFloat(price).toFixed(2)
}

