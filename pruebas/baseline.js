import http from 'k6/http';
import { check, sleep } from 'k6';

// Configuración del escenario
export const options = {
  // Vamos a simular 10 usuarios simultáneos durante 30 segundos
  vus: 10,
  duration: '30s',
  
  // Umbrales para decir si la prueba pasó o falló (Criterios de aceptación)
  thresholds: {
    http_req_duration: ['p(95)<500'], // El 95% de las peticiones deben ser más rápidas de 500ms
  },
};

export default function () {
  // 1. El usuario entra a la página principal
  const res = http.get('http://localhost:8080');

  // 2. Verificamos que la tienda responda "200 OK" (que no haya error)
  check(res, {
    'status is 200': (r) => r.status === 200,
    'text verification': (r) => r.body.includes('Online Boutique'),
  });

  // 3. El usuario "piensa" un segundo antes de volver a cargar (para ser realistas)
  sleep(1);
}