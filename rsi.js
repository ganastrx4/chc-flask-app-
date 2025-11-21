/**
* Calcula el Índice de Fuerza Relativa (RSI).
*
* @param {number[]} precios Un array de precios de cierre.
* @param {number} period El período para calcular el RSI (por defecto: 14).
* @returns {number} El valor del RSI.
*/
function rsi(precios, period = 14) {
if (precios.length < period) {
console.warn("No hay suficientes datos para calcular el RSI.");
return NaN;
}

let ganancias = [];
let perdidas = [];

for (let i = 1; i < precios.length; i++) {
let cambio = precios[i] - precios[i - 1];
if (cambio > 0) {
ganancias.push(cambio);
perdidas.push(0);
} else {
ganancias.push(0);
perdidas.push(Math.abs(cambio));
}
}

let avgGanancias = ganancias.slice(0, period).reduce((a, b) => a + b, 0) / period;
let avgPerdidas = perdidas.slice(0, period).reduce((a, b) => a + b, 0) / period;

for (let i = period; i < ganancias.length; i++) {
avgGanancias = (avgGanancias * (period - 1) + ganancias[i]) / period;
avgPerdidas = (avgPerdidas * (period - 1) + perdidas[i]) / period;
}

let rs = avgGanancias / avgPerdidas;
let rsi = 100 - (100 / (1 + rs));

return rsi;
}

// (Opcional) Exporta la función si estás usando módulos ES
// export { rsi };
