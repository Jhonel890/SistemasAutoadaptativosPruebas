import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // Configuración ligera: 1 usuario por 10 segundos
  vus: 1,
  duration: '10s',
};

export default function () {
  // Intenta entrar a la tienda (Frontend)
  const res = http.get('http://localhost');
  
  // Verifica que la tienda respondió bien (Código 200 OK)
  check(res, { 'status was 200': (r) => r.status == 200 });
  
  sleep(1); // Espera 1 segundo antes de volver a entrar
}